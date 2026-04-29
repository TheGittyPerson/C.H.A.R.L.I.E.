import datetime
import getpass
from typing import Any

from .agent import Agent


def register_default_contexts(charlie: Agent, **context: Any) -> None:
    """Register the default runtime context providers for the CLI.

    Available context kwargs:
    - `username`: defaults to `getpass.getuser()`

    """

    @charlie.context
    def user_context() -> str:
        return (
            f"Current date and time: "
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Current user: {context.get('username', getpass.getuser())}\n"
        )
