# MCP Chat

MCP Chat is a command-line application that chats with an LLM via **OpenRouter** and extends the model with **MCP (Model Context Protocol)** tools, resources, and prompts. The stack demonstrates a minimal **MCP host** (CLI + model loop), an **MCP client** (stdio), and an **MCP server** (FastMCP) working together.

## How to approach learning this codebase

Use this order so concepts stay grounded in running code and the notes stay in sync with the repo.

### 1. Read the notes first (concepts + diagrams)

1. **[`notes/basics.md`](notes/basics.md)** — Host, client, server; tools, resources, prompts in order; stdio mental model; how this repo maps to each piece.
2. **[`notes/advanced.md`](notes/advanced.md)** — JSON-RPC message categories, Streamable HTTP / SSE, load balancing and `stateless` / `json_response`, **sampling**, logging & progress, **roots**; figure index for everything under [`notes/images/`](notes/images/).

Skim the official docs in parallel when a section links out: [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture), [intro](https://modelcontextprotocol.io/docs/getting-started/intro), [spec](https://modelcontextprotocol.io/specification/latest).

### 2. Run the app, then read the root project in file order

1. Complete **Prerequisites** and **Setup** below, then run `uv run main.py` (or `python main.py`).
2. Try **Usage**: plain chat, `@document` mentions (resources), `/command` flows (prompts), and tool use via the model.
3. Trace execution top-down:
   - [`main.py`](main.py) — spawns `MCPClient`, builds `CliChat` / `CliApp`, optional extra servers from CLI args.
   - [`mcp_client.py`](mcp_client.py) — stdio transport, `initialize`, `list_tools`, `call_tool`, resources, prompts.
   - [`mcp_server.py`](mcp_server.py) — FastMCP: tools (`read_doc_contents`, `edit_document`), resources (`docs://…`), prompt (`format`).
   - [`core/chat.py`](core/chat.py) + [`core/tools.py`](core/tools.py) — aggregate MCP tools for OpenRouter and run the tool-call loop.
   - [`core/cli_chat.py`](core/cli_chat.py) — `@` resource injection and `/` prompt commands.
   - [`core/openrouter.py`](core/openrouter.py), [`core/cli.py`](core/cli.py), [`core/cli_chat.py`](core/cli_chat.py) — CLI and API wiring.

### 3. Advanced transport and server UX (`mcp-advanced/`)

The root app uses **stdio**. For **Streamable HTTP**, logging/progress in a server, and flags like `stateless_http` / `json_response`, open [`mcp-advanced/README.md`](mcp-advanced/README.md), run [`mcp-advanced/main.py`](mcp-advanced/main.py), and reconcile what you see with **section 2** of [`notes/advanced.md`](notes/advanced.md).

### 4. Extend deliberately

- **New docs or tools:** start in [`mcp_server.py`](mcp_server.py); confirm discovery with `mcp_client.py` or the Inspector.
- **Host behavior:** [`core/cli_chat.py`](core/cli_chat.py) (mentions, slash commands) and [`core/chat.py`](core/chat.py) (model + tools).
- **Second MCP server:** pass another script as a CLI argument to [`main.py`](main.py) and follow how `clients` is built.

## Learning resources

- [Anthropic — Introduction to Model Context Protocol (Skilljar)](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [MCP — Getting started / intro](https://modelcontextprotocol.io/docs/getting-started/intro)
- [MCP — Architecture overview](https://modelcontextprotocol.io/docs/learn/architecture)

## Prerequisites

- Python 3.10+ (see [`pyproject.toml`](pyproject.toml))
- OpenRouter API key and a chosen model id

## Setup

### Step 1: Configure environment variables

Create or edit `.env` in the project root:

```env
OPENROUTER_API_KEY=""   # your OpenRouter API key
OPENROUTER_MODEL=""     # e.g. anthropic/claude-3.5-sonnet (see OpenRouter model list)
# Optional: USE_UV=1 makes main.py spawn the server with `uv run mcp_server.py`
```

### Step 2: Install dependencies

#### Option 1: uv (recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

1. Install uv if needed: `pip install uv`
2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. Install and run:

```bash
uv pip install -e .
uv run main.py
```

#### Option 2: pip

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
python main.py
```

## Usage

### Basic interaction

Type a message and press Enter to chat with the model.

### Document retrieval (resources via `@`)

Include a document id from the server’s catalog:

```text
> Tell me about @deposition.md
```

### Commands (prompts via `/`)

Run server-defined prompts by name (Tab completes):

```text
> /format deposition.md
```

## Development

### Adding new documents

Edit the `docs` dictionary in [`mcp_server.py`](mcp_server.py).

### Implementing or extending MCP behavior

1. Server surface: tools, resources, prompts in [`mcp_server.py`](mcp_server.py).
2. Client/session helpers: [`mcp_client.py`](mcp_client.py).
3. Host integration: [`core/chat.py`](core/chat.py), [`core/tools.py`](core/tools.py), [`core/cli_chat.py`](core/cli_chat.py).

### Linting and typing

There are no shared lint or type-check tasks in this repo yet; add them if you want stricter CI.
