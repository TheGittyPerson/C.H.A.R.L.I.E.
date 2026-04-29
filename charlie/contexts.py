import datetime
import getpass
import os
import platform
from typing import Any

from .agent import Agent


def register_default_contexts(charlie: Agent, **context: Any) -> None:
    """Register the default runtime context providers for the CLI.

    Contexts sent to the model:
        - `user_context`
            - current date and time
            - current user
        - `environment_context`
            - current working directory
            - operating system name
            - Python version
            - timezone
        - `response_preferences_context`
            - preferred response length
            - preferred tone/style

    Available context kwargs:
        - `username`: defaults to `getpass.getuser()`
        - `preferred_response_length`: defaults to `"no preference"`
        - `tone_style`: defaults to `"no preference"`
        - `timezone`: defaults to the local system timezone
    """

    @charlie.context
    def user_context() -> str:
        return (
            f"Current date and time: "
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Current user: {context.get('username', getpass.getuser())}\n"
        )

    @charlie.context
    def environment_context() -> str:
        timezone = context.get("timezone")
        if timezone is None:
            timezone = datetime.datetime.now().astimezone().tzinfo

        return (
            f"Current working directory: {os.getcwd()}\n"
            f"Operating system: {platform.system()}\n"
            f"Python version: {platform.python_version()}\n"
            f"Timezone: {timezone}\n"
        )

    @charlie.context
    def response_preferences_context() -> str:
        return (
            "Preferred response length: "
            f"{context.get('preferred_response_length', 'no preference')}\n"
            f"Preferred response tone/style: "
            f"{context.get('tone_style', 'no preference')}\n"
        )
