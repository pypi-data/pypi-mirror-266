from __future__ import annotations

import io
import os
import urllib.parse
from morphdb_utils.type import RefResponse, SignedUrlResponse, SqlResultResponse

import pandas as pd
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from typing import Optional, Literal, Union, TypedDict

urllib3.disable_warnings(InsecureRequestWarning)


class MorphApiError(Exception):
    pass


class SheetCellParams(TypedDict):
    type: Literal['sheet']
    cell_name: str
    filename: Optional[str]
    timestamp: Optional[int]
    base_url: Optional[str]
    team_slug: Optional[str]
    authorization: Optional[str]
    notebook_id: Optional[str]

class SqlCellParams(TypedDict):
    type: Literal['sql']
    sql: str
    connection_slug: Optional[str]
    database_id: Optional[str]
    base_url: Optional[str]
    team_slug: Optional[str]
    authorization: Optional[str]
    notebook_id: Optional[str]


LoadDataParams = Union[RefResponse, SheetCellParams, SqlCellParams]


def _handle_morph_api_error(response: dict) -> Optional[dict[str, str]]:
    if "error" in response and "subCode" in response and "message" in response:
        raise MorphApiError(response["message"])


def _read_configuration_from_env() -> dict[str, str]:
    config = {}
    if "MORPH_DATABASE_ID" in os.environ:
        config["database_id"] = os.environ["MORPH_DATABASE_ID"]
    if "MORPH_BASE_URL" in os.environ:
        config["base_url"] = os.environ["MORPH_BASE_URL"]
    if "MORPH_TEAM_SLUG" in os.environ:
        config["team_slug"] = os.environ["MORPH_TEAM_SLUG"]
    if "MORPH_AUTHORIZATION" in os.environ:
        config["authorization"] = os.environ["MORPH_AUTHORIZATION"]
    if "MORPH_NOTEBOOK_ID" in os.environ:
        config["notebook_id"] = os.environ["MORPH_NOTEBOOK_ID"]

    return config


def _canonicalize_base_url(base_url: str) -> str:
    if base_url.startswith("http"):
        return base_url
    else:
        return f"https://{base_url}"


def _convert_sql_engine_response(
    response: SqlResultResponse,
) -> pd.DataFrame:
    fields = response.headers

    def parse_value(case_type, value):
        if case_type == "nullValue":
            return None
        elif case_type == "doubleValue":
            return value[case_type]
        elif case_type == "floatValue":
            return value[case_type]
        elif case_type == "int32Value":
            return value[case_type]
        elif case_type == "int64Value":
            return int(value[case_type])
        elif case_type == "uint32Value":
            return value[case_type]
        elif case_type == "uint64Value":
            return int(value[case_type])
        elif case_type == "sint32Value":
            return value[case_type]
        elif case_type == "sint64Value":
            return int(value[case_type])
        elif case_type == "fixed32Value":
            return value[case_type]
        elif case_type == "fixed64Value":
            return int(value[case_type])
        elif case_type == "sfixed32Value":
            return value[case_type]
        elif case_type == "sfixed64Value":
            return int(value[case_type])
        elif case_type == "boolValue":
            return value[case_type]
        elif case_type == "stringValue":
            return value[case_type]
        elif case_type == "bytesValue":
            return value[case_type]
        elif case_type == "structValue":
            return value[case_type]["fields"]
        elif case_type == "listValue":
            rows = []
            for v in value[case_type]["values"]:
                rows.append(parse_value(v["kind"]["$case"], v["kind"]))
            return rows

    parsed_rows = []
    for row in response.rows:
        parsed_row = {}
        for field in fields:
            value = row["value"][field]["kind"]
            case_type = value["$case"]
            parsed_row[field] = parse_value(case_type, value)
        parsed_rows.append(parsed_row)
    return pd.DataFrame.from_dict(parsed_rows)


def _convert_signed_url_response_to_dateframe(
    response: SignedUrlResponse,
) -> pd.DataFrame:
    ext = response.url.split(".")[-1].split("?")[0]
    r = requests.get(response.url)

    if ext == "csv":
        chunks = []
        for chunk in pd.read_csv(
            io.BytesIO(r.content),
            header=0,
            chunksize=1_000_000,
            encoding_errors="replace",
        ):
            chunks.append(chunk)
        df = pd.concat(chunks, axis=0)
    else:
        if ext.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(r.content), engine="xlrd", header=0, sheet_name=0)
        else:
            df = pd.read_excel(io.BytesIO(r.content), engine="openpyxl", header=0, sheet_name=0)
    return df


def _load_file_data_impl(
    cell_name: str,
    filename: str | None = None,
    timestamp: int | None = None,
    base_url: str | None = None,
    team_slug: str | None = None,
    authorization: str | None = None,
    notebook_id: str | None = None,
) -> pd.DataFrame:
    config_from_env = _read_configuration_from_env()
    if base_url is None:
        base_url = config_from_env["base_url"]
    if team_slug is None:
        team_slug = config_from_env["team_slug"]
    if authorization is None:
        authorization = config_from_env["authorization"]
    if notebook_id is None:
        notebook_id = config_from_env["notebook_id"]        

    headers = {
        "teamSlug": team_slug,
        "Authorization": authorization,
    }
    url_sql = urllib.parse.urljoin(
        _canonicalize_base_url(base_url),
        f"/canvas-file-history/{cell_name}/url/sign",
    )

    query_params = {}
    if notebook_id is not None:
        query_params["notebookId"] = notebook_id
    if filename is not None:
        query_params["filename"] = filename
    if timestamp is not None:
        query_params["timestamp"] = timestamp        
    url_sql += f"?{urllib.parse.urlencode(query_params)}"
    
    response = requests.get(url_sql, headers=headers)
    if response.status_code != 200:
        raise MorphApiError(response.text)
    response_body = response.json()
    _handle_morph_api_error(response_body)

    try:    
        structured_response_body = SignedUrlResponse(url=response_body["url"])
        df = _convert_signed_url_response_to_dateframe(structured_response_body)
        return df
    except Exception as e:
        raise MorphApiError(f"{e}")


