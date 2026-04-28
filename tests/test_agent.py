import unittest
from unittest.mock import patch

from charlie.agent import Agent


class _FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {
            "choices": [
                {
                    "message": {
                        "content": "ok",
                        "tool_calls": [],
                    }
                }
            ]
        }


class AgentRequestTestCase(unittest.TestCase):
    @patch("charlie.agent.requests.post")
    def test_chat_sends_temperature_when_configured(self, mock_post) -> None:
        mock_post.return_value = _FakeResponse()

        agent = Agent(temperature=0.7)
        agent.chat("Hello")

        request_json = mock_post.call_args.kwargs["json"]
        self.assertEqual(request_json["temperature"], 0.7)

    @patch("charlie.agent.requests.post")
    def test_chat_omits_temperature_when_not_configured(self, mock_post) -> None:
        mock_post.return_value = _FakeResponse()

        agent = Agent()
        agent.chat("Hello")

        request_json = mock_post.call_args.kwargs["json"]
        self.assertNotIn("temperature", request_json)


if __name__ == "__main__":
    unittest.main()
