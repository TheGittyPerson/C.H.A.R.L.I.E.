from typing import Any

from rich.console import Console


def start(charlie: Any) -> int:
    console = Console()

    while True:
        console.print("\n[green]You:[/green] ", end="")
        user_input = console.input()

        if user_input.lower().strip() in ["quit", "exit", "bye"]:
            console.print("\n[dim]Bye![/dim]")
            return 0

        with console.status("[dim]Thinking...[/dim]", spinner="aesthetic"):
            response = charlie.chat(user_input).strip()

        console.print(f"\n[blue]C.H.A.R.L.I.E.:[/blue] {response}")