def _execute_sql_impl(
    sql: str,
    connection_slug: str | None = None,
    database_id: str | None = None,
    base_url: str | None = None,
    team_slug: str | None = None,
    authorization: str | None = None,
    notebook_id: str | None = None,
) -> pd.DataFrame:
    config_from_env = _read_configuration_from_env()
    if database_id is None:
        database_id = config_from_env["database_id"]
    if base_url is None:
        base_url = config_from_env["base_url"]
    if team_slug is None:
        team_slug = config_from_env["team_slug"]
    if authorization is None:
        authorization = config_from_env["authorization"]
    if notebook_id is None:
        notebook_id = config_from_env["notebook_id"]

    headers = {
        "teamSlug": team_slug,
        "Authorization": authorization,
    }

    url_sql = urllib.parse.urljoin(
        _canonicalize_base_url(base_url),
        f"/{database_id}/sql/python",
    )

    request = {
        "sql": sql
    }
    if connection_slug is not None:
        request["connectionSlug"] = connection_slug

    response = requests.post(url_sql, headers=headers, json=request, verify=True)
    if response.status_code != 200:
        raise MorphApiError(response.text)
    response_body = response.json()
    _handle_morph_api_error(response_body)

    try:        
        structured_response_body = SqlResultResponse(
            headers=response_body["headers"], rows=response_body["rows"]
        )
        df = _convert_sql_engine_response(structured_response_body)
        return df
    except Exception as e:
        raise MorphApiError(f"{e}")



def ref(
    reference: str,
    base_url: str | None = None,
    team_slug: str | None = None,
    authorization: str | None = None,
    notebook_id: str | None = None
) -> RefResponse:
    config_from_env = _read_configuration_from_env()
    if base_url is None:
        base_url = config_from_env["base_url"]
    if team_slug is None:
        team_slug = config_from_env["team_slug"]
    if authorization is None:
        authorization = config_from_env["authorization"]
    if notebook_id is None:
        notebook_id = config_from_env["notebook_id"]

    headers = {
        "teamSlug": team_slug,
        "Authorization": authorization,
    }

    url_sql = urllib.parse.urljoin(
        _canonicalize_base_url(base_url),
        f"/canvas/{notebook_id}/cell-name/{reference}",
    )
    response = requests.get(url_sql, headers=headers, verify=True)
    if response.status_code != 200:
        raise MorphApiError(response.text)
    response_body = response.json()
    _handle_morph_api_error(response_body)
    
    structured_response_body = RefResponse(
        cell_id=response_body["cellId"],
        cell_name=response_body["cellName"],
        cell_type=response_body["cellType"],
        code=response_body["code"],
        connection_type=response_body["connectionType"],
        connection_slug=response_body["connectionSlug"],
    )
    
    return structured_response_body


def execute_sql(*args, **kwargs) -> pd.DataFrame:
    if args and isinstance(args[0], RefResponse):
        if args[0].cell_type != "sql":
            raise MorphApiError(f"Cell {args[0].cell_name} is not a SQL cell")
        ref_dict = {
            "sql": args[0].code,
            "connection_slug": args[0].connection_slug,
        }
        return _execute_sql_impl(**ref_dict, **kwargs)
    else:
        return _execute_sql_impl(*args, **kwargs)
    

def load_file_data(*args, **kwargs) -> pd.DataFrame:
    if args and isinstance(args[0], RefResponse):
        if args[0].cell_type != "readonlySheet":
            raise MorphApiError(f"Cell {args[0].cell_name} is not a Sheet cell")
        ref_dict = {
            "cell_name": args[0].cell_name,
        }
        return _load_file_data_impl(**ref_dict, **kwargs)
    else:
        return _load_file_data_impl(*args, **kwargs)
    

def load_data(*args: LoadDataParams, **kwargs) -> pd.DataFrame:
    if args and isinstance(args[0], RefResponse):
        if args[0].cell_type == "sql":
            ref_dict = {
                "sql": args[0].code,
                "connection_slug": args[0].connection_slug,
            }
            return _execute_sql_impl(**ref_dict, **kwargs)
        elif args[0].cell_type == "readonlySheet":
            ref_dict = {
                "cell_name": args[0].cell_name,
            }
            return _load_file_data_impl(**ref_dict, **kwargs)
        else:
            raise MorphApiError(f"Cell {args[0].cell_name} is not a valid cell type")
    elif "type" in args[0]:
        if args[0]["type"] == "sql":
            omitted_args = {k: v for k, v in args[0].items() if k != "type"}
            return _execute_sql_impl(**omitted_args, **kwargs)
        elif args[0]["type"] == "sheet":
            omitted_args = {k: v for k, v in args[0].items() if k != "type"}
            return _load_file_data_impl(**omitted_args, **kwargs)
        else:
            raise ValueError("Invalid data cell type provided.")
    else:
        raise ValueError("Invalid data cell type provided.")
