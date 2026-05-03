import unittest

from charlie.agent import Agent
from charlie.toolsets.datetime_tools import register_datetime_tools


class DateTimeToolsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        charlie = Agent(
            model="test-model",
            base_url="http://127.0.0.1:1234/v1",
        )
        register_datetime_tools(charlie)
        self.get_current_datetime = charlie.tools.tools["get_current_datetime"]
        self.get_weekday = charlie.tools.tools["get_weekday"]
        self.convert_datetime_timezone = (
            charlie.tools.tools["convert_datetime_timezone"]
        )
        self.add_duration_to_datetime = (
            charlie.tools.tools["add_duration_to_datetime"]
        )
        self.calculate_datetime_difference = (
            charlie.tools.tools["calculate_datetime_difference"]
        )

    def test_get_current_datetime_returns_expected_metadata(self) -> None:
        result = self.get_current_datetime("UTC")
        self.assertEqual(result["timezone"], "UTC")
        self.assertIsInstance(result["unix_timestamp"], int)
        self.assertIn("+00:00", result["result"])

    def test_get_weekday(self) -> None:
        self.assertEqual(
            self.get_weekday("2026-05-03"),
            {"result": "Sunday"},
        )

    def test_convert_datetime_timezone_from_naive_input(self) -> None:
        self.assertEqual(
            self.convert_datetime_timezone(
                "2024-01-01T12:00:00",
                "Asia/Tokyo",
                "UTC",
            )["result"],
            "2024-01-01T21:00:00+09:00",
        )

    def test_add_duration_to_datetime(self) -> None:
        self.assertEqual(
            self.add_duration_to_datetime(
                "2024-01-01T12:30:00",
                days=1,
                hours=2,
                minutes=15,
                source_timezone="UTC",
            ),
            {"result": "2024-01-02T14:45:00+00:00"},
        )

    def test_calculate_datetime_difference(self) -> None:
        self.assertEqual(
            self.calculate_datetime_difference(
                "2024-01-01T00:00:00",
                "2024-01-02T01:01:01",
                "UTC",
            ),
            {
                "result": 90_061,
                "human_readable": "1 day, 1 hour, 1 minute, 1 second",
            },
        )

    def test_unknown_timezone_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.get_current_datetime("Mars/Olympus_Mons")


if __name__ == "__main__":
    unittest.main()
