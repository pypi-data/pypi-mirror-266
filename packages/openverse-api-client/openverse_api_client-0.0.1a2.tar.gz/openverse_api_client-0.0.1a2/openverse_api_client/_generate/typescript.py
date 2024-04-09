import inspect
from typing_extensions import Set, TypedDict, get_args, _TypedDictMeta, is_typeddict  # type: ignore[attr-defined]
from types import UnionType, NoneType
from decimal import Decimal
from dataclasses import dataclass, asdict


from openverse_api_client import endpoints
from openverse_api_client._generate.base import template_env, is_bytes


TypeScriptFiles = TypedDict(
    "TypeScriptFiles",
    {
        "types.ts": str,
    },
)


@dataclass(unsafe_hash=True)
class TSProperty:
    name: str
    required: bool
    type: str


@dataclass
class TSObjectMeta:
    interface_name: str
    properties: list[TSProperty]

    def __hash__(self) -> int:
        return f"{self.interface_name}; {','.join((str(p) for p in self.properties))}".__hash__()


interface_template = template_env.get_template("typescript/helpers/interface.ts.jinja")
types_template = template_env.get_template("typescript/types.ts.jinja")


def map_typed_dict_to_ts_object_meta(
    endpoint: endpoints.OpenverseAPIEndpoint, d: _TypedDictMeta
) -> TSObjectMeta:
    """
    Map a Python TypedDict property.
    """

    properties = []
    for p_name, p_type in inspect.get_annotations(d).items():
        properties.append(
            TSProperty(
                name=p_name,
                required=p_name in d.__required_keys__
                or p_name in endpoint.path_params,
                type=map_python_type(endpoint, p_type),
            )
        )

    return TSObjectMeta(
        interface_name=d.__name__,
        properties=properties,
    )


interfaces: Set[TSObjectMeta] = set()


def map_python_type(endpoint: endpoints.OpenverseAPIEndpoint, t: type) -> str:
    """
    Map a Python type to the equivalent TypeScript type.
    """

    if t is None or t == NoneType:
        return "null"
    elif t is str:
        return "string"
    elif t is bool:
        return "boolean"
    elif t is bytes:
        return "ReadableStream"
    elif t is int or t is Decimal:
        return "number"
    elif isinstance(t, UnionType):
        return " | ".join((map_python_type(endpoint, a) for a in get_args(t)))
    elif is_typeddict(t):
        # Add to ambient interfaces
        interfaces.add(map_typed_dict_to_ts_object_meta(endpoint, t))
        return t.__name__
    elif hasattr(t, "__name__"):
        match t.__name__:
            case "Type":
                return map_python_type(endpoint, get_args(t)[0])
            case "Literal":
                # Literal accepts multiple arguments, rather than
                # a single union argument. In TS, that translates
                # to a union of "literals", e.g., `type Category = 'photo' | 'illustration'`
                args = []
                for arg in get_args(t):
                    if isinstance(arg, str):
                        args.append(f"'{arg}'")
                    else:
                        args.append(arg)
                return " | ".join(args)
            case "Required":
                return map_python_type(endpoint, get_args(t)[0])
            case "list" | "Iterable" | "Sequence":
                # Use `Array` instead of `[]` shorthand to avoid
                # complications with a Union as the argument
                return f"Array<{map_python_type(endpoint, get_args(t)[0])}>"
            case "tuple":
                tuple_args = ", ".join(
                    [map_python_type(endpoint, a) for a in get_args(t)]
                )
                return f"[{tuple_args}]"
            case "dict" | "Mapping":
                args = [map_python_type(endpoint, a) for a in get_args(t)]
                if not args:
                    return "Record<string, any>"
                if len(args) == 1:
                    args = [args[0], args[0]]
                return f"Record<{', '.join(args)}>"

    raise ValueError(f"Unsupported type {t}")


def render_types():
    global interfaces
    interfaces = set()
    requests = []

    for endpoint in endpoints.OpenverseAPIEndpoint.__subclasses__():
        request = {
            "name": f"{endpoint.method} {endpoint.endpoint}",
            "content_type": endpoint.content_type,
            "path_params": endpoint.path_params,
            "json_response": not is_bytes(endpoint.response),
        }
        if not endpoint.params:
            request["params"] = None
        elif isinstance(endpoint.params, UnionType):
            for arg in get_args(endpoint.params):
                obj_meta = map_typed_dict_to_ts_object_meta(endpoint, arg)
                interfaces.add(obj_meta)
            request["params"] = " | ".join(
                (a.__name__ for a in get_args(endpoint.params))
            )
        else:
            obj_meta = map_typed_dict_to_ts_object_meta(endpoint, endpoint.params)
            if obj_meta.interface_name != "params":
                interfaces.add(obj_meta)
                request["params"] = obj_meta.interface_name
            else:
                request["params"] = obj_meta.properties

        if isinstance(endpoint.response, _TypedDictMeta):
            obj_meta = map_typed_dict_to_ts_object_meta(endpoint, endpoint.response)
            if obj_meta.interface_name != "response":
                interfaces.add(obj_meta)
                request["response"] = obj_meta.interface_name
            else:
                request["response"] = obj_meta.properties
        else:
            request["response"] = map_python_type(endpoint, endpoint.response)

        requests.append(request)

    rendered_interfaces = [
        interface_template.render(**asdict(interface)) for interface in interfaces
    ]
    context = {
        "interfaces": rendered_interfaces,
        "requests": requests,
    }

    return types_template.render(**context)


def generate_typescript() -> TypeScriptFiles:
    return TypeScriptFiles(**{"types.ts": render_types()})
