from typing import Any, List, Type, Union

from hcube.api.exceptions import ConfigurationError, ConsistencyError
from hcube.api.models.aggregation import Aggregation, AggregationOp, ArrayAgg, Count
from hcube.api.models.dimensions import Dimension
from hcube.api.models.filters import (
    ComparisonFilter,
    ComparisonType,
    EqualityFilter,
    Filter,
    FilterCombinator,
    IsNullFilter,
    ListFilter,
    NegativeListFilter,
    OverlapFilter,
    SubstringFilter,
    SubstringMultiValueFilter,
    Wrapper,
)
from hcube.api.models.group_filters import ComparisonGroupFilter, GroupFilter
from hcube.api.models.injections import Injection
from hcube.api.models.metrics import Metric
from hcube.api.models.ordering import OrderDirection, OrderSpec
from hcube.api.models.transforms import Transform


class CubeQuery:
    """
    Describes a cube query - i. e. filters, groups, aggregations and ordering
    """

    FILTER_SHORTHANDS = {
        "in": ListFilter,
        "isnull": IsNullFilter,
        "not_in": NegativeListFilter,
        "overlap": OverlapFilter,
    }

    def __init__(self, cube: Type["Cube"]):  # noqa - cannot import Cube - circular import
        self.cube = cube
        self.filters: List[Filter] = []
        self.aggregations: List[Aggregation] = []
        self.groups: List[Dimension] = []
        self.group_filters: List[GroupFilter] = []
        self.orderings: List[OrderSpec] = []
        self.transforms: List[Transform] = []
        self.limit = None
        self.injections: List[Injection] = []

    def filter(self, *fltrs: Filter, **named_filters: Any) -> "CubeQuery":
        for fltr in fltrs:
            if isinstance(fltr, FilterCombinator):
                self._check_combinator(fltr)
            elif isinstance(fltr, Wrapper):
                fltr = self._resolve_wrapper(fltr)
            else:
                fltr.dimension = self._resolve_dim(fltr.dimension)
            self.filters.append(fltr)
        for spec, value in named_filters.items():
            self.filters.append(self.resolve_shorthand(spec, value))
        return self

    def aggregate(self, *aggregations: Aggregation, **named_aggregs) -> "CubeQuery":
        self.aggregations.extend(aggregations)
        for name, aggreg in named_aggregs.items():
            aggreg.name = name
            self.aggregations.append(aggreg)
        for aggreg in self.aggregations:
            self._postprocess_aggregation(aggreg)
        return self

    def group_by(self, *dims: Union[str, Dimension]) -> "CubeQuery":
        for dim in dims:
            self.groups.append(self._resolve_dim(dim))
        return self

    def group_filter(self, *filters: GroupFilter, **named_filters: Any) -> "CubeQuery":
        for fltr in filters:
            self._postprocess_aggregation(fltr.agg)
            self.group_filters.append(fltr)
        for spec, value in named_filters.items():
            self.group_filters.append(self._resolve_group_filter_shorthand(spec, value))
        return self

    def order_by(self, *orders: Union[str, OrderSpec]) -> "CubeQuery":
        for order in orders:
            if not isinstance(order, OrderSpec):
                direction = OrderDirection.DESC if order.startswith("-") else OrderDirection.ASC
                oname = order.lstrip("-")
                try:
                    dim = self._resolve_dim(oname)
                except ConfigurationError:
                    dims = [agg for agg in self.aggregations if agg.name == oname]
                    if dims:
                        dim = dims[0]
                    else:
                        raise ConfigurationError(
                            f"Order by '{oname}' is not possible - it is neither dimension nor "
                            f"aggregation"
                        ) from None
                order = OrderSpec(dimension=dim, direction=direction)
            else:
                self._check_own_dimension(order.dimension)
            self.orderings.append(order)
        return self

    def possible_materialized_views(
        self,
    ) -> [Type["AggregatingMaterializedView"]]:  # noqa - circular import
        mat_views = [mv for mv in self.cube._materialized_views if not mv.projection]
        if not mat_views:
            return []
        # we only support Sum and Count aggregations in materialized views at present, so any other
        # aggregation makes use of materialized views impossible
        if not all(agg.op in (AggregationOp.SUM, AggregationOp.COUNT) for agg in self.aggregations):
            return []
        # let's check materialized views against the used dims and metrics
        used_dim_names = set()
        if self.groups:
            used_dim_names |= {group.name for group in self.groups}
            used_dim_names |= {fltr.dimension.name for fltr in self.filters}
            used_dim_names |= {order.dimension.name for order in self.orderings}
            used_dim_names |= {transform.dimension.name for transform in self.transforms}
            used_dim_names |= {
                agg.distinct.name
                for agg in self.aggregations
                if isinstance(agg, Count) and agg.distinct
            }
        else:
            # if there is no grouping, we will return all dimensions
            used_dim_names |= {dim.name for dim in self.cube._dimensions.values()}

        used_metrics = {agg.dim_or_metric.name for agg in self.aggregations if agg.dim_or_metric}
        if not self.groups:
            # if there are no groups, we return all metrics
            used_metrics = {metric.name for metric in self.cube._metrics.values()}
        out = []
        for mv in self.cube._materialized_views:
            mv_dim_names = {dim.name for dim in mv._dimensions.values()}
            mv_metric_names = {agg.dim_or_metric.name for agg in mv._aggregations}
            if used_dim_names.issubset(mv_dim_names) and used_metrics.issubset(mv_metric_names):
                out.append(mv)
        return out

    def transform(self, *transforms: Transform, **name_to_transform: Transform):
        for transform in transforms:
            self.transforms.append(transform)
        for name, transform in name_to_transform.items():
            transform.name = name
            self.transforms.append(transform)
        # translate dimension names if used
        for transform in self.transforms:
            transform.dimension = self._resolve_dim(transform.dimension)
        return self

    def inject_groups(self, injection: Injection):
        self.injections.append(injection)

    def resolve_shorthand(self, spec: str, value: Any) -> Filter:
        parts = spec.split("__")
        if len(parts) == 1:
            return EqualityFilter(dimension=self._resolve_dim(parts[0]), value=value)
        if len(parts) != 2:
            raise ValueError("filter spec must be in format `name`__`filter`")
        dim_name, shorthand = parts
        fltr_cls = self.FILTER_SHORTHANDS.get(shorthand)
        if fltr_cls:
            return fltr_cls(self._resolve_dim(dim_name), value)
        if shorthand in ("gt", "gte", "lt", "lte"):
            return ComparisonFilter(
                dimension=self._resolve_dim(dim_name),
                comparison=ComparisonType[shorthand.upper()],
                value=value,
            )
        if shorthand in ("contains", "icontains"):
            return SubstringFilter(
                dimension=self._resolve_dim(dim_name),
                value=value,
                case_sensitive=shorthand == "contains",
            )
        if shorthand in ("mcontains", "imcontains"):
            return SubstringMultiValueFilter(
                dimension=self._resolve_dim(dim_name),
                values=value,
                case_sensitive=shorthand == "mcontains",
            )
        raise ValueError(f"unsupported filter `{shorthand}`")

    def _resolve_group_filter_shorthand(self, spec: str, value: Any) -> GroupFilter:
        parts = spec.split("__")
        if len(parts) != 2:
            raise ValueError("filter spec must be in format `name`__`filter`")
        dim_name, shorthand = parts
        if shorthand in ("gt", "gte", "lt", "lte"):
            return ComparisonGroupFilter(
                agg=self._resolve_aggregation(dim_name),
                comparison=ComparisonType[shorthand.upper()],
                value=value,
            )
        raise ValueError(f"unsupported filter `{shorthand}`")

    def _resolve_dim(self, dim: Union[str, Dimension]) -> Union[Dimension, Transform]:
        if isinstance(dim, Dimension):
            return self._check_own_dimension(dim)
        else:
            for transform in self.transforms:
                if transform.name == dim:
                    return transform
            return self.cube.dimension_by_name(dim)

    def _resolve_dim_or_metric(
        self, dim_or_metric: Union[str, Metric, Dimension]
    ) -> Union[Metric, Dimension]:
        if isinstance(dim_or_metric, Metric):
            return self._check_own_metric(dim_or_metric)
        elif isinstance(dim_or_metric, Dimension):
            return self._resolve_dim(dim_or_metric)
        else:
            try:
                return self.cube.metric_by_name(dim_or_metric)
            except ConfigurationError:
                try:
                    return self.cube.dimension_by_name(dim_or_metric)
                except ConfigurationError:
                    raise ConfigurationError(
                        f"Unknown dimension or metric: {dim_or_metric}"
                    ) from None

    def _resolve_metric(self, metric: Union[str, Metric]) -> Metric:
        if isinstance(metric, Metric):
            return self._check_own_metric(metric)
        else:
            return self.cube.metric_by_name(metric)

    def _resolve_aggregation_filters(self, aggreg: Aggregation):
        new_filters = []
        for fltr in aggreg.filters:
            if isinstance(fltr, dict):
                for key, value in fltr.items():
                    new_filters.append(self.resolve_shorthand(key, value))
            else:
                new_filters.append(fltr)
        aggreg.filters = new_filters

    def _resolve_aggregation(self, name):
        for aggreg in self.aggregations:
            if aggreg.name == name:
                return aggreg
        raise ConfigurationError(f"Aggregation '{name}' is not defined")

    def _check_own_dimension(self, dim: Dimension) -> Dimension:
        if dim not in self.cube._dimensions.values():
            raise ConsistencyError(f'Dimension "{dim}" is not associated with cube: {self.cube}')
        return dim

    def _check_own_metric(self, metric: Metric) -> Metric:
        if metric not in self.cube._metrics.values():
            raise ConsistencyError(f'Metric "{metric}" is not associated with cube: {self.cube}')
        return metric

    def _check_combinator(self, combinator: FilterCombinator):
        new_filters = []
        for fltr in combinator.filters:
            if isinstance(fltr, FilterCombinator):
                self._check_combinator(fltr)
                new_filters.append(fltr)
            elif isinstance(fltr, Wrapper):
                new_filters.append(self._resolve_wrapper(fltr))
            else:
                fltr.dimension = self._resolve_dim(fltr.dimension)
                new_filters.append(fltr)
        combinator.filters = new_filters

    def _resolve_wrapper(self, wrapper: Wrapper) -> Filter:
        return self.resolve_shorthand(wrapper.key, wrapper.value)

    def _postprocess_aggregation(self, aggreg):
        if aggreg.filters:
            self._resolve_aggregation_filters(aggreg)
        if aggreg.dim_or_metric:
            # resolve the metric when it was given as a string
            aggreg.dim_or_metric = self._resolve_dim_or_metric(aggreg.dim_or_metric)
        elif isinstance(aggreg, (Count, ArrayAgg)) and aggreg.distinct:
            aggreg.distinct = self._resolve_dim(aggreg.distinct)
        else:
            if not aggreg.allow_metric_none:
                raise ConfigurationError(
                    f"Aggregation '{aggreg.__class__}' cannot have empty metric"
                )

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.start:
                raise ConfigurationError("Only slices from start are supported for now")
            self.limit = key.stop
            return self
        else:
            raise ConfigurationError(f"Unsupported slicing type: {key} ({type(key)})")
