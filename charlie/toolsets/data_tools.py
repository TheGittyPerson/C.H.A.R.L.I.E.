import csv
import io
import json
from typing import Annotated, Any

from ..agent import Agent


def register_data_tools(charlie: Agent) -> None:
    _register_json_tools(charlie)
    _register_csv_tools(charlie)


def _register_json_tools(charlie: Agent) -> None:
    @charlie.tool
    def validate_json(
        json_text: Annotated[str, "JSON text to validate"],
    ) -> dict[str, bool | str]:
        """Check whether a string contains valid JSON."""
        try:
            parsed = json.loads(json_text)
        except json.JSONDecodeError as exc:
            return {
                "valid": False,
                "error": (
                    f"{exc.msg} at line {exc.lineno}, column {exc.colno}"
                ),
            }

        return {
            "valid": True,
            "type": type(parsed).__name__,
        }

    @charlie.tool
    def format_json(
        json_text: Annotated[str, "JSON text to pretty-print"],
        indent: Annotated[int, "Number of spaces to indent nested levels"] = 2,
        sort_keys: Annotated[
            bool,
            "Whether to sort object keys alphabetically"
        ] = False,
    ) -> dict[str, str]:
        """Pretty-print JSON text with consistent indentation."""
        parsed = _load_json(json_text)
        safe_indent = max(0, indent)
        return {
            "result": json.dumps(
                parsed,
                indent=safe_indent,
                sort_keys=sort_keys,
            )
        }

    @charlie.tool
    def minify_json(
        json_text: Annotated[str, "JSON text to compress"],
    ) -> dict[str, str]:
        """Remove unnecessary whitespace from JSON text."""
        parsed = _load_json(json_text)
        return {
            "result": json.dumps(parsed, separators=(",", ":"))
        }

    @charlie.tool
    def extract_json_value(
        json_text: Annotated[str, "JSON text to query"],
        path: Annotated[
            str,
            "JSON path such as user.name, items[0], or user[\"full.name\"]",
        ] = "",
    ) -> dict[str, Any]:
        """Extract a value from JSON using dot-and-bracket path syntax."""
        parsed = _load_json(json_text)
        value = _resolve_json_path(parsed, path)
        return {"result": value}

    @charlie.tool
    def list_json_keys(
        json_text: Annotated[str, "JSON text to inspect"],
        path: Annotated[
            str,
            "Object path to inspect. Leave empty to inspect the root object.",
        ] = "",
    ) -> dict[str, list[str]]:
        """List the keys on a JSON object at a given path."""
        parsed = _load_json(json_text)
        value = _resolve_json_path(parsed, path)
        if not isinstance(value, dict):
            raise ValueError(
                "JSON value at the requested path is not an object"
            )
        return {"result": sorted(value.keys())}


def _register_csv_tools(charlie: Agent) -> None:
    @charlie.tool
    def csv_to_json_rows(
        csv_text: Annotated[str, "CSV text with a header row"],
        delimiter: Annotated[str, "Single-character field delimiter"] = ",",
    ) -> dict[str, Any]:
        """Convert CSV text with headers into JSON-style rows."""
        if len(delimiter) != 1:
            raise ValueError("Delimiter must be a single character.")

        reader = csv.DictReader(io.StringIO(csv_text), delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError("CSV input must include a header row.")

        rows = list(reader)
        return {
            "result": rows,
            "columns": reader.fieldnames,
            "row_count": len(rows),
        }


def _load_json(json_text: str) -> Any:
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}"
        ) from exc


def _resolve_json_path(value: Any, path: str) -> Any:
    tokens = _parse_json_path(path)
    current = value

    for token in tokens:
        if isinstance(token, int):
            if not isinstance(current, list):
                raise ValueError("Path index can only be used on JSON arrays.")
            try:
                current = current[token]
            except IndexError as exc:
                raise ValueError(
                    f"JSON array index out of range: {token}"
                ) from exc
            continue

        if not isinstance(current, dict):
            raise ValueError("Path key can only be used on JSON objects.")
        if token not in current:
            raise ValueError(f"JSON key not found: {token}")
        current = current[token]

    return current


def _parse_json_path(path: str) -> list[str | int]:
    stripped = path.strip()
    if stripped in {"", "$"}:
        return []
    if stripped.startswith("$"):
        stripped = stripped[1:]

    tokens: list[str | int] = []
    index = 0

    while index < len(stripped):
        char = stripped[index]

        if char == ".":
            index += 1
            continue

        if char == "[":
            end_index = stripped.find("]", index)
            if end_index == -1:
                raise ValueError("JSON path is missing a closing ']'.")

            segment = stripped[index + 1:end_index].strip()
            if not segment:
                raise ValueError(
                    "JSON path contains an empty bracket expression"
                )

            if segment[0] in {"'", '"'}:
                if len(segment) < 2 or segment[-1] != segment[0]:
                    raise ValueError(
                        "Quoted JSON path keys must close with the same quote"
                    )
                tokens.append(segment[1:-1])
            else:
                try:
                    tokens.append(int(segment))
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid JSON array index: {segment}"
                    ) from exc

            index = end_index + 1
            continue

        next_break = index
        while next_break < len(stripped) and stripped[next_break] not in ".[":
            next_break += 1

        token = stripped[index:next_break].strip()
        if not token:
            raise ValueError("JSON path contains an empty key segment.")
        tokens.append(token)
        index = next_break

    return tokens
