from typing_extensions import TypedDict, Required, Literal, Type, TypeAlias
from decimal import Decimal

from openverse_api_client.endpoints.base import OpenverseAPIEndpoint


_MediaTypePlural = Literal["images", "audio"]
_MediaTypeSingular = Literal["image", "audio"]


class SourceStats(TypedDict, total=True):
    source_name: str
    display_name: str
    source_url: str
    media_count: int
    logo_url: str


def _GET_v1___stats(media_type: _MediaTypePlural):
    return type(
        f"GET_v1_{media_type}_stats",
        (OpenverseAPIEndpoint,),
        {
            "method": "GET",
            "endpoint": f"v1/{media_type}/stats/",
            "params": None,
            "response": list[SourceStats],
        },
    )


GET_v1_images_stats = _GET_v1___stats("images")
GET_v1_audio_stats = _GET_v1___stats("audio")


class _BaseSearchParams(TypedDict, total=False):
    page: int
    page_size: int
    source: str | list[str]
    excluded_source: str | list[str]
    license: str | list[str]
    license_type: str | list[str]
    tags: str | list[str]
    filter_dead: bool
    extension: str | list[str]
    include_sensitive_results: bool


class _ByQuerySearchParams(_BaseSearchParams):
    q: str


class _ByFieldSearchParams(_BaseSearchParams):
    creator: str
    title: str


class _ImageSearchParams(TypedDict, total=False):
    category: str | list[str]
    aspect_ratio: str | list[str]
    size: list[str]


class _ImageByQuerySearchParams(_ImageSearchParams, _ByQuerySearchParams): ...


class _ImageByFieldSearchParams(_ImageSearchParams, _ByFieldSearchParams): ...


class _AudioSearchParams(TypedDict, total=False):
    category: str | list[str]
    length: str | list[str]
    peaks: bool


class _AudioByQuerySearchParams(_AudioSearchParams, _ByQuerySearchParams): ...


class _AudioByFieldSearchParams(_AudioSearchParams, _ByFieldSearchParams): ...


class Tag(TypedDict, total=False):
    name: Required[str]
    accuracy: Decimal | None


class _MediaDetail(TypedDict, total=True):
    id: str
    title: str | None
    indexed_on: str
    foreign_landing_url: str | None
    url: str | None
    creator: str | None
    creator_url: str | None
    license: str
    license_version: str | None
    license_url: str | None
    provider: str | None
    source: str | None
    category: str | None
    filesize: str | None
    filetype: str | None
    tags: list[Tag] | None
    attribution: str
    fields_matched: list[str] | None
    mature: bool
    thumbnail: str
    detail_url: str
    related_url: str


class ImageDetail(_MediaDetail):
    height: int | None
    width: int | None


class _SearchResponse(TypedDict, total=True):
    result_count: int
    page_count: int
    page_size: int
    page: int


class GET_v1_images(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/images/"

    # Note: need to use overloads to type the client method kwargs
    params = Type[_ImageByQuerySearchParams] | Type[_ImageByFieldSearchParams]

    class response(_SearchResponse):
        results: list[ImageDetail]


class AudioSet(TypedDict, total=True):
    title: str | None
    foreign_landing_url: str | None
    creator: str | None
    creator_url: str | None
    url: str | None
    filesize: int | None
    filetype: int | None


class AudioDetail(_MediaDetail):
    audio_set: AudioSet | None
    duration: int | None
    bit_rate: int | None
    sample_rate: int | None
    waveform: str
    peaks: list[int] | None
    alt_files: dict | None
    genres: list[str] | None


class GET_v1_audio(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/audio/"

    params = Type[_AudioByQuerySearchParams] | Type[_AudioByFieldSearchParams]

    class response(_SearchResponse):
        results: list[AudioDetail]


class GET_v1_single_image(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/images/:identifier/"
    path_params = ("identifier",)

    class params(TypedDict, total=False):
        identifier: str

    response = Type[ImageDetail]


class GET_v1_single_audio(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/audio/:identifier/"
    path_params = ("identifier",)

    class params(TypedDict, total=False):
        identifier: str

    response = Type[AudioDetail]


class GET_v1_images_related(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/images/:identifier/related/"
    path_params = ("identifier",)

    class params(TypedDict, total=False):
        identifier: str

    response = Type[ImageDetail]


class GET_v1_audio_related(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/audio/:identifier/related/"
    path_params = ("identifier",)

    class params(TypedDict, total=False):
        identifier: str

    response = Type[AudioDetail]


class GET_v1_images_thumbnail(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/images/:identifier/thumb/"
    path_params = ("identifier",)

    class params(TypedDict, total=False):
        identifier: str
        full_size: bool
        compressed: bool

    response: TypeAlias = bytes


class GET_v1_audio_thumbnail(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/audio/:identifier/thumb/"
    path_params = ("identifier",)

    class params(TypedDict, total=False):
        identifier: str
        full_size: bool
        compressed: bool

    # class response(bytes):
    # pass
    response: TypeAlias = bytes


class GET_v1_audio_waveform(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/audio/:identifier/waveform/"
    path_params = ("identifier",)

    class params(TypedDict, total=False):
        identifier: str

    class response(TypedDict, total=True):
        len: int
        points: list[int]


class GET_v1_images_oembed(OpenverseAPIEndpoint):
    method = "GET"
    endpoint = "v1/images/oembed"

    class params(TypedDict, total=True):
        url: str

    class response(TypedDict, total=True):
        version: str
        type: str
        width: int
        height: int
        title: str | None
        author_name: str | None
        author_url: str | None
        license_url: str
