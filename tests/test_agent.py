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
    @staticmethod
    def _make_agent(**kwargs) -> Agent:
        return Agent(
            model="test-model",
            base_url="http://127.0.0.1:1234/v1",
            **kwargs,
        )

    @patch("charlie.agent.requests.post")
    def test_chat_sends_temperature_when_configured(self, mock_post) -> None:
        mock_post.return_value = _FakeResponse()

        agent = self._make_agent(temperature=0.7)
        agent.chat("Hello")

        request_json = mock_post.call_args.kwargs["json"]
        self.assertEqual(request_json["temperature"], 0.7)

    @patch("charlie.agent.requests.post")
    def test_chat_omits_temperature_when_not_configured(self, mock_post) -> None:
        mock_post.return_value = _FakeResponse()

        agent = self._make_agent()
        agent.chat("Hello")

        request_json = mock_post.call_args.kwargs["json"]
        self.assertNotIn("temperature", request_json)

    @patch("charlie.agent.requests.post")
    def test_chat_forwards_additional_request_kwargs(self, mock_post) -> None:
        mock_post.return_value = _FakeResponse()

        agent = self._make_agent()
        agent.add_request_kwargs(top_p=0.9, seed=7, stop=["END"])
        agent.chat("Hello")

        request_json = mock_post.call_args.kwargs["json"]
        self.assertEqual(request_json["top_p"], 0.9)
        self.assertEqual(request_json["seed"], 7)
        self.assertEqual(request_json["stop"], ["END"])

    @patch("charlie.agent.requests.post")
    def test_chat_omits_removed_request_kwargs(self, mock_post) -> None:
        mock_post.return_value = _FakeResponse()

        agent = self._make_agent()
        agent.add_request_kwargs(top_p=0.9, seed=7, stop=["END"])
        agent.remove_request_kwargs("seed", "stop", "missing_key")
        agent.chat("Hello")

        request_json = mock_post.call_args.kwargs["json"]
        self.assertEqual(request_json["top_p"], 0.9)
        self.assertNotIn("seed", request_json)
        self.assertNotIn("stop", request_json)


if __name__ == "__main__":
    unittest.main()
