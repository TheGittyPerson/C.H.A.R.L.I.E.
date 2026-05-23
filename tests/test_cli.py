import unittest
from types import ModuleType
from unittest.mock import patch


class _ImportConsole:
    pass


fake_rich = ModuleType("rich")
fake_rich_console = ModuleType("rich.console")
fake_rich_console.Console = _ImportConsole
fake_rich.console = fake_rich_console

with patch.dict("sys.modules", {
    "rich": fake_rich,
    "rich.console": fake_rich_console,
}):
    from charlie.cli import CLI


class _FakeStatus:
    def __enter__(self) -> "_FakeStatus":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class _FakeConsole:
    def __init__(self, inputs: list[str]) -> None:
        self._inputs = iter(inputs)
        self.outputs: list[str] = []

    def input(self, prompt: str = "") -> str:
        self.outputs.append(prompt)
        return next(self._inputs)

    def print(self, *args, **kwargs) -> None:
        self.outputs.append("".join(str(arg) for arg in args))

    def status(self, *args, **kwargs) -> _FakeStatus:
        return _FakeStatus()


class _FakeAgent:
    def __init__(self, responses: list[dict[str, object]]) -> None:
        self.responses = iter(responses)
        self.name = "C.H.A.R.L.I.E."
        self.received_messages: list[str] = []

    def chat(self, user_message: str) -> dict[str, object]:
        self.received_messages.append(user_message)
        return next(self.responses)


# noinspection PyTypeChecker
class CLITestCase(unittest.TestCase):
    def test_start_prints_token_cost_when_enabled(self) -> None:
        console = _FakeConsole(["hello", "exit"])
        agent = _FakeAgent([
            {"content": "ok", "reasoning": "", "token_cost": 42},
        ])

        cli = CLI(agent, console=console, show_token_cost=True)
        cli.start()

        self.assertEqual(agent.received_messages, ["hello"])
        self.assertTrue(
            any("Token cost:" in output and "42" in output
                for output in console.outputs)
        )
        self.assertTrue(any("Bye!" in output for output in console.outputs))

    def test_start_shows_dash_when_token_cost_missing(self) -> None:
        console = _FakeConsole(["hello", "exit"])
        agent = _FakeAgent([
            {"content": "ok", "reasoning": "", "token_cost": None},
        ])

        cli = CLI(agent, console=console, show_token_cost=True)
        cli.start()

        self.assertTrue(
            any("Token cost:" in output and "-" in output
                for output in console.outputs)
        )


if __name__ == "__main__":
    unittest.main()
