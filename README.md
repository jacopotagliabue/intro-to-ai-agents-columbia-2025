# Introduction to AI agents (Columbia University 2025)

## Overview
This repo contains code snippets used for my 2025 lecture at Columbia University, an introduction to AI Agents (slides TBA) titled: "From LLMs to agents: The road to autonomy is paved with good intentions".


## Setup

### Python
We use [uv](https://docs.astral.sh/uv/guides/install-python/) to manage the environment. To set up the environment, run:

```bash
uv sync
```

### LLM
We use Anthropic APIs for the LLM backend. Make sure to create a `.env` file in `src` directory using `local.env` as a template. If you prefer to use other models, we rely on [LiteLLM](https://github.com/BerriAI/litellm) interface, so it should be straightforward to swap out the model backend.

## Running the code

To run the code snippets, navigate to the `src` directory and execute the desired Python script with uv, for example:

```bash
cd src
uv run text_to_tool_to_text.py
```