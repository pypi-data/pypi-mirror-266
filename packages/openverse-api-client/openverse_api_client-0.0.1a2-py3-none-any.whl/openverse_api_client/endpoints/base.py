from typing_extensions import Iterable, TypeAlias
from abc import ABC


class NoParams:
    pass


class OpenverseAPIEndpoint(ABC):
    method: str
    endpoint: str
    content_type: str = "application/json"
    path_params: Iterable[str] = ()
    params: type | TypeAlias
    response: type | TypeAlias
