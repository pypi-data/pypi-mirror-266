import inspect
from typing import TypedDict, get_args

from openverse_api_client import endpoints
from openverse_api_client._generate.base import template_env, is_bytes
from openverse_api_client.meta import empty


client_template = template_env.get_template("python/client.py.jinja")


def type_to_string(t) -> str:
    if isinstance(t, str):
        return f"'{str(t)}'"
    elif not hasattr(t, "__name__"):
        return str(t)

    if t.__name__ == "Literal":
        literals = ", ".join([type_to_string(a) for a in get_args(t)])
        return f"Literal[{literals}]"
    elif t.__name__ in ["Required", "Type"]:
        return type_to_string(get_args(t)[0])
    return t.__name__


PythonFiles = TypedDict("PythonFiles", {"async_client.py": str, "sync_client.py": str})


def generate_python() -> PythonFiles:
    methods = []

    for endpoint in endpoints.OpenverseAPIEndpoint.__subclasses__():
        signatures = []
        param_definitions = getattr(endpoint.params, "__args__", [endpoint.params])
        for param_def in param_definitions:
            parameters = []
            if param_def:
                if getattr(param_def, "__name__", None) == "Type":
                    param_def = get_args(param_def)[0]

                for name, annotation in inspect.get_annotations(param_def).items():
                    required = (
                        name in param_def.__required_keys__
                        or name in endpoint.path_params
                    )
                    param = {
                        "name": name,
                        "type": type_to_string(annotation),
                        "required": required,
                    }

                    default = getattr(param_def, name, empty)
                    if default != empty:
                        param["default"] = type_to_string(default)

                    parameters.append(param)

            parameters.sort(
                key=lambda x: 1 if "default" in x or not x["required"] else 0
            )

            signature = dict(
                parameters=parameters, return_annotation=endpoint.response.__name__
            )
            signatures.append(signature)

        methods.append(
            {
                "signatures": signatures,
                "overloaded": len(signatures) > 1,
                "endpoint": endpoint,
                "json_response": not is_bytes(endpoint.response),
            }
        )

    async_client = client_template.render(
        **{
            "methods": methods,
            "await": "await ",
            "a": "a",
            "def": "async def",
            "Async": "Async",
        }
    )

    sync_client = client_template.render(
        **{
            "methods": methods,
            "await": "",
            "a": "",
            "def": "def",
            "Async": "",
        }
    )

    return PythonFiles(
        **{
            "async_client.py": async_client,
            "sync_client.py": sync_client,
        }
    )
