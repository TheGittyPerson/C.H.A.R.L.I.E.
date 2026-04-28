from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Contexts:
    """Stores context providers and renders them into prompt content."""

    contexts: dict[str, Callable[[], str]] = field(default_factory=dict)

    def register(self, func: Callable[[], str]) -> Callable[[], str]:
        """Register a callable context provider by function name."""
        self.contexts[func.__name__] = func
        return func

    def render(self) -> str:
        """Render all registered context providers into system prompt text."""
        return "\n\n".join(
            f"<context>\n<{name}>{func()}</{name}></context>"
            for name, func in self.contexts.items()
        )
