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
registry, a context registry, and a small set of built-in toolsets for text,
math, datetime, and structured-data operations.

## Read the Docs
- User Guide: [docs/user_guide.md](docs/user_guide.md)

---

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
