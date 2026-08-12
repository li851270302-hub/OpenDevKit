# OpenDevKit

[![Tests](https://github.com/li851270302-hub/OpenDevKit/actions/workflows/tests.yml/badge.svg)](https://github.com/li851270302-hub/OpenDevKit/actions/workflows/tests.yml)

OpenDevKit is a local-first Python CLI for practical software maintenance. It helps developers inspect a repository, run lightweight security checks, review code with an optional OpenAI API integration, generate test ideas, and prepare maintenance reports.

## Features

- `analyze` — inspect repository structure, languages, file counts, and likely entry points.
- `security` — run a conservative static scan for common secret, unsafe subprocess, path-handling, and dependency risks.
- `review` — send selected source files to an OpenAI model for code review.
- `test` — generate focused test plans from the current repository.
- `docs` — generate a README draft from repository metadata.
- `report` — combine local analysis and security findings into a Markdown report.

OpenDevKit does **not** execute generated code, install dependencies, modify files, or run arbitrary shell commands. AI-assisted commands are advisory by default.

## Requirements

- Python 3.10+
- Optional: an OpenAI API key for `review`, `test`, and `docs`

## Installation

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -e .
```

Copy `.env.example` to `.env` if you want to use the OpenAI API. The `.env` file is ignored by Git:

```text
OPENAI_API_KEY=your_key_here
OPENDEVKIT_MODEL=gpt-5.6-luna
```

The OpenAI Python SDK is used through the Responses API.

## Usage

```bash
opendev analyze .
opendev security .
opendev report . --output maintenance-report.md
opendev review . --path opendevkit/security.py
opendev test .
opendev docs .
```

For JSON output:

```bash
opendev analyze . --json
opendev security . --json
```

## Security model

OpenDevKit is intentionally conservative:

1. Repository content is treated as untrusted input.
2. Static analysis never executes repository code.
3. The CLI does not run arbitrary commands supplied by an LLM.
4. API keys are read from environment variables and are never written to reports.
5. AI review is optional and sends only the selected files plus a bounded repository summary.
6. Users should review generated suggestions before applying changes.

This project is designed as a maintenance assistant, not an autonomous code execution agent.

## Development

```bash
pip install -e ".[dev]"
pytest -q
```

## License

MIT
