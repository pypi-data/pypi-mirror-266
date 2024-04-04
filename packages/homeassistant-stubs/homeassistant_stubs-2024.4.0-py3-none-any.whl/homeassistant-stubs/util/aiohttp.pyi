from .json import json_loads as json_loads
from _typeshed import Incomplete
from aiohttp import web as web
from aiohttp.typedefs import JSONDecoder as JSONDecoder
from multidict import MultiDict
from typing import Any

class MockStreamReader:
    _content: Incomplete
    def __init__(self, content: bytes) -> None: ...
    async def read(self, byte_count: int = -1) -> bytes: ...

class MockRequest:
    mock_source: str | None
    method: Incomplete
    url: Incomplete
    status: Incomplete
    headers: Incomplete
    query_string: Incomplete
    _content: Incomplete
    def __init__(self, content: bytes, mock_source: str, method: str = 'GET', status: int = ..., headers: dict[str, str] | None = None, query_string: str | None = None, url: str = '') -> None: ...
    @property
    def query(self) -> MultiDict[str]: ...
    @property
    def _text(self) -> str: ...
    @property
    def content(self) -> MockStreamReader: ...
    @property
    def body_exists(self) -> bool: ...
    async def json(self, loads: JSONDecoder = ...) -> Any: ...
    async def post(self) -> MultiDict[str]: ...
    async def text(self) -> str: ...

def serialize_response(response: web.Response) -> dict[str, Any]: ...
