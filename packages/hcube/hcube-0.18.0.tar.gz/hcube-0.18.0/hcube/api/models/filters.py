from enum import Enum
from typing import Any, List, Union

from hcube.api.models.dimensions import ArrayDimension, Dimension
from hcube.api.models.transforms import Transform


class Filter:
    def __init__(self, dimension: Union[Dimension, str]):  # str will be resolved in query
        self.dimension = dimension


class EqualityFilter(Filter):
    def __init__(self, dimension: Union[Dimension, str], value: Union[str, int]):
        super().__init__(dimension)
        self.value = value


class ListFilter(Filter):
    def __init__(self, dimension: Union[Dimension, str], values: list):
        super().__init__(dimension)
        self.values = values


class NegativeListFilter(Filter):
    def __init__(self, dimension: Union[Dimension, str], values: list):
        super().__init__(dimension)
        self.values = values


class IsNullFilter(Filter):
    def __init__(self, dimension: Union[Dimension, str], is_null: bool):
        super().__init__(dimension)
        self.is_null = is_null


class ComparisonType(Enum):
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="


class ComparisonFilter(Filter):
    def __init__(self, dimension: Union[Dimension, str], comparison: ComparisonType, value: Any):
        super().__init__(dimension)
        self.comparison = comparison
        self.value = value


class SubstringFilter(Filter):
    def __init__(self, dimension: Union[Dimension, str], value: str, case_sensitive: bool = True):
        super().__init__(dimension)
        self.value = value
        self.case_sensitive = case_sensitive


class SubstringMultiValueFilter(Filter):
    """
    Represents matching a value against a list of values. If any value matches, the filter matches.
    """

    def __init__(
        self, dimension: Union[Dimension, str], values: [str], case_sensitive: bool = True
    ):
        super().__init__(dimension)
        self.values = list(values)
        self.case_sensitive = case_sensitive


class OverlapFilter(Filter):
    """
    Describes overlap between two arrays.
    """

    def __init__(self, dimension: Union[Dimension, str], values: list):
        if not isinstance(dimension, (ArrayDimension, Transform)):
            raise ValueError(
                "OverlapFilter can only be used with ArrayDimension or a Transform, "
                "'{}' given".format(dimension)
            )
        super().__init__(dimension)
        self.values = list(values)


class Wrapper:
    """
    This is helper class wrapping one filter shorthand. It is similar to Django Q objects,
    but only limited to one filter.
    """

    def __init__(self, **named_filters):
        if len(named_filters) > 1:
            raise ValueError("Wrapper can only wrap one filter")
        for key, value in named_filters.items():
            self.key = key
            self.value = value


class FilterCombinator:
    def __init__(self, *filters: Union[Filter, Wrapper]):
        self.filters: List[Filter] = list(filters)


class Or(FilterCombinator):
    pass
