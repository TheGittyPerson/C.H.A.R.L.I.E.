import unittest

from charlie.agent import Agent
from charlie.toolsets.data_tools import register_data_tools


class JsonToolsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        charlie = Agent(
            model="test-model",
            base_url="http://127.0.0.1:1234/v1",
        )
        register_data_tools(charlie)
        self.validate_json = charlie.tools.tools["validate_json"]
        self.format_json = charlie.tools.tools["format_json"]
        self.minify_json = charlie.tools.tools["minify_json"]
        self.extract_json_value = charlie.tools.tools["extract_json_value"]
        self.list_json_keys = charlie.tools.tools["list_json_keys"]
        self.csv_to_json_rows = charlie.tools.tools["csv_to_json_rows"]

    def test_validate_json_accepts_valid_json(self) -> None:
        self.assertEqual(
            self.validate_json('{"name":"Charlie","active":true}'),
            {"valid": True, "type": "dict"},
        )

    def test_validate_json_reports_invalid_json(self) -> None:
        result = self.validate_json('{"name": }')
        self.assertEqual(result["valid"], False)
        self.assertIn("line 1, column 10", result["error"])

    def test_format_json(self) -> None:
        self.assertEqual(
            self.format_json('{"b":1,"a":2}', indent=2, sort_keys=True),
            {"result": '{\n  "a": 2,\n  "b": 1\n}'},
        )

    def test_minify_json(self) -> None:
        self.assertEqual(
            self.minify_json('{\n  "name": "Charlie",\n  "id": 7\n}'),
            {"result": '{"name":"Charlie","id":7}'},
        )

    def test_extract_json_value_supports_nested_paths(self) -> None:
        payload = (
            '{"users":[{"name":"Alice"}],"profile":{"full.name":"Charlie"}}'
        )
        self.assertEqual(
            self.extract_json_value(payload, 'users[0].name'),
            {"result": "Alice"},
        )
        self.assertEqual(
            self.extract_json_value(payload, 'profile["full.name"]'),
            {"result": "Charlie"},
        )

    def test_list_json_keys(self) -> None:
        self.assertEqual(
            self.list_json_keys(
                '{"user":{"name":"Charlie","role":"agent"}}', "user"
            ),
            {"result": ["name", "role"]},
        )

    def test_csv_to_json_rows(self) -> None:
        self.assertEqual(
            self.csv_to_json_rows("name,age\nAlice,30\nBob,28\n"),
            {
                "result": [
                    {"name": "Alice", "age": "30"},
                    {"name": "Bob", "age": "28"},
                ],
                "columns": ["name", "age"],
                "row_count": 2,
            },
        )

    def test_extract_json_value_rejects_missing_keys(self) -> None:
        with self.assertRaises(ValueError):
            self.extract_json_value('{"name":"Charlie"}', "profile.name")


if __name__ == "__main__":
    unittest.main()
