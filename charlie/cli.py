import traceback
from dataclasses import dataclass, field

import requests  # For error handling
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

    def _maybe_show_traceback(self) -> None:
        """Optionally print the current traceback without crashing on input."""
        try:
            should_show = self.console.input(
                "\nSee full traceback? [y/n]: "
            ).lower().strip() == "y"
        except (EOFError, KeyboardInterrupt):
            return

        if should_show:
            self.console.print(f"\n{traceback.format_exc()}")

    def start(self) -> None:
        """Start the CLI for the agent. Return status."""
        try:
            while True:
                self.console.print(
                    f"\n[bold][{self.user_color}]You:"
                    f"[/{self.user_color}][/bold] ",
                    end=""
                )
                user_input = self.console.input()

                if user_input.lower().strip() in self.exit_keywords:
                    self.console.print(f"\n[dim]{self.exit_message}[/dim]")
                    return

                with self.console.status(
                    f"[dim]{self.thinking_message}[/dim]",
                    spinner=self.spinner_style
                ):
                    response = self.charlie.chat(user_input)
                    content = response.get("content", "").strip()
                    reasoning = response.get("reasoning", "").strip()

                self.console.print(
                    f"\n[bold][{self.agent_color}]{self.charlie.name}:"
                    f"[/{self.agent_color}][/bold]"
                )
                if self.show_reasoning and reasoning:
                    self.console.print(
                        f"\n[dim][bold]Reasoning:[/bold] {reasoning}[/dim]",
                    )
                self.console.print(f"\n{content}")

        except KeyboardInterrupt:
            self.console.print("\n[dim]Program stopped.[/dim]")
            return
        except EOFError:
            self.console.print("\n[dim]Input stream closed.[/dim]")
            return
        except requests.exceptions.Timeout:
            self.console.print(
                "\n[bold][red]Error:[/red][/bold] Request timed out."
                "\nThe server did not respond before the timeout expired."
            )
            self._maybe_show_traceback()
            return
        except requests.exceptions.ConnectionError:
            self.console.print(
                "\n[bold][red]Error:[/red][/bold] Server connection failed. "
                "\nIf you are using a remote server, please check your "
                "network connection and try again."
                "\nIf you are using a local server, ensure the server is "
                "running and you are connected to the correct port."
            )
        except requests.exceptions.HTTPError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None else "unknown"
            )
            reason = exc.response.reason if exc.response is not None else ""
            reason_text = f" ({reason})" if reason else ""
            self.console.print(
                "\n[bold][red]Error:[/red][/bold] "
                f"Server returned HTTP {status_code}{reason_text}."
            )
        except requests.exceptions.RequestException:
            self.console.print(
                "\n[bold][red]Error:[/red][/bold] Request to the server "
                "failed."
            )
        except (RuntimeError, ValueError, KeyError) as exc:
            self.console.print(
                "\n[bold][red]Error:[/red][/bold] "
                f"Application error: {exc}"
            )
        except Exception:
            self.console.print(
                f"\n[bold][red]Error:[/red][/bold] An unexpected error "
                "occurred."
            )

        self._maybe_show_traceback()
