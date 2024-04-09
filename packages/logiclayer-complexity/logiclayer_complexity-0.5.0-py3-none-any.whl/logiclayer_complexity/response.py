import os
import tempfile as tmp
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Union

import orjson
import pandas as pd
from fastapi import HTTPException, Response
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask


@dataclass
class ComplexityStatus:
    module: str
    version: str
    debug: Union[bool, dict]
    extras: dict


class ResponseFormat(str, Enum):
    csv = "csv"
    excel = "xlsx"
    jsonarrays = "jsonarrays"
    jsonrecords = "jsonrecords"
    parquet = "parquet"
    tsv = "tsv"

    def serialize(
        self,
        df: pd.DataFrame,
        aliases: Dict[str, str],
        filters: Dict[str, Tuple[str, ...]],
    ):
        # filter which members will be sent in the response
        for key, values in filters.items():
            column_id = f"{key} ID"
            dropping = df.loc[~df[column_id].isin(values)].index
            df.drop(dropping, inplace=True)
            del dropping

        # apply aliases requested by the user
        df.rename(columns=aliases, inplace=True)

        return data_response(df, self)


MIMETYPES = {
    ResponseFormat.csv: "text/csv",
    ResponseFormat.excel: "application/vnd.ms-excel",
    ResponseFormat.jsonarrays: "application/json",
    ResponseFormat.jsonrecords: "application/json",
    ResponseFormat.parquet: "application/vnd.apache.parquet",
    ResponseFormat.tsv: "text/tab-separated-values",
}


def data_response(
    df: pd.DataFrame,
    extension: ResponseFormat,
) -> Response:
    columns = tuple(df.columns)

    headers = {
        "X-Tesseract-Columns": ",".join(columns),
        "X-Tesseract-RowCount": str(len(df.index)),
    }

    with tmp.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp_file:
        if extension is ResponseFormat.csv:
            df.to_csv(tmp_file.name, sep=",", index=False)

        elif extension is ResponseFormat.excel:
            # df.write_excel(tmp_file.name)
            raise NotImplementedError

        elif extension is ResponseFormat.jsonarrays:
            res = df.to_dict("tight")
            target = {"columns": columns, "data": res["data"]}
            tmp_file.write(orjson.dumps(target))

        elif extension is ResponseFormat.jsonrecords:
            target = {"columns": columns, "data": df.to_dict("records")}
            tmp_file.write(orjson.dumps(target))

        elif extension is ResponseFormat.tsv:
            df.to_csv(tmp_file.name, sep="\t", index=False)

        elif extension is ResponseFormat.parquet:
            # df.write_parquet(tmp_file.name)
            raise NotImplementedError

        else:
            raise HTTPException(406, f"Requested format is not supported: {extension}")

    return FileResponse(
        tmp_file.name,
        headers=headers,
        media_type=MIMETYPES[extension],
        background=BackgroundTask(os.unlink, tmp_file.name),
    )
