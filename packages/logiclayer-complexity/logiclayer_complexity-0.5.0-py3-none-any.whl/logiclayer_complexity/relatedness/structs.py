from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import economic_complexity as ec
import pandas as pd

if TYPE_CHECKING:
    from logiclayer_complexity.rca import RcaParameters, RcaSubnationalParameters


@dataclass
class RelatednessParameters:
    rca_params: "RcaParameters"
    cutoff: float = 1
    iterations: int = 20
    rank: bool = False
    sort_ascending: Optional[bool] = None

    @property
    def column_name(self):
        return f"{self.rca_params.measure} Relatedness"

    @property
    def request(self):
        return self.rca_params.request

    def _calculate(self, rca: pd.Series) -> pd.Series:
        df_rca = rca.unstack()
        df_relatd = ec.relatedness(df_rca, cutoff=self.cutoff)
        relatd: pd.Series = df_relatd.stack()  # type: ignore
        return relatd.rename(self.column_name)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        sort_ascending = self.sort_ascending
        name = self.column_name

        df_pivot = self.rca_params.pivot(df)
        columns = df_pivot.index.name, df_pivot.columns.name

        rca = self.rca_params._calculate(df_pivot)
        relatd = self._calculate(rca)

        ds = pd.concat([rca, relatd], axis=1).reset_index()

        if sort_ascending is not None:
            ds.sort_values(by=name, ascending=sort_ascending, inplace=True)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = (
                ds[name].rank(ascending=False, method="max").astype(int)
            )

        return df.merge(ds, how="left", on=columns)


@dataclass
class RelatednessSubnationalParameters:
    rca_params: "RcaSubnationalParameters"
    cutoff: float = 1
    rank: bool = False
    sort_ascending: Optional[bool] = None

    @property
    def column_name(self):
        return f"{self.rca_params.subnat_params.measure} Relatedness"

    def _calculate(self, df_subnat: pd.DataFrame, df_global: pd.DataFrame):
        name = self.column_name
        params = self.rca_params.subnat_params

        location_id = params.location_id
        activity_id = params.activity_id

        df, tbl_global, tbl_rca_subnat = self.rca_params._calculate_subnat(
            df_subnat, df_global
        )
        df_country = ec.rca(tbl_global)

        proximity = ec.proximity(df_country)
        output = ec.relatedness(
            tbl_rca_subnat.reindex(columns=list(proximity)).fillna(0),
            proximities=proximity,
        )
        output = pd.melt(output.reset_index(), id_vars=[location_id], value_name=name)
        output = output.merge(df, on=[location_id, activity_id], how="inner")

        return output

    def calculate(
        self,
        df_subnat: pd.DataFrame,
        df_global: pd.DataFrame,
    ) -> pd.DataFrame:
        name = self.column_name
        sort_ascending = self.sort_ascending
        params = self.rca_params.subnat_params

        location_id = params.location_id
        activity_id = params.activity_id

        ds = self._calculate(df_subnat, df_global)

        if sort_ascending is not None:
            ds.sort_values(by=name, ascending=sort_ascending, inplace=True)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = (
                ds[name].rank(ascending=False, method="max").astype(int)
            )

        df_relatedness = ds.merge(
            df_subnat[[activity_id, params.activity]].drop_duplicates(),
            on=activity_id,
            how="left",
        )
        df_relatedness = df_relatedness.merge(
            df_subnat[[location_id, params.location]].drop_duplicates(),
            on=location_id,
            how="left",
        )

        df_relatedness = df_relatedness.merge(
            df_subnat,
            on=[location_id, params.location, activity_id, params.activity],
            how="left",
        )
        df_relatedness[params.measure] = df_relatedness[params.measure].fillna(0)

        return df_relatedness
