import unittest

from charlie.agent import Agent
from charlie.toolsets.text_tools import register_text_tools


class MorseToolsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        charlie = Agent(
            model="test-model",
            base_url="http://127.0.0.1:1234/v1",
        )
        register_text_tools(charlie)
        self.encode_morse = charlie.tools.tools["encode_morse"]
        self.decode_morse = charlie.tools.tools["decode_morse"]

    def test_encode_morse_single_word(self) -> None:
        self.assertEqual(self.encode_morse("SOS"), {"result": "... --- ..."})

    def test_decode_morse_single_word(self) -> None:
        self.assertEqual(self.decode_morse("... --- ..."), {"result": "SOS"})

    def test_decode_morse_multiple_words(self) -> None:
        morse = ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
        self.assertEqual(
            self.decode_morse(morse),
            {"result": "HELLO WORLD"},
        )

    def test_round_trip_morse(self) -> None:
        plain = "HELLO WORLD"
        encoded = self.encode_morse(plain)["result"]
        self.assertEqual(self.decode_morse(encoded), {"result": plain})

    def test_decode_morse_rejects_invalid_characters(self) -> None:
        with self.assertRaises(ValueError):
            self.decode_morse("... --- ... x")

    def test_decode_morse_empty_string(self) -> None:
        self.assertEqual(self.decode_morse(""), {"result": ""})


class BasicTextToolsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        charlie = Agent(
            model="test-model",
            base_url="http://127.0.0.1:1234/v1",
        )
        register_text_tools(charlie)
        self.count_text_length = charlie.tools.tools["count_text_length"]
        self.count_substring_instances = (
            charlie.tools.tools["count_substring_instances"]
        )
        self.reverse_text = charlie.tools.tools["reverse_text"]
        self.normalize_whitespace = charlie.tools.tools["normalize_whitespace"]

    def test_count_text_length(self) -> None:
        self.assertEqual(
            self.count_text_length("Tony Stark"),
            {"result": 10},
        )

    def test_count_substring_instances(self) -> None:
        self.assertEqual(
            self.count_substring_instances("banana", "an"),
            {"result": 2},
        )

    def test_count_substring_instances_rejects_empty_substring(self) -> None:
        self.assertEqual(
            self.count_substring_instances("banana", ""),
            {"error": "Substring cannot be empty."},
        )

    def test_reverse_text(self) -> None:
        self.assertEqual(
            self.reverse_text("charlie"),
            {"result": "eilrahc"},
        )

    def test_normalize_whitespace(self) -> None:
        self.assertEqual(
            self.normalize_whitespace("  too\tmany\nspaces  here "),
            {"result": "too many spaces here"},
        )


if __name__ == "__main__":
    unittest.main()
