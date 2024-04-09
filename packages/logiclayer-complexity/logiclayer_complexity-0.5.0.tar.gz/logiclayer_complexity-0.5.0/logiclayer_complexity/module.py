"""Economic Complexity adapter for use in LogicLayer.

Contains a module to enable endpoints which return economic complexity
calculations, using a Tesseract OLAP server as data source.
"""

from typing import Dict, List, Mapping, Optional, Tuple

import logiclayer as ll
import pandas as pd
import polars as pl
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from tesseract_olap import DataRequest, OlapServer, PublicCube, PublicSchema
from tesseract_olap.backend import Session
from tesseract_olap.exceptions import QueryError, TesseractError
from typing_extensions import Annotated

from . import __title__, __version__
from .complexity import (
    ComplexityParameters,
    ComplexitySubnationalParameters,
    prepare_complexity_params,
    prepare_complexity_subnational_params,
)
from .dependencies import parse_alias, parse_filter
from .opportunity_gain import OpportunityGainParameters, prepare_opportunity_gain_params
from .pmi import (
    PEIIParameters,
    PGIParameters,
    prepare_peii_params,
    prepare_pgi_params,
)
from .rca import (
    RcaParameters,
    RcaSubnationalParameters,
    prepare_rca_params,
    prepare_subnatrca_params,
)
from .relatedness import (
    RelatednessParameters,
    RelatednessSubnationalParameters,
    prepare_relatedness_params,
    prepare_relatedness_subnational_params,
)
from .response import ComplexityStatus, ResponseFormat
from .wdi import WdiParameters, WdiReference, WdiReferenceSchema, parse_wdi


