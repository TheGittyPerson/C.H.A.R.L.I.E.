<p align="center">
  <img src="assets/images/logo_500x500_nobg.png" alt="logo" style="width: 200px">
</p>

<h1 align="center"><i>C.H.A.R.L.I.E.</i></h1>

**<p align="center">Version 0.1.0</p>**

<p align="center">
  <b>C</b>ognitive <b>H</b>elper for <b>A</b>daptive <b>R</b>esponse and 
  <b>L</b>ogical <b>I</b>ntelligent <b>E</b>xecution
</p>

**C.H.A.R.L.I.E.** is a lightweight, command-line-centered AI agent and 
assistant in Python that can be run locally offline (requires model 
installation) or online using a public API. It is beginner-friendly and highly
customizable, and can be easily integrated into other projects.

> By _[Morpheus][profile]_

## What the `charlie` package does

`charlie` is a Python package for building a conversational AI agent that can:

- send chat requests to an OpenAI-compatible endpoint
- register tools the model can call during a conversation
- register runtime context providers and inject their output into the prompt
- run an interactive and customizable terminal chat loop

The package is structured around an `Agent` class, a `CLI` class, a tool 
registry, a context registry, and a small set of built-in toolsets for text and
math operations.

---

## How to use

```python
from charlie.agent import Agent
from charlie.cli import CLI
from charlie.contexts import register_default_contexts
from charlie.toolsets import (
    register_math_tools,
    register_text_tools,
)

if __name__ == "__main__":
    charlie = Agent(
        model="qwen/qwen3.5-9b",
        base_url="http://127.0.0.1:1234/v1",
        reasoning="low",
        system_prompt=(
            "You are a helpful and friendly assistant that follows the user's "
            "instructions, avoids guessing, and states clearly when you do not "
            "know something."
        ),
    )
    charlie.add_request_kwargs(enable_thinking=True)

    register_default_contexts(
        charlie,
        username="Morpheus",
        preferred_response_length="no longer than 300 characters",
        tone_style="friendly and direct",
    )

    register_math_tools(charlie)
    register_text_tools(charlie)

    cli = CLI(charlie, show_reasoning=True)
    cli.start()

```

### `Agent`: the core runtime

`Agent` is the main class in the package. It represents a stateful chat client
that talks to an OpenAI-compatible endpoint and keeps track of the conversation
history in memory.

To build an agent instance, you provide:

- `model`: the model identifier to send in the request
- `base_url`: the root URL for the chat backend
- optional generation settings such as `temperature`, `repeat_penalty`,
  `max_output_tokens`, and `reasoning`
- `system_prompt`: the behavior and instruction prompt for the assistant

If a backend needs extra request fields that are not first-class `Agent`
attributes, you can add them after initialization with
`add_request_kwargs()`. Those values are merged into the outgoing
chat-completions payload.

```python
charlie.add_request_kwargs(top_p=0.9, seed=7, stop=["END"])
```

Once initialized, the main method you use is `chat()`:

```python
reply = charlie.chat("Summarize this in two sentences.")
```

`chat()` returns a dictionary with at least:

- `content`: the assistant's final response text
- `reasoning`: optional reasoning text when the backend returns it and the
  current configuration includes it

Calling `chat()`:

1. appends the user message to `messages`
2. prepends the current system prompt and rendered runtime contexts
3. sends the request to the configured `/chat/completions` endpoint
4. stores the assistant reply
5. executes any requested tool calls
6. continues looping until the model returns a final normal response

This means you can call `chat()` from a script, GUI, web app, or terminal loop 
and let the agent handle tool execution automatically.

### Registering tools on the agent

The `tool()` decorator attaches normal Python functions to the agent so the
model can call them.

```python
@charlie.tool
def add(a: int, b: int) -> dict[str, int]:
    """Add two numbers together."""
    return {"result": a + b}
```

The tool registry inspects the function signature, converts type annotations
into a tool schema, and exposes that schema to the model. When the model emits
a tool call, the agent runs the matching Python function and appends the result
back into the conversation as a tool message.

Out of the box, the project includes some basic helper registration functions 
that you can directly import into your project.

### Registering runtime context

The `context()` decorator lets you register callables that produce dynamic text
for the prompt at request time.

```python
@charlie.context
def project_context() -> str:
    return "Project phase: prototype"
```

Each registered context is rendered into a structured `<context>` block and
inserted as a system message before every request. This is useful for
information that changes over time or depends on the current environment.

The built-in `register_default_contexts()` helper currently adds user-oriented
runtime context such as:

- the current date and time
- the current username, or a provided `username`
- the current working directory
- the operating system name
- the Python version
- the timezone
- the preferred response length
- the preferred tone/style

### `CLI`: the interactive terminal wrapper

`CLI` is a separate dataclass that wraps an `Agent` and runs a terminal chat
session for it. The class exists so the interactive experience is configurable
without changing the agent implementation itself.

Basic usage:

```python
cli = CLI(charlie)
cli.start()
```

Calling `start()` launches a read-eval-print loop that:

1. prints a user prompt
2. reads input from the terminal
3. exits cleanly if the input matches one of the configured exit keywords
4. shows a Rich status spinner while the agent is thinking
5. prints the assistant response using the agent's configured `name`

The CLI is customizable through instance attributes:

- `console`: the Rich `Console` object used for terminal I/O
- `show_reasoning`: whether to print returned reasoning text
- `user_color`: color for the `You:` prompt
- `agent_color`: color for the assistant name
- `spinner_style`: Rich spinner style while waiting on the model
- `thinking_message`: status text shown during generation
- `exit_keywords`: words that end the session
- `exit_message`: final message printed when the loop exits

In short, the user can treat `Agent` as the programmable brain and `CLI` as the
default terminal front end.

## How to install

1. Go to the repository homepage on GitHub
2. Click on [Releases][releases] (found on the right column on Desktop)
3. Scroll to the latest release and select one of the download links 
   (ZIP recommended) under 'Assets'
4. Open the downloaded archive file on your local machine

---

Special thanks to **[@indently](https://github.com/indently)** for his YouTube 
tutorial series, ["Build a Local AI Agent in Python"][vid], which helped get 
this project started. Check out his YouTube chanel 
[here](https://www.youtube.com/@Indently).

---

## License

This project is licensed under the [MIT License](LICENSE.txt).


[profile]: https://github.com/TheGittyPerson
[repo]: https://github.com/TheGittyPerson/C.H.A.R.L.I.E.
[releases]: https://github.com/TheGittyPerson/C.H.A.R.L.I.E./releases
[vid]: https://www.youtube.com/watch?v=LykXu60aKoY&list=PL4KX3oEgJcfcPez5tpvsdC1ghaNFo1Bhc
