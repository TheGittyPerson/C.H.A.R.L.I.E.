from dataclasses import dataclass, field

from rich.console import Console

from .agent import Agent


@dataclass
class CLI:
    charlie: Agent
    console: Console = field(default_factory=Console)

    show_reasoning: bool = False

    user_color: str = "green"
    agent_color: str = "blue"
    spinner_style: str = "aesthetic"

    thinking_message: str = "Thinking..."
    exit_keywords: list[str] = field(
        default_factory=lambda: ["bye", "quit", "exit"]
    )
    exit_message: str = "Bye!"

    def start(self) -> int:
        """Start the CLI for the agent."""
        while True:
            self.console.print(
                f"\n[bold][{self.user_color}]You:"
                f"[/{self.user_color}][/bold] ",
                end=""
            )
            user_input = self.console.input()

            if user_input.lower().strip() in self.exit_keywords:
                self.console.print(f"\n[dim]{self.exit_message}[/dim]")
                return 0

            with self.console.status(
                f"[dim]{self.thinking_message}[/dim]",
                spinner=self.spinner_style
            ):
                response = self.charlie.chat(user_input)
                content = response.get("content", "").strip()
                reasoning = response.get("reasoning", "").strip()

            if self.show_reasoning and reasoning:
                self.console.print(
                    f"\n[bold][{self.agent_color}]{self.charlie.name}:"
                    f"[/{self.agent_color}][/bold]"
                )
                self.console.print(
                    f"\n[dim]Reasoning: {reasoning}[/dim]",
                )
            else:
                self.console.print(
                    f"\n[{self.agent_color}]{self.charlie.name}:"
                    f"[/{self.agent_color}] {content}"
                )
