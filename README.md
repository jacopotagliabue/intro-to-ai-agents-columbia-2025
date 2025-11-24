# Introduction to AI agents (Columbia University 2025)

## Overview
This repo contains code snippets used for my 2025 lecture at Columbia University, an introduction to AI Agents ([slides here](https://jacopotagliabue.it/public/Columbia_Slides_nov_2025.pdf)) titled: "From LLMs to agents: The road to autonomy is paved with good intentions".

## Setup

### Python
We use [uv](https://docs.astral.sh/uv/guides/install-python/) to manage the environment. To set up the environment, run:

```bash
uv sync
```

### LLM
We use Anthropic APIs for the LLM backend. Make sure to create a `.env` file in `src` directory using `local.env` as a template. If you prefer to use other models, we rely on [LiteLLM](https://github.com/BerriAI/litellm) interface, so it should be straightforward to swap out the model backend. Make sure to change both the `.env` and the LLM init accordingly.

## Running the code

To run the code snippets, navigate to the `src` directory and execute the desired Python script with uv, for example:

```bash
cd src
uv run text_to_tool_to_text.py
```

Please refer to the slides for the general context and the AI background. The code has been developed for educational purposes only, using Claude Code as an AI assistant throughout the development process.

A standalone [Fast MCP server](https://gofastmcp.com/getting-started/welcome) can be found in the `fast_mcp` directory, to showcase how to build and leverage a minimal server inside of an agentic loop: the server gets automatically called from the `agent_with_mcp.py` script, but could also be run in a standalone fashion.

## License

This project is provided "as is" and it is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
