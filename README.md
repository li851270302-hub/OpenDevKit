# OpenDevKit

[![Tests](https://github.com/li851270302-hub/OpenDevKit/actions/workflows/tests.yml/badge.svg)](https://github.com/li851270302-hub/OpenDevKit/actions/workflows/tests.yml)

OpenDevKit is a local-first Python CLI for practical software maintenance. It helps developers inspect a repository, run lightweight security checks, review code with an optional OpenAI API integration, generate test ideas, and prepare maintenance reports.

## Features

- `analyze` — inspect repository structure, languages, file counts, and likely entry points.
- `security` — run a conservative static scan for common secret, unsafe subprocess, path-handling, and untrusted-instruction risks.
- `deps` — inspect Python and Node.js dependency manifests for non-exact versions and parse problems.
- `prompt-scan` — flag repository text that may try to manipulate an AI-assisted maintenance workflow.
- `review` — send selected source files to an OpenAI model for code review.
- `test` — generate focused test plans from the current repository.
- `docs` — generate a README draft from repository metadata.
- `report` — combine local analysis, security findings, and dependency findings into a Markdown report.

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
opendev deps .
opendev prompt-scan .
opendev report . --output maintenance-report.md
opendev review . --path opendevkit/scanner.py
opendev test .
opendev docs .
```

To review only one file, pass a repository-relative path. OpenDevKit still includes a bounded repository summary, but only the selected file is added as source context:

```bash
opendev review . --path opendevkit/scanner.py
```

For machine-readable output:

```bash
opendev analyze . --json
opendev security . --json
opendev deps . --json
opendev prompt-scan . --json
```

Dependency findings are advisory. A non-exact version is reported for review but does not prove a vulnerable package. Untrusted-instruction findings are also heuristic and should be validated by a human.

## Security model

OpenDevKit is intentionally conservative:

1. Repository content is treated as untrusted input.
2. Static analysis never executes repository code.
3. The CLI does not run arbitrary commands supplied by an LLM.
4. API keys are read from environment variables and are never written to reports.
5. AI review is optional and sends only the selected files plus a bounded repository summary.
6. Dependency and untrusted-instruction findings are explainable heuristics for human review.
7. Users should review generated suggestions before applying changes.

This project is designed as a maintenance assistant, not an autonomous code execution agent.

## Development

```bash
pip install -e ".[dev]"
pytest -q
opendev security .
opendev deps . --json
opendev prompt-scan . --json
```

## License

MIT
