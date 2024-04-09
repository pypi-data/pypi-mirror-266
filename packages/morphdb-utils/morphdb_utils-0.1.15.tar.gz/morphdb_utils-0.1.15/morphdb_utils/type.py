from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, TypedDict, Optional, Literal, Union


class NullValue(Enum):
    NULL_VALUE = 0


class ListValue(TypedDict):
    values: List["Value"]


class Struct(TypedDict):
    fields: Dict[str, "Value"]


class Value(TypedDict):
    kind: Dict[str, Any]


class SqlResultRowResponse(TypedDict):
    value: Dict[str, Value]


@dataclass
class SqlResultResponse:
    headers: List[str]
    rows: List[SqlResultRowResponse]


@dataclass
class SignedUrlResponse:
    url: str


@dataclass
class RefResponse:
    cell_id: str
    cell_name: str
    code: str
    cell_type: str
    connection_type: Optional[str]
    connection_slug: Optional[str]


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