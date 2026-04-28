<h1 align="center"><i>C.H.A.R.L.I.E.</i></h1>

**<p align="center">Version 0.1.0</p>**

<p align="center">
  <b>C</b>ognitive <b>H</b>elper for <b>A</b>daptive <b>R</b>esponse and 
  <b>L</b>ogical <b>I</b>ntelligent <b>E</b>xecution
</p>

> By _[Morpheus][profile]_

## What the `charlie` package does

`charlie` is a Python package for building a conversational AI agent that can:

- send chat requests to an OpenAI-compatible `/chat/completions` endpoint
- register tools the model can call during a conversation
- register runtime context providers and inject their output into the prompt
- run an interactive terminal chat loop

The package is structured around an `Agent` class, a tool registry, a context
registry, and a small set of built-in toolsets for text and math operations.

---

## How to use

```python
from charlie.agent import Agent
from charlie.contexts import register_default_contexts
from charlie.toolsets import (
    register_math_tools,
    register_text_tools,
)
from charlie import cli

if __name__ == "__main__":
    charlie = Agent(
        model="qwen/qwen3.5-9b",
        reasoning="medium",
        system_prompt="Your name is C.H.A.R.L.I.E. (Cognitive Helper for "
                      "Adaptive Response and Logical Intelligent Execution). "
                      "Responses should be no longer than 300 characters "
                      "unless the prompt deems it necessary. You are a "
                      "helpful and friendly assistant that does what they are "
                      "told to do. You know your limits and tell the user "
                      "when they are unable to do a task or don't know "
                      "something, avoiding assumptions and guessing)."
    )

    register_default_contexts(charlie, username="Morpheus")

    register_math_tools(charlie)
    register_text_tools(charlie)

    cli.start(charlie)
```

By default, `Agent` targets a local OpenAI-compatible server at 
`http://127.0.0.1:1234/v1`, so make sure that endpoint is available or 
override `base_url` when creating the agent.

## How to install

1. Go to the repository homepage on GitHub
2. Click on [Releases][releases] (found on the right column on Desktop)
3. Scroll to the latest release and select one of the download links 
   (ZIP recommended) under 'Assets'
4. Open the downloaded archive file on your local machine

---

Special thanks to **[@indently](https://github.com/indently)** for his YouTube 
tutorial series, ["Build a Local AI Agent in Python"][vid]. Check out his 
YouTube chanel [here](https://www.youtube.com/@Indently).

---

## License

This project is licensed under the [MIT License](LICENSE.txt).


[profile]: https://github.com/TheGittyPerson
[repo]: https://github.com/TheGittyPerson/C.H.A.R.L.I.E.
[releases]: https://github.com/TheGittyPerson/C.H.A.R.L.I.E./releases
[vid]: https://www.youtube.com/watch?v=LykXu60aKoY&list=PL4KX3oEgJcfcPez5tpvsdC1ghaNFo1Bhc
