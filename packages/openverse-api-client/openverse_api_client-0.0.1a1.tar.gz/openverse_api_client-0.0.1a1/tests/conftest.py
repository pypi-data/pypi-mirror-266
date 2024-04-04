import pytest
import pook  # type: ignore[import-untyped]
from pathlib import Path

from openverse_api_client import AsyncOpenverseClient, OpenverseClient


mock_thumbnail_path = Path(__file__).parent / "mock-thumbnail.bin"


@pytest.fixture
def credentials() -> dict[str, str]:
    return {"client_id": "test-client-id", "client_secret": "test-client-secret"}


@pytest.fixture(scope="session")
def mock_thumbnail() -> bytes:
    return mock_thumbnail_path.read_bytes()


@pytest.fixture
def base_url() -> str:
    return "https://pook.local"


@pytest.fixture
def mock_token_req(base_url):
    def do(*, token: str | None = None, expiry: int | None = None):
        return (
            pook.post(f"{base_url}/v1/auth_tokens/token/")
            .reply(200)
            .json(
                {
                    "access_token": token or "test-token",
                    "scope": "test-scope",
                    "expires_in": expiry if expiry is not None else 10,
                    "token_type": "token",
                }
            )
            .mock
        )

    return do


@pytest.fixture
def async_client(base_url, credentials) -> AsyncOpenverseClient:
    return AsyncOpenverseClient(base_url=base_url, **credentials)


@pytest.fixture
def sync_client(base_url, credentials) -> OpenverseClient:
    return OpenverseClient(base_url=base_url, **credentials)
