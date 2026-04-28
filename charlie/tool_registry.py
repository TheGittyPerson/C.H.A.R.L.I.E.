import inspect
import json
from dataclasses import dataclass, field
from typing import get_origin, get_args, Any, Annotated, Callable, Union, Final


@dataclass
class Tools:
    """Stores tools, builds their schemas, and runs tool calls by name."""

    TOOL_SCHEMA_ATTR: Final[str] = "__tool_schema__"
    tools: dict[str, Callable[..., Any]] = field(default_factory=dict)

    @staticmethod
    def _annotation_to_schema(annotation: Any) -> dict[str, Any]:
        """Convert a type annotation to a JSON schema fragment."""
        schema: dict[str, Any] = {"type": "string"}
        description: str | None = None
        origin = get_origin(annotation)

        if origin is Annotated:
            base_type, *meta = get_args(annotation)
            schema = Tools._annotation_to_schema(base_type)
            if meta:
                description = str(meta[0])
        elif annotation in (int, float):
            schema = {"type": "number"}
        elif annotation is bool:
            schema = {"type": "boolean"}
        elif annotation is str:
            schema = {"type": "string"}
        elif annotation is dict:
            schema = {"type": "object"}
        elif annotation is list:
            schema = {"type": "array"}
        elif origin is list:
            schema = {
                "type": "array",
                "items": Tools._annotation_to_schema(get_args(annotation)[0])
            }
        elif origin is dict:
            schema = {"type": "object"}
        elif origin is Union:
            any_of = [
                Tools._annotation_to_schema(arg)
                for arg in get_args(annotation)
                if arg is not type(None)
            ]
            if any_of:
                schema = any_of[0]

        if description:
            schema["description"] = description

        return schema

    @classmethod
    def schema_for_callable(cls, func: Callable[..., Any]) -> dict[str, Any]:
        """Build OpenAI tool schema dict for `func`."""
        sig = inspect.signature(func)
        annotations = inspect.get_annotations(func)

        parameters: dict[str, Any] = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

        for name, param in sig.parameters.items():
            annotation = annotations.get(name, inspect.Parameter.empty)

            if annotation is inspect.Parameter.empty:
                continue

            parameters["properties"][name] = cls._annotation_to_schema(
                annotation
            )

            if param.default is param.empty:
                parameters["required"].append(name)

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__ or "No description provided.",
                "parameters": parameters,
                "strict": True,
            },
        }

    def register(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Attach generated schema to `func` (if missing), register by name

        Return `func`.
        """
        if getattr(func, self.TOOL_SCHEMA_ATTR, None) is None:
            setattr(func, self.TOOL_SCHEMA_ATTR, self.schema_for_callable(func))
        self.tools[func.__name__] = func
        return func

    def get_schemas(self) -> list[dict[str, Any]]:
        """OpenAI-style tool definitions for the chat API."""
        out: list[dict[str, Any]] = []
        for fn in self.tools.values():
            s: dict[str, Any] | None = getattr(fn, self.TOOL_SCHEMA_ATTR, None)
            if s is not None:
                out.append(s)
        return out

    def execute(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        """Run a tool from a chat-completions `tool_calls` entry.

        (name + arguments JSON)
        """
        fn_payload: dict[str, str] = tool_call.get("function") or {}
        fn_name: str | None = fn_payload.get("name")
        fn = self.tools.get(fn_name) if fn_name else None

        if not fn:
            return {"error": f"Tool '{fn_name}' not found"}

        try:
            args = json.loads(fn_payload.get("arguments") or "{}")
            result = fn(**args)
            return result if isinstance(result, dict) else {"result": result}
        except KeyboardInterrupt:
            raise
        except Exception as e:
            return {"error": str(e)}
