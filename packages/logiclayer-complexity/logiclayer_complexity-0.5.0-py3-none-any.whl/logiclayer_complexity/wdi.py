from dataclasses import dataclass, field
from typing import Dict, List

from fastapi import HTTPException, Query
from tesseract_olap import DataRequest
from typing_extensions import Annotated, Required, TypedDict


@dataclass
class WdiParameters:
    year: List[int]
    indicator: str
    comparison: str
    value: int
    location: str


class WdiReferenceSchema(TypedDict, total=False):
    cube: Required[str]
    measure: str
    level_mapper: Dict[str, str]


@dataclass
class WdiReference:
    cube: str
    measure: str = field(default="Measure")
    level_mapper: Dict[str, str] = field(default_factory=dict)

    def build_request(self, params: WdiParameters):
        location = self.level_mapper.get(params.location, params.location)

        return DataRequest.new(
            self.cube,
            {
                "drilldowns": [location],
                "measures": [self.measure],
                "cuts_include": {
                    "Indicator": [params.indicator],
                    "Year": [str(item) for item in params.year],
                },
                "filters": {self.measure: ((params.comparison, params.value),)},
                "sorting": (self.measure, "desc"),
            },
        )

    def get_level(self, name: str):
        return self.level_mapper.get(name, name)


def parse_wdi(
    location: str,
    wdi: Annotated[
        List[str],
        Query(
            description="Applies an additional threshold over the data, using a parameter from the World Bank's WDI database."
        ),
    ] = [],
) -> List[WdiParameters]:
    """WDI dependency.

    Parses the parameters needed for the request done against the WDI cube.
    """

    def parse_singleton(param: str):
        tokens = param.split(":")
        if len(tokens) == 3:
            year, indicator, value = tokens
            comparison = "gte"
        elif len(tokens) == 4:
            year, indicator, comparison, value = tokens
        else:
            raise HTTPException(
                400, f"Malformed 'wdi' parameter, {len(tokens)} values were passed"
            )

        if not value.isnumeric():
            raise HTTPException(
                400, f"Malformed 'wdi' parameter, '{value}' must be numeric"
            )

        return WdiParameters(
            year=[int(item) for item in year.split(",")],
            indicator=indicator,
            comparison=comparison,
            value=int(value),
            location=location,
        )

    return [parse_singleton(param) for token in wdi for param in token.split(",")]
