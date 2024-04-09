from jinja2 import Environment, PackageLoader, select_autoescape
from typing_extensions import get_args


template_env = Environment(
    loader=PackageLoader(
        "openverse_api_client",
        package_path="_templates",
    ),
    autoescape=select_autoescape(),
)


def is_bytes(t):
    if t is bytes:
        return True

    args = get_args(t)
    if not args:
        return False

    return args[0] is bytes
