from dataclasses import dataclass
from typing import Generic, TypeVar

import httpx


Params = TypeVar("Params")
ResponseBody = TypeVar("ResponseBody")


@dataclass
class OpenverseAPIRequest(Generic[Params]):
    headers: httpx.Headers
    params: Params | None


@dataclass
class OpenverseAPIResponse(Generic[ResponseBody]):
    body: ResponseBody
    headers: httpx.Headers
    status_code: int
    request: OpenverseAPIRequest


class Empty:
    pass


empty = Empty()
