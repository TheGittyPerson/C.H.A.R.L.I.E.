from typing import Annotated

from ..agent import Agent

MORSE_TO_PLAIN = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F",
    "--.": "G", "....": "H", "..": "I", ".---": "J", "-.-": "K", ".-..": "L",
    "--": "M", "-.": "N", "---": "O", ".--.": "P", "--.-": "Q", ".-.": "R",
    "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6", "--...": "7",
    "---..": "8", "----.": "9", ".-.-.-": ".", "--..--": ",", "..--..": "?",
    ".----.": """, "-.-.--": "!", "-..-.": "/", "-.--.": "(", "-.--.-": ")",
    ".-...": "&", "---...": ":", "-.-.-.": ";", "-...-": "=", ".-.-.": "+",
    "-....-": "-", "..--.-": "_", ".-..-.": """, "...-..-": "$", ".--.-.": "@",
    "/": " ", "...---...": "SOS"
}
PLAIN_TO_MORSE = {value: key for key, value in MORSE_TO_PLAIN.items()}


def register_text_tools(charlie: Agent) -> None:
    _register_morse_tools(charlie)
    _register_basic_text_tools(charlie)


def _register_morse_tools(charlie: Agent) -> None:
    @charlie.tool
    def encode_morse(
            plain: Annotated[str, "Plain ASCII text"]
    ) -> dict[str, str]:
        """Encode plain text into Morse code.

        Letters are separated by a space.
        Words are separated by three spaces.
        Case-insensitive.
        """
        words = plain.upper().split(" / ")

        words_encoded = []
        for word in words:
            word_encoded = " ".join([PLAIN_TO_MORSE[char] for char in word])
            words_encoded.append(word_encoded)

        return {"result": " / ".join(words_encoded)}

    @charlie.tool
    def decode_morse(
            morse: Annotated[str, "Morse code (ASCII only, spaces = '/')"]
    ) -> dict[str, str]:
        """Decode Morse code into plain text.

        Letters should be separated by a space.
        Words should be separated by three spaces.
        Case-insensitive.
        """
        if not all(char in [".", "-", " ", "/"] for char in morse):
            raise ValueError(
                "Morse code must only contain '.' (periods/dots), '-' (dashes) "
                "and/or ' ' (spaces)"
            )

        if not morse.strip():
            return {"result": ""}

        words = morse.strip().split(" / ")

        words_decoded = []
        for word in words:
            letters = word.split()
            word_decoded = "".join(MORSE_TO_PLAIN[char] for char in letters)
            words_decoded.append(word_decoded)

        return {"result": " ".join(words_decoded)}


def _register_basic_text_tools(charlie: Agent) -> None:
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
