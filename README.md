# stakagents

A framework for prototyping, running, and evaluating AI agents powered by LangChain, LangGraph, and LiteLLM.

## Features

- **Agent Core Architecture**: Modular agent foundation with registry management (`src/stakagents/core/agent.py`, `src/stakagents/core/registry.py`).
- **LLM & Gateway Integration**: LiteLLM configuration and client management (`litellm.config.yaml`, `src/stakagents/core/llm.py`).
- **Telemetry & Tracing**: Built-in OpenTelemetry and OpenInference instrumentation for LangChain tracing (`src/stakagents/core/tracing.py`).
- **Web Service**: FastAPI and Uvicorn-based service interface (`src/stakagents/service/`).
- **Prebuilt Agents**: Ready-to-use specialized agents, such as the `readme_generator` agent.
- **Evaluation Support**: Dedicated module for agent evaluation workflows (`src/stakagents/evals/`).
- **Containerized Deployment**: Docker Compose setups included (`docker-compose.yml`, `docker-compose.override.yml`).

## Requirements

- Python `>=3.12`
- [uv](https://github.com/astral-sh/uv) (or standard Python package managers)

## Installation

Clone the repository and install dependencies using `uv`:

```bash
git clone https://github.com/Hackastak/stakagents.git
cd stakagents
uv sync
```

## Configuration

Copy the example environment configuration file and update it with your credentials:

```bash
cp .env.example .env
```

Model routing and gateway settings can be configured via `litellm.config.yaml`.

## Usage

### Running via CLI

Execute the package CLI entry point:

```bash
uv run stakagents
```

### Running with Docker Compose

Start the services with Docker Compose:

```bash
docker compose up
```

## Project Structure

```text
stakagents/
├── docker-compose.yml            # Docker services definition
├── docker-compose.override.yml   # Local Docker overrides
├── litellm.config.yaml           # LiteLLM proxy configuration
├── pyproject.toml                # Project metadata and dependencies
├── uv.lock                       # Dependency lockfile
├── .env.example                  # Example environment variables
└── src/
    └── stakagents/
        ├── __init__.py           # Package root and CLI entry point
        ├── agents/               # Implemented agent workflows
        │   ├── __init__.py
        │   └── readme_generator.py
        ├── core/                 # Core utilities and base classes
        │   ├── __init__.py
        │   ├── agent.py          # Base agent definitions
        │   ├── config.py         # Settings and environment configuration
        │   ├── llm.py            # LLM initialization
        │   ├── registry.py       # Agent registry
        │   └── tracing.py        # OpenTelemetry & OpenInference tracing
        ├── evals/                # Agent evaluation logic
        │   └── __init__.py
        └── service/              # API and web service layer
            └── __init__.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
