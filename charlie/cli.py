import time
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
    show_token_cost: bool = False

    user_color: str = "green"
    agent_color: str = "blue"
    spinner: str = "aesthetic"

    thinking_message: str = "Thinking..."
    exit_keywords: list[str] = field(
        default_factory=lambda: ["bye", "quit", "exit"]
    )
    exit_message: str = "Bye!"

    def _maybe_show_traceback(self) -> None:
        """Optionally print the current traceback without crashing on input."""
        try:
            should_show = self.console.input(
                "\nSee full traceback? (y/n): "
            ).lower().strip() == "y"
        except (EOFError, KeyboardInterrupt):
            return

        if should_show:
            self.console.print(f"\n{traceback.format_exc()}")

    def start(self, retry_limit: int = 50, retry_delay: int = 500) -> None:
        """Start the CLI for the agent.

        Args:
            retry_limit (int):
                Number of times to retry initial connection before reporting an
                error.
            retry_delay (int):
                Delay in milliseconds between each retry attempt.
        """
        try:
            with self.console.status(
                    "[dim]Connecting...[/dim]",
                    spinner=self.spinner
            ):
                for _ in range(retry_limit):
                    if (result := self.charlie.test_connection()).success:
                        break
                    time.sleep(retry_delay / 1000)
                else:
                    self.console.print(
                        "\n[bold][red]Error:[/red][/bold] Connection "
                        "failed."
                        f"\n{result.error}"
                    )
                    return

            while (
                    user_input := self.console.input(  # I love this operator
                        f"\n[bold][{self.user_color}]"
                        f"You:[/{self.user_color}][/bold] "
                    )
            ) not in self.exit_keywords:
                if not user_input:
                    continue

                with self.console.status(
                    f"[dim]{self.thinking_message}[/dim]",
                    spinner=self.spinner
                ):
                    response = self.charlie.chat(user_input)
                    content = response.get("content", "").strip()
                    reasoning = response.get("reasoning", "").strip()
                    token_cost = response.get("token_cost") or "-"

                self.console.print(
                    f"\n[bold][{self.agent_color}]{self.charlie.name}:"
                    f"[/{self.agent_color}][/bold]"
                )
                if self.show_reasoning and reasoning:
                    self.console.print(
                        f"\n[dim][bold]Reasoning:[/bold] {reasoning}[/dim]",
                    )

                self.console.print(f"\n{content}")

                if self.show_token_cost:
                    self.console.print(
                        f"\n[dim]Token cost:[/dim] {token_cost}",
                    )

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
            self._maybe_show_traceback()
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
            self._maybe_show_traceback()
        except requests.exceptions.RequestException:
            self.console.print(
                "\n[bold][red]Error:[/red][/bold] Request to the server "
                "failed."
            )
            self._maybe_show_traceback()
        except (RuntimeError, ValueError, KeyError) as exc:
            self.console.print(
                "\n[bold][red]Error:[/red][/bold] "
                f"C.H.A.R.L.I.E. encountered an error: {exc}"
            )
            self._maybe_show_traceback()
        except Exception:
            self.console.print(
                f"\n[bold][red]Error:[/red][/bold] An unexpected error "
                "occurred."
            )
            self._maybe_show_traceback()
        else:
            self.console.print(f"\n[dim]{self.exit_message}[/dim]")
            return
