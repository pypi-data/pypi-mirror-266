from dataclasses import dataclass, field
from typing import Mapping, Optional, Tuple

import economic_complexity as ec
import pandas as pd
from tesseract_olap import DataRequest, DataRequestParams

from logiclayer_complexity.common import df_melt, df_pivot, series_compare


@dataclass
class RcaParameters:
    cube: str
    activity: str
    location: str
    measure: str
    cuts: Mapping[str, Tuple[str, ...]] = field(default_factory=dict)
    locale: Optional[str] = None
    parents: bool = False
    threshold: Mapping[str, Tuple[str, float]] = field(default_factory=dict)

    @property
    def activity_id(self):
        return self.activity + " ID"

    @property
    def location_id(self):
        return self.location + " ID"

    @property
    def column_name(self):
        return f"{self.measure} RCA"

    @property
    def request(self) -> DataRequest:
        params: DataRequestParams = {
            "drilldowns": (self.location, self.activity),
            "measures": (self.measure,),
            "cuts_include": {**self.cuts},
            "parents": self.parents,
        }

        if self.locale is not None:
            params["locale"] = self.locale

        return DataRequest.new(self.cube, params)

    def apply_threshold(self, df: "pd.DataFrame"):
        """Applies threshold ranges over the provided DataFrame in-place."""
        measure = self.measure

        for level, condition in self.threshold.items():
            column_id = f"{level} ID"
            # From data, group rows by `level` dimension and get the sum of `measure`
            measure_sum = df[[column_id, measure]].groupby(by=[column_id]).sum()
            # Apply threshold condition and get rows that comply
            sum_to_drop = measure_sum.loc[
                series_compare(measure_sum[measure], *condition)
            ]
            # Drop complying rows from summed dataframe (leaving non-complying only)
            measure_sum.drop(sum_to_drop.index, inplace=True)
            # Get indexes of non-complying rows
            data_to_drop = df.loc[df[column_id].isin(measure_sum.index)].index
            # ...and drop them from the original data
            df.drop(data_to_drop, inplace=True)

            del measure_sum, sum_to_drop, data_to_drop

    def pivot(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pivots the Tidy DataFrame to prepare for calculations."""
        location_id = self.location_id
        index = location_id if location_id in df.columns else self.location

        activity_id = self.activity_id
        columns = activity_id if activity_id in df.columns else self.activity

        # pivot the table and remove NAs
        tbl = pd.pivot_table(df, index=index, columns=columns, values=self.measure)
        tbl.dropna(axis=1, how="all", inplace=True)
        tbl.fillna(0, inplace=True)

        return tbl.astype(float)

    def _calculate(self, tbl: "pd.DataFrame") -> pd.Series:
        """Performs the RCA calculation."""
        df_rca = ec.rca(tbl)
        rca: pd.Series = df_rca.stack()  # type: ignore
        return rca.rename(self.column_name)

    def calculate(self, df: "pd.DataFrame"):
        """Execute RCA calculations."""
        # pivot the data to prepare for calculation
        pivot_tbl = self.pivot(df)
        columns = pivot_tbl.index.name, pivot_tbl.columns.name
        # calculate RCA values
        rca = self._calculate(pivot_tbl)
        # merge RCA values to input DataFrame
        return df.merge(rca.reset_index(), how="left", on=columns)


@dataclass
class RcaSubnationalParameters:
    subnat_params: RcaParameters
    global_params: RcaParameters
    rank: bool = field(default=False)
    sort_ascending: Optional[bool] = None

    def _calculate_subnat(self, df_subnat: pd.DataFrame, df_global: pd.DataFrame):
        params_global = self.global_params
        params_subnat = self.subnat_params

        # Prepare Subnational data
        params_subnat.apply_threshold(df_subnat)
        pv_subnat = df_pivot(
            df=df_subnat,
            index=params_subnat.location_id,
            column=params_subnat.activity_id,
            value=params_subnat.measure,
        )

        # Sum activities for each subnat location
        location_sum = pv_subnat.sum(axis=1)

        # Calculates numerator
        rca_numerator = pv_subnat.divide(location_sum, axis=0)

        # Prepare Global data
        params_global.apply_threshold(df_global)
        pv_global = df_pivot(
            df=df_global,
            index=params_global.location_id,
            column=params_global.activity_id,
            value=params_global.measure,
        )

        # Sum locations for each activity globally
        row_sums = pv_global.sum(axis=0)

        # Calculates denominator
        rca_denominator = row_sums / row_sums.sum()  # type: pd.Series

        # Calculates subnational RCA
        tbl_rca = rca_numerator / rca_denominator
        rca_subnat = df_melt(
            tbl_rca,
            index=params_subnat.location_id,
            value=f"{params_subnat.measure} RCA",
        )

        return rca_subnat, pv_global, tbl_rca

    def calculate(self, df_subnat: pd.DataFrame, df_global: pd.DataFrame):
        sort_ascending = self.sort_ascending
        params = self.subnat_params

        name = f"{params.measure} RCA"

        ds, _, _ = self._calculate_subnat(df_subnat, df_global)

        if sort_ascending is not None:
            ds.sort_values(by=name, ascending=sort_ascending, inplace=True)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = (
                ds[name].rank(ascending=False, method="max").astype(int)
            )

        # recover missing labels using InnerJoin against original subnat DF
        df_rca = ds.merge(
            df_subnat,
            on=[params.location_id, params.activity_id],
            how="inner",
        )

        return df_rca
