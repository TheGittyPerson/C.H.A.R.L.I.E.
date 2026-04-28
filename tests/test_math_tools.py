import unittest

from charlie.agent import Agent
from charlie.toolsets.math_tools import register_math_tools


class BaseConversionToolsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        charlie = Agent()
        register_math_tools(charlie)
        self.encode_binary = charlie.tools.tools["encode_binary"]
        self.decode_binary = charlie.tools.tools["decode_binary"]
        self.encode_hexadecimal = charlie.tools.tools["encode_hexadecimal"]
        self.decode_hexadecimal = charlie.tools.tools["decode_hexadecimal"]
        self.encode_octal = charlie.tools.tools["encode_octal"]
        self.decode_octal = charlie.tools.tools["decode_octal"]

    def test_binary_round_trip(self) -> None:
        encoded = self.encode_binary("Hi")["result"]
        self.assertEqual(self.decode_binary(encoded), {"result": "Hi"})

    def test_hexadecimal_round_trip(self) -> None:
        encoded = self.encode_hexadecimal("Hi")["result"]
        self.assertEqual(self.decode_hexadecimal(encoded), {"result": "Hi"})

    def test_octal_round_trip(self) -> None:
        encoded = self.encode_octal("Hi")["result"]
        self.assertEqual(self.decode_octal(encoded), {"result": "Hi"})

    def test_decode_binary_rejects_invalid_characters(self) -> None:
        with self.assertRaises(ValueError):
            self.decode_binary("01000001 0100000X")

    def test_decode_hexadecimal_rejects_invalid_characters(self) -> None:
        with self.assertRaises(ValueError):
            self.decode_hexadecimal("41 4G")

    def test_decode_octal_rejects_invalid_characters(self) -> None:
        with self.assertRaises(ValueError):
            self.decode_octal("101 178")


if __name__ == "__main__":
    unittest.main()