class EconomicComplexityModule(ll.LogicLayerModule):
    """Economic Complexity calculations module class for LogicLayer."""

    olap: "OlapServer"
    wdi: Optional["WdiReference"]

    def __init__(
        self,
        olap: "OlapServer",
        wdi: Optional["WdiReferenceSchema"] = None,
        **kwargs,
    ):
        """Setups the server for this instance."""
        super().__init__()

        if olap is None:
            raise ValueError(
                "EconomicComplexityModule requires a tesseract_olap.OlapServer instance"
            )

        self.debug = kwargs.get("debug", False)
        self.olap = olap
        self.wdi = None if wdi is None else WdiReference(**wdi)

    def apply_threshold(
        self,
        session: Session,
        df: pl.DataFrame,
        *,
        rca: RcaParameters,
        wdi: List[WdiParameters] = [],
    ) -> pd.DataFrame:
        threshold_expr = [
            *_yield_threshold_expr(df, rca.measure, rca.threshold),
            *self._yield_wdi_threshold_expr(session, wdi),
        ]
        if len(threshold_expr) > 0:
            df = df.filter(threshold_expr)
        return df.to_pandas()

    def _yield_wdi_threshold_expr(self, session: Session, params: List[WdiParameters]):
        if not self.wdi or len(params) == 0:
            return None

        for item in params:
            request = self.wdi.build_request(item)
            data = self.fetch_data(session, request)
            location = f"{self.wdi.get_level(item.location)} ID"
            yield pl.col(location).is_in(data[location])

    def fetch_data(self, session: Session, request: DataRequest):
        """Retrieves the data from the backend, and handles related errors."""
        query = self.olap.build_query(request)
        result = session.fetch_dataframe(query)
        return result.data

    @ll.route("GET", "/")
    def route_status(self) -> ComplexityStatus:
        return ComplexityStatus(
            module=__title__,
            version=__version__,
            debug=False,
            extras={
                "wdi": "disabled" if self.wdi is None else "enabled",
            },
        )

    @ll.route("GET", "/cubes")
    def route_schema(self, locale: Optional[str] = None) -> PublicSchema:
        roles = []
        locale = self.olap.schema.default_locale if locale is None else locale
        return PublicSchema.from_entity(self.olap.schema, locale=locale, roles=roles)

    @ll.route("GET", "/cubes/{cube_name}")
    def route_schema_cube(self, cube_name: str, locale: Optional[str] = None):
        roles = []
        cube = self.olap.schema.get_cube(cube_name)
        if not cube.is_authorized(roles):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "You don't have authorization to access this cube. "
                "Check your credentials and try again.",
            )
        locale = self.olap.schema.default_locale if locale is None else locale
        return PublicCube.from_entity(cube, locale=locale)

    @ll.route("GET", "/rca.{extension}")
    def route_rca(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RcaParameters = Depends(prepare_rca_params),
        wdi: List[WdiParameters] = Depends(parse_wdi),
    ):
        """RCA calculation endpoint."""
        with self.olap.session() as session:
            df = self.fetch_data(session, params.request)
            df = self.apply_threshold(session, df, rca=params, wdi=wdi)

        df_rca = params.calculate(df)

        return extension.serialize(df_rca, aliases, filters)

    @ll.route("GET", "/eci.{extension}")
    def route_eci(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: ComplexityParameters = Depends(prepare_complexity_params),
        wdi: List[WdiParameters] = Depends(parse_wdi),
    ):
        """ECI calculation endpoint."""
        with self.olap.session() as session:
            df = self.fetch_data(session, params.request)
            df = self.apply_threshold(session, df, rca=params.rca_params, wdi=wdi)

        df_eci = params.calculate(df, "ECI")

        return extension.serialize(df_eci, aliases, filters)

    @ll.route("GET", "/pci.{extension}")
    def route_pci(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: ComplexityParameters = Depends(prepare_complexity_params),
        wdi: List[WdiParameters] = Depends(parse_wdi),
    ):
        """PCI calculation endpoint."""
        with self.olap.session() as session:
            df = self.fetch_data(session, params.request)
            df = self.apply_threshold(session, df, rca=params.rca_params, wdi=wdi)

        df_pci = params.calculate(df, "PCI")

        return extension.serialize(df_pci, aliases, filters)

    @ll.route("GET", "/relatedness.{extension}")
    def route_relatedness(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RelatednessParameters = Depends(prepare_relatedness_params),
    ):
        """Relatedness calculation endpoint."""
        with self.olap.session() as session:
            df = self.fetch_data(session, params.request)
            df = self.apply_threshold(session, df, rca=params.rca_params)

        df_reltd = params.calculate(df)

        return extension.serialize(df_reltd, aliases, filters)

    @ll.route("GET", "/opportunity_gain.{extension}")
    def route_opportunity_gain(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: OpportunityGainParameters = Depends(prepare_opportunity_gain_params),
    ):
        """Opportunity Gain calculation endpoint."""
        with self.olap.session() as session:
            df = self.fetch_data(session, params.request)
            df = self.apply_threshold(session, df, rca=params.rca_params)

        df_opgain = params.calculate(df)

        return extension.serialize(df_opgain, aliases, filters)

    @ll.route("GET", "/pgi.{extension}")
    def route_pgi(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: PGIParameters = Depends(prepare_pgi_params),
    ):
        """PGI calculation endpoint."""
        with self.olap.session() as session:
            df = self.fetch_data(session, params.rca_params.request)
            df = self.apply_threshold(session, df, rca=params.rca_params)
            df_gini = self.fetch_data(session, params.request).to_pandas()

        df_pgi = params.calculate(df, df_gini)

        return extension.serialize(df_pgi, aliases, filters)

    @ll.route("GET", "/peii.{extension}")
    def route_peii(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: PEIIParameters = Depends(prepare_peii_params),
    ):
        """PEII calculation endpoint."""
        with self.olap.session() as session:
            df = self.fetch_data(session, params.rca_params.request)
            df = self.apply_threshold(session, df, rca=params.rca_params)
            df_emissions = self.fetch_data(session, params.request).to_pandas()

        df_peii = params.calculate(df, df_emissions)

        return extension.serialize(df_peii, aliases, filters)

    @ll.route("GET", "/rca_subnational.{extension}")
    def route_rca_subnational(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RcaSubnationalParameters = Depends(prepare_subnatrca_params),
    ):
        with self.olap.session() as session:
            df_subnat = self.fetch_data(
                session, params.subnat_params.request
            ).to_pandas()
            df_global = self.fetch_data(
                session, params.global_params.request
            ).to_pandas()

        df_rca = params.calculate(df_subnat, df_global)

        return extension.serialize(df_rca, aliases, filters)

    @ll.route("GET", "/eci_subnational.{extension}")
    def route_eci_subnational(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: ComplexitySubnationalParameters = Depends(
            prepare_complexity_subnational_params
        ),
    ):
        """ECI calculation endpoint."""
        with self.olap.session() as session:
            df_subnat = self.fetch_data(
                session, params.rca_params.subnat_params.request
            ).to_pandas()
            df_global = self.fetch_data(
                session, params.rca_params.global_params.request
            ).to_pandas()

        df_eci = params.calculate(df_subnat, df_global, "ECI")

        return extension.serialize(df_eci, aliases, filters)

    @ll.route("GET", "/pci_subnational.{extension}")
    def route_pci_subnational(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: ComplexitySubnationalParameters = Depends(
            prepare_complexity_subnational_params
        ),
    ):
        """PCI calculation endpoint."""
        with self.olap.session() as session:
            df_subnat = self.fetch_data(
                session, params.rca_params.subnat_params.request
            ).to_pandas()
            df_global = self.fetch_data(
                session, params.rca_params.global_params.request
            ).to_pandas()

        df_pci = params.calculate(df_subnat, df_global, "PCI")

        return extension.serialize(df_pci, aliases, filters)

    @ll.route("GET", "/relatedness_subnational.{extension}")
    def route_relatedness_subnational(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RelatednessSubnationalParameters = Depends(
            prepare_relatedness_subnational_params
        ),
    ):
        """Relatedness calculation endpoint."""
        with self.olap.session() as session:
            df_subnat = self.fetch_data(
                session, params.rca_params.subnat_params.request
            ).to_pandas()
            df_global = self.fetch_data(
                session, params.rca_params.global_params.request
            ).to_pandas()

        df_reltd = params.calculate(df_subnat, df_global)

        return extension.serialize(df_reltd, aliases, filters)

    @ll.route("GET", "/{endpoint}", response_class=RedirectResponse)
    def route_redirect(
        self,
        request: Request,
        endpoint: str,
        accept: Annotated[Optional[str], Header()] = None,
    ):
        if not any(path.startswith("/" + endpoint + ".") for path in self.route_paths):
            raise HTTPException(404, "Not found")

        if accept is None or accept.startswith("*/*") or "text/csv" in accept:
            extension = ResponseFormat.csv
        elif "application/x-jsonarray" in accept:
            extension = ResponseFormat.jsonarrays
        elif "application/x-jsonrecords" in accept:
            extension = ResponseFormat.jsonrecords
        elif "text/tab-separated-values" in accept:
            extension = ResponseFormat.tsv
        else:
            message = f"Requested invalid format: '{accept}'. Prefer an explicit format using a path with a filetype extension."
            raise HTTPException(status_code=406, detail=message)

        url = request.url
        path, endpoint = url.path.rsplit("/", maxsplit=1)
        return f"{path}/{endpoint}.{extension}?{url.query}"

    @ll.exception_handler(TesseractError)
    def exc_tesseracterror(self, request: Request, exc: TesseractError):
        if self.debug or isinstance(exc, QueryError):
            content = {"error": True, "type": type(exc).__name__, "detail": exc.message}
        else:
            content = {"error": True, "detail": "Backend error"}
        return JSONResponse(content, status_code=exc.code)


def condition_expr(measure: str, operator: str, value: float):
    if operator == "lt":
        return pl.col(measure) < value
    elif operator == "lte":
        return pl.col(measure) <= value
    elif operator == "gt":
        return pl.col(measure) > value
    elif operator == "gte":
        return pl.col(measure) >= value
    elif operator == "eq":
        return pl.col(measure) == value
    else:
        return pl.col(measure) != value


def _yield_threshold_expr(
    df: pl.DataFrame, measure: str, threshold: Mapping[str, Tuple[str, float]]
):
    for level, (operator, value) in threshold.items():
        column = f"{level} ID"
        # Group rows by `column` and get the sum of `measure`, then
        # apply threshold condition and get `column` of rows that comply
        keepids = (
            df.lazy()
            .select(column, measure)
            .group_by(column)
            .agg(pl.col(measure).sum())
            .filter(condition_expr(measure, operator, value))
            .select(column)
            .collect()
        )
        # Yield Expr for this threshold instruction
        yield pl.col(column).is_in(keepids[column])
