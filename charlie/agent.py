import json
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

import requests

from .context_registry import Contexts
from .tool_registry import Tools


@dataclass
class Agent:
    """Stateful client for a local OpenAI-compatible chat endpoint."""

    model: str
    base_url: str = "http://127.0.0.1:1234/v1"
    api_endpoint: str = "/chat/completions"
    api_key: str = field(default="NO_API_KEY", repr=False)

    system_prompt: str = ""
    temperature: int | float | None = None
    repeat_penalty: int | float | None = None
    max_output_tokens: int | None = None
    reasoning: Literal["off", "low", "medium", "high", "on"] | None = None

    tools: Tools = field(default_factory=Tools)
    contexts: Contexts = field(default_factory=Contexts)
    messages: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize configuration values after initialization."""
        self.system_prompt = (
            f"Your name is C.H.A.R.L.I.E. (Cognitive Helper for Adaptive "
            f"Response and Logical Intelligent Execution). {self.system_prompt}"
        )
        self.base_url = self.base_url.rstrip("/")

    def tool(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to register a function as a tool on this agent."""
        return self.tools.register(func)

    def context(self, func: Callable[[], str]) -> Callable[[], str]:
        """Register a callable that can supply dynamic prompt context."""
        return self.contexts.register(func)

    def chat(self, user_message: str) -> str:
        """Send a message to the model and persist the conversation history."""
        self._append_user_message(user_message)
        prefix: list[dict[str, Any]] = self._build_prefix_messages()

        # Keep going until the model gives a final reply with no tool calls.
        while True:
            api_kwargs: dict[str, Any] = self._build_request_payload(prefix)

            response_data = self._post_chat_completion(api_kwargs)
            message = self._extract_message(response_data)
            tool_calls = self._append_assistant_message(message)

            if not tool_calls:
                return message.get("content") or ""

            self._handle_tool_calls(tool_calls)

    def _append_user_message(self, user_message: str) -> None:
        """Append the latest user message to the conversation history."""
        self.messages.append({"role": "user", "content": user_message})

    def _build_prefix_messages(self) -> list[dict[str, Any]]:
        """Build the system and context messages prepended to each request."""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": self.contexts.render()},
        ]

    def _build_request_payload(
            self, prefix: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Assemble the request payload sent to the chat-completions API."""
        api_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": prefix + self.messages,
        }
        if self.temperature is not None:
            api_kwargs["temperature"] = self.temperature
        if self.repeat_penalty is not None:
            api_kwargs["repeat_penalty"] = self.repeat_penalty
        if self.max_output_tokens is not None:
            api_kwargs["max_output_tokens"] = self.max_output_tokens
        if self.reasoning is not None:
            api_kwargs["reasoning"] = self.reasoning

        tool_schemas = self.tools.get_schemas()
        if tool_schemas:
            api_kwargs["tools"] = tool_schemas

        return api_kwargs

    def _post_chat_completion(
            self, api_kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Send a chat-completions request and return the decoded response."""
        url: str = f"{self.base_url}{self.api_endpoint}"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        r = requests.post(
            url,
            headers=headers,
            json=api_kwargs,
            timeout=300,
        )

        r.raise_for_status()

        return r.json()

    @staticmethod
    def _extract_message(response_data: dict[str, Any]) -> dict[str, Any]:
        """Validate response shape and return the first assistant message."""
        choices: list[dict[str, Any]] | None = response_data.get("choices")

        if not choices:
            raise RuntimeError("Model response missing choices")
        choices: list[dict[str, Any]]

        message = choices[0].get("message")
        if message is None:
            raise RuntimeError("Model response missing messages")
        message: dict[str, Any]
        return message

    def _append_assistant_message(
            self, message: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Store the assistant message and return any normalized tool calls."""
        tool_calls = message.get("tool_calls") or []

        normalized_tool_calls = [
            {
                "id": tc.get("id"),
                "type": tc.get("type"),
                "function": {
                    "name": (tc.get("function") or {}).get("name"),
                    "arguments": (tc.get("function") or {}).get(
                        "arguments"
                    ),
                },
            }
            for tc in tool_calls
        ]

        self.messages.append({
            "role": "assistant",
            "content": message.get("content"),
            "tool_calls": normalized_tool_calls,
        })

        return normalized_tool_calls

    def _handle_tool_calls(self, tool_calls: list[dict[str, Any]]) -> None:
        """Execute requested tools and append their results to history."""
        for tool_call in tool_calls:
            result = self.tools.execute(tool_call)
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id"),
                "content": json.dumps(result),
            })
