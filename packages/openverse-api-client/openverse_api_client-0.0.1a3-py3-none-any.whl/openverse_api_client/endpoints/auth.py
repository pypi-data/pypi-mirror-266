from typing_extensions import TypedDict, Literal

from openverse_api_client.endpoints.base import OpenverseAPIEndpoint


class POST_v1_auth_tokens_register(OpenverseAPIEndpoint):
    method = "POST"
    endpoint = "v1/auth_tokens/register/"

    class params(TypedDict, total=True):
        name: str
        description: str
        email: str

    class response(TypedDict, total=True):
        name: str
        client_id: str
        client_secret: str


class POST_v1_auth_tokens_token(OpenverseAPIEndpoint):
    method = "POST"
    endpoint = "v1/auth_tokens/token/"
    content_type = "application/x-www-form-urlencoded"

    class params(TypedDict, total=True):
        grant_type: Literal["client_credentials"]
        client_id: str
        client_secret: str

    class response(TypedDict, total=True):
        access_token: str
        scope: str
        expires_in: int
        token_type: str


class GET_v1_rate_limit(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/rate_limit/"

    # Based entirely on bearer token
    class params(TypedDict):
        pass

    class response(TypedDict, total=True):
        requests_this_minute: int | None
        requests_today: int | None
        rate_limit_model: Literal["standard", "enhanced"]
        verified: bool
