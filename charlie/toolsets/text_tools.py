from typing import Annotated

from ..agent import Agent

PLAIN_TO_MORSE = {
    "a": ".-",     "b": "-...",   "c": "-.-.",   "d": "-..",
    "e": ".",      "f": "..-.",   "g": "--.",    "h": "....",
    "i": "..",     "j": ".---",   "k": "-.-",    "l": ".-..",
    "m": "--",     "n": "-.",     "o": "---",    "p": ".--.",
    "q": "--.-",   "r": ".-.",    "s": "...",    "t": "-",
    "u": "..-",    "v": "...-",   "w": ".--",    "x": "-..-",
    "y": "-.--",   "z": "--..",

    "1": ".----",  "2": "..---",  "3": "...--",  "4": "....-",
    "5": ".....",  "6": "-....",  "7": "--...",  "8": "---..",
    "9": "----.",  "0": "-----",

    ".": ".-.-.-", ",": "--..---", "?": "..--..", "'": ".----.",
    "!": "-.-.--", "/": "-..-.",   "(": "-.--.",  ")": "-.--.-",
    "&": ".-...",  ":": "---...",  ";": "-.-.-.", "=": "-...-",
    "+": ".-.-.",  "-": "-....-",  "_": "..--.-", '"': ".-..-.",
    "$": "...-..-", "@": ".--.-."
}

MORSE_TO_PLAIN = {value: key for key, value in PLAIN_TO_MORSE.items()}


def register_text_tools(charlie: Agent) -> None:
    _register_morse_tools(charlie)
    _register_basic_text_tools(charlie)


def _register_morse_tools(charlie: Agent) -> None:
    @charlie.tool
    def encode_morse(
            plain: Annotated[str, "Plain ASCII text"],
            space: Annotated[str, "What spaces will be replaced with"] = "/",
    ) -> dict[str, str]:
        """Encode plain text into Morse code.

        Letters are separated by a space. Inconvertible characters are replaces
        with "#".
        The given ``space`` parameter will be used to resolve spaces in the
        given plain text, padded with two extra spaces.
        e.g., "AB CD" with argument ``space="/"`` (the default)
          => ".- -... / -.-. -.."

        Case-insensitive.
        """
        out = []
        for char in plain.lower():
            if char == " ":
                out.append(f" {space} ")
            else:
                out.append(PLAIN_TO_MORSE.get(char, "#") + " ")

        return {"result": "".join(out).strip()}

    @charlie.tool
    def decode_morse(
            morse: Annotated[str, "Morse code"],
            space: Annotated[
                str, "What spaces are represented with in the given morse"
            ] = "/",
    ) -> dict[str, str]:
        """Decode Morse code into plain text.

        Letters should be separated by a space. Any invalid morse sequence
        will be replaced with "#".
        The given ``space`` argument will be used to resolve spaces in the
        given morse code. The string representing a space is assumed to be
        padded with an extra space on each side, meaning this is an example
        of the expected input when `space="/"` (the default):

        ".... . .-.. .-.. --- / .-- --- .-. .-.. -.." => "HELLO WORLD"

        Returns text in lowercase.
        """
        allowed_chars = {".", "-", " "} | set(space)
        if not all(char in allowed_chars for char in morse):
            raise ValueError(
                "Morse code must only contain '.' (periods/dots), '-' (dashes) "
                f"and/or '{space}'"
            )

        if not morse.strip():
            return {"result": ""}

        delimiter = f" {space} "
        words_decoded = []

        for word in morse.split(delimiter):
            letters = word.strip().split(" ")
            decoded_word = "".join(
                MORSE_TO_PLAIN.get(letter, "#") for letter in letters)
            words_decoded.append(decoded_word.lower())

        return {"result": " ".join(words_decoded)}


def _register_basic_text_tools(charlie: Agent) -> None:
    @charlie.tool
    def to_uppercase(
            text: Annotated[str, "Text to convert to uppercase"]
    ) -> dict[str, str]:
        """Convert text to uppercase."""
        return {"result": text.upper()}

    @charlie.tool
    def to_lowercase(
            text: Annotated[str, "Text to convert to lowercase"]
    ):
        """Convert text to lowercase."""
        return {"result": text.lower()}

    @charlie.tool
    def count_text_length(
            text: Annotated[str, "Text to measure"]
    ) -> dict[str, int]:
        """Count the number of characters in a text."""
        return {"result": len(text)}

    @charlie.tool
    def count_substring_instances(
            text: Annotated[str, "Text to search within"],
            substring: Annotated[str, "Substring to count"],
    ) -> dict[str, int] | dict[str, str]:
        """Count non-overlapping instances of a substring in a text."""
        if substring == "":
            return {"error": "Substring cannot be empty."}
        return {"result": text.count(substring)}

    @charlie.tool
    def reverse_text(
            text: Annotated[str, "Text to reverse"]
    ) -> dict[str, str]:
        """Reverse the characters in a text."""
        return {"result": text[::-1]}

    @charlie.tool
    def normalize_whitespace(
            text: Annotated[str, "Text with arbitrary whitespace"]
    ) -> dict[str, str]:
        """Collapse repeated whitespace and trim leading/trailing gaps."""
        return {"result": " ".join(text.split())}


def _register_cipher_tools(charlie: Agent) -> None:
    @charlie.tool
    def encode_caesar_cipher():
        ...
