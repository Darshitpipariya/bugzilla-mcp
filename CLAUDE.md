# Bugzilla MCP Server - Developer Guide

This document acts as the source of truth for developer tools, build/test commands, project architecture, and code styling rules for the Bugzilla Model Context Protocol (MCP) server.

---

## 🛠 Build & Run Commands

This project uses `uv` for python package and dependency management.

### Environment Setup
```bash
# Sync all dependencies (including test suite)
uv sync --all-extras
```

### Local Development Server
Starts the FastMCP HTTP server locally:
```bash
# Start the local development server (binds to http://127.0.0.1:8000/mcp)
uv run python server.py
```

### Server Inspection
Inspect server tools, prompts, and configurations using the FastMCP CLI:
```bash
# Inspect the MCP server schemas and interface
uv run fastmcp inspect server.py:mcp
```

---

## 🧪 Testing Commands

We use `pytest` with async/httpx plugins for writing and executing tests.

### Run All Tests
```bash
uv run pytest
```

### Run Tests with Coverage
```bash
uv run pytest --cov=bugzilla_mcp
```

### Run Specific Test Suites
```bash
# Run middleware tests only
uv run pytest tests/test_middleware

# Run tool tests only
uv run pytest tests/test_tools

# Run utility client tests only
uv run pytest tests/test_utils

# Run a single specific test file
uv run pytest tests/test_tools/test_bugzilla.py
```

---

## 🚀 RTK - Rust Token Killer Integration

The repository integrates **RTK** to optimize CLI execution and save context tokens.

### RTK Core Commands
```bash
rtk gain              # Show token savings analytics
rtk gain --history    # Show command usage history with savings
rtk discover          # Analyze Claude Code history for missed opportunities
rtk proxy <cmd>       # Execute raw command without filtering (for debugging)
rtk --version         # Verify installation & view version
which rtk             # Verify binary path
```

### Hook-Based Transparent Execution
All standard CLI and git operations are transparently intercepted and rewritten by the Claude Code hook.
- Run them normally in your terminal (e.g., `git status`, `git diff`) and they are transparently mapped to `rtk <command>` without manual prefixing.

---

## 🏗 Codebase Architecture

The project is a standard Python application built with **FastMCP** implementing the **Model Context Protocol** (MCP) for communicating securely with Bugzilla rest endpoints.

```
bugzilla-mcp/
├── bugzilla_mcp/             # Main application package
│   ├── middleware/           # MCP Middleware (Header validation & client configuration)
│   │   ├── __init__.py
│   │   └── validate_headers.py
│   ├── tools/                # MCP Tool registration and execution
│   │   ├── __init__.py
│   │   └── bugzilla.py
│   ├── utils/                # Bugzilla HTTP utility client & global references
│   │   ├── __init__.py
│   │   └── bugzilla.py
│   └── __init__.py
├── tests/                    # Complete PyTest Suite
│   ├── test_middleware/      # Headers validation & edge case coverage
│   ├── test_tools/           # MCP tools integration tests
│   ├── test_utils/           # Mocked API client unit tests
│   └── conftest.py           # Shared fixtures and mock definitions
├── docs/                     # Static NuxtJS-based documentation site
├── pyproject.toml            # Project dependencies & Python metadata
├── server.py                 # Application entrypoint & FastMCP initialization
└── README.md                 # Public overview and integration guides
```

### Key Architectural Concepts
1. **Dynamic Client Initialization (`ValidateHeaders` Middleware)**:
   Because MCP servers are designed to be stateless or multi-tenant, authentication is passed dynamically per request through HTTP headers (`api_key` and `bugzilla_url`). The `ValidateHeaders` middleware extracts these headers on each request and binds a `Bugzilla` client instance to a globally shared reference `bugzilla_mcp.utils.bz`.
2. **Graceful Inspection Fallback**:
   During FastMCP server inspection (via `fastmcp inspect`), HTTP headers are absent. The middleware detects this and initializes a dummy client reference (`https://bugzilla.example.com` / `inspection-placeholder`) to ensure schema discovery works seamlessly without auth failures.
3. **Resource Tokens Optimization**:
   To minimize context token size in queries, search responses (`bugs_quicksearch`) filter full Bugzilla records down to only the essential subset of fields (`bug_id`, `product`, `component`, `assigned_to`, `status`, `resolution`, `summary`, `last_updated`). Detailed info can be requested on-demand using the `bug_info` tool.

---

## 🎨 Code Style & Development Guidelines

### Python Guidelines
- **Python Version Compatibility**: Enforce compatibility with Python `>=3.12`.
- **Type Annotations**: Always include full type annotations for new functions, methods, and variables. Use standard generic types (e.g. `dict[str, Any]`, `list[Any]`).
- **Asynchronous Execution**: Always use `async`/`await` for HTTP calls and file interactions. Use the shared asynchronous `httpx.AsyncClient` from the `Bugzilla` utility client class (`self.client`) for any Bugzilla rest APIs.
- **Error Handling**: 
  - Raise `fastmcp.exceptions.ToolError` inside MCP tools to convey user-friendly or LLM-friendly errors.
  - Raise `fastmcp.exceptions.PromptError` / `ValidationError` for malformed inputs or validation failures in middleware/prompts.
- **Docstrings**: Document every module, class, tool, and utility method with clear Python docstrings. Keep docstrings updated when refactoring function signatures.
- **Imports Sorting**: Follow PEP 8 guidelines. Group imports:
  1. Standard library imports
  2. Third-party imports (e.g., `fastmcp`, `httpx`, `dotenv`)
  3. Local package imports (e.g., `bugzilla_mcp`)
