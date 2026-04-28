from typing import Annotated

from ..agent import Agent


def register_math_tools(charlie: Agent) -> None:
    _register_arithmetic_tools(charlie)
    _register_base_conversion_tools(charlie)


def _register_arithmetic_tools(charlie: Agent) -> None:
    @charlie.tool
    def add(a: Annotated[int, "First number"],
            b: Annotated[int, "Second number"]) -> dict[str, int]:
        """Add two numbers together."""
        return {"result": a + b}

    @charlie.tool
    def multiply(a: Annotated[int, "First number"],
                 b: Annotated[int, "Second number"]) -> dict[str, int]:
        """Multiply two numbers together."""
        return {"result": a * b}

    @charlie.tool
    def subtract(a: Annotated[int, "First number"],
                 b: Annotated[int, "Second number"]) -> dict[str, int]:
        """Subtract the second number from the first."""
        return {"result": a - b}

    @charlie.tool
    def divide(
        a: Annotated[int, "Number to divide"],
        b: Annotated[int, "Number to divide by"]
    ) -> dict[str, float] | dict[str, str]:
        """Divide one number by another."""
        if b == 0:
            return {"error": "Cannot divide by zero."}
        return {"result": a / b}

    @charlie.tool
    def power(base: Annotated[int, "Base number"],
              exponent: Annotated[int, "Exponent"]) -> dict[str, int]:
        """Raise a number to a power."""
        return {"result": base ** exponent}

    @charlie.tool
    def modulo(
            a: Annotated[int, "First number"],
            b: Annotated[int, "Second number"],
    ) -> dict[str, int] | dict[str, str]:
        """Get the remainder after division."""
        if b == 0:
            return {"error": "Cannot divide by zero."}
        return {"result": a % b}


def _register_base_conversion_tools(charlie: Agent) -> None:
    @charlie.tool
    def encode_binary(
            plain: Annotated[str, "Plain ASCII text (spaces = '/')"]
    ) -> dict[str, str]:
        """Encode plain text into binary."""
        return {
            "result": ' '.join(format(ord(char), "08b") for char in plain)
        }

    @charlie.tool
    def decode_binary(
            binary: Annotated[str, "Binary bytes separated by spaces"]
    ) -> dict[str, str]:
        """Decode binary into plain text."""
        parts = binary.split()

        if not parts:
            return {"result": ""}

        if not all(set(part) <= {"0", "1"} for part in parts):
            raise ValueError("Binary must only contain 0, 1, and spaces.")

        return {"result": ''.join(chr(int(part, 2)) for part in parts)}

    @charlie.tool
    def encode_hexadecimal(
            plain: Annotated[str, "Plain text"]
    ) -> dict[str, str]:
        """Encode plain text into hexadecimal."""
        return {
            "result": ' '.join(format(ord(char), "02X") for char in plain)
        }

    @charlie.tool
    def decode_hexadecimal(
        hexadecimal: Annotated[str, "Hex bytes separated by spaces"],
    ) -> dict[str, str]:
        """Decode hexadecimal into plain text."""
        parts = hexadecimal.split()

        if not parts:
            return {"result": ""}

        valid_chars = set("0123456789abcdefABCDEF")
        if not all(set(part) <= valid_chars for part in parts):
            raise ValueError(
                "Hexadecimal must only contain 0-9, A-F, and spaces."
            )

        return {
            "result": ''.join(chr(int(part, 16)) for part in parts)
        }

    @charlie.tool
    def encode_octal(plain: Annotated[str, "Plain text"]) -> dict[str, str]:
        """Encode plain text into octal."""
        return {
            "result": ' '.join(format(ord(char), "03o") for char in plain)
        }

    @charlie.tool
    def decode_octal(
            octal: Annotated[str, "Octal bytes separated by spaces"]
    ) -> dict[str, str]:
        """Decode octal into plain text."""
        parts = octal.split()

        if not parts:
            return {"result": ""}

        if not all(set(part) <= set("01234567") for part in parts):
            raise ValueError("Octal must only contain digits 0-7 and spaces.")

        return {
            "result": ''.join(chr(int(part, 8)) for part in parts)
        }
