import pytest

import pook  # type: ignore[import-untyped]


pytestmark = [pytest.mark.pook]


def test_image_stats(base_url, sync_client, mock_token_req):
    mock_token_req(token="test-token")
    (
        pook.get(f"{base_url}/v1/images/stats/")
        .header("authorization", "Bearer test-token")
        .reply(200)
        .json([{"source_name": "flickr"}])
    )

    stats = sync_client.GET_v1_images_stats()

    assert stats.body == [{"source_name": "flickr"}]


def test_thumbnail(base_url, sync_client, mock_thumbnail, mock_token_req):
    mock_token_req(token="test-token")
    (
        pook.get(f"{base_url}/v1/images/")
        .header("authorization", "Bearer test-token")
        .param("q", "dogs")
        .reply(200)
        .json({"results": [{"id": "a-dog"}]})
    )

    (
        pook.get(f"{base_url}/v1/images/a-dog/thumb/")
        .header("authorization", "Bearer test-token")
        .reply(200)
        .body(mock_thumbnail, binary=True)
    )

    image_search = sync_client.GET_v1_images(q="dogs")

    assert image_search.body == {"results": [{"id": "a-dog"}]}
    image = image_search.body["results"][0]

    thumbnail = sync_client.GET_v1_images_thumbnail(identifier=image["id"])
    assert thumbnail.body == mock_thumbnail
