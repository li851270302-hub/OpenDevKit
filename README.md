# OpenDevKit

[![Tests](https://github.com/li851270302-hub/OpenDevKit/actions/workflows/tests.yml/badge.svg)](https://github.com/li851270302-hub/OpenDevKit/actions/workflows/tests.yml)

OpenDevKit is a local-first Python CLI for practical software maintenance. It helps developers inspect a repository, run lightweight security checks, review code with an optional OpenAI API integration, generate test ideas, and prepare maintenance reports.

## Features

- `analyze` — inspect repository structure, languages, file counts, and likely entry points.
- `security` — run a conservative static scan for common secret, unsafe subprocess, path-handling, and untrusted-instruction risks.
- `deps` — inspect Python and Node.js dependency manifests for non-exact versions and parse problems.
- `prompt-scan` — flag repository text that may try to manipulate an AI-assisted maintenance workflow.
- `--fail-on` — make security scans CI-enforceable at a selected severity while preserving advisory defaults.
- `review` — send selected source files to an OpenAI model for code review.
- `test` — generate focused test plans from the current repository.
- `docs` — generate a README draft from repository metadata.
- `report` — combine local analysis, security findings, and dependency findings into a Markdown report.

OpenDevKit does **not** execute generated code, install dependencies, or run arbitrary shell commands. Scans are read-only; `report` writes only the requested output file. AI-assisted commands return suggestions without applying them.

This is an early-stage project. Its scans use heuristics and can miss real issues or flag harmless examples; they are not a security audit or a vulnerability database lookup.

## Requirements

- Python 3.10+
- Optional: an OpenAI API key for `review`, `test`, and `docs`

## Installation

### Install a GitHub release

Download the `.whl` file from [GitHub Releases](https://github.com/li851270302-hub/OpenDevKit/releases), then install it in a virtual environment:

```bash
python -m venv .venv
```

Activate it using the command for your shell:

| Shell | Command |
| --- | --- |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows Command Prompt | `.venv\Scripts\activate.bat` |
| macOS/Linux | `source .venv/bin/activate` |

```bash
python -m pip install ./opendevkit-0.3.1-py3-none-any.whl
opendev version
opendev --help
```

The wheel path above assumes that you saved the download in the current directory.
PyPI publication is separate from a GitHub release; use the release wheel until a PyPI project linked to this repository is verified.

### Install from source

```bash
git clone https://github.com/li851270302-hub/OpenDevKit.git
cd OpenDevKit
python -m venv .venv
# Activate the environment using the table above, then:
python -m pip install -e .
```

### Optional AI commands

For a source checkout, copy `.env.example` to `.env` if you want to use the OpenAI API. For a wheel installation, set the following environment variables yourself. Keep credentials out of version control:

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
opendev security . --fail-on high
opendev deps . --fail-on low
opendev prompt-scan . --fail-on medium
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

By default, scan findings are advisory and the commands exit successfully. For CI enforcement, pass `--fail-on low`, `--fail-on medium`, or `--fail-on high`; a finding at the selected severity or higher exits with status 1 after normal table or JSON output is emitted.

Dependency findings remain heuristic: a non-exact version is reported for review but does not prove a vulnerable package. Untrusted-instruction findings should also be validated by a human.

## Security model

OpenDevKit is intentionally conservative:

1. Repository content is treated as untrusted input.
2. Static analysis never executes repository code.
3. The CLI does not run arbitrary commands supplied by an LLM.
4. The configured API credential is read from the environment. CLI and report findings omit evidence snippets, but paths and source files may still contain sensitive information.
5. AI review is optional and sends only the selected files plus a bounded repository summary.
6. Dependency and untrusted-instruction findings are explainable heuristics for human review.
7. Users should review generated suggestions before applying changes.

This project is designed as a maintenance assistant, not an autonomous code execution agent.

AI review sends source content to the configured OpenAI service and does not automatically redact secrets. Inspect the selected files first. Local commands (`analyze`, `security`, `deps`, `prompt-scan`, and `report`) do not need an API key.

## Try it and give feedback

Follow the [five-minute local trial](https://github.com/li851270302-hub/OpenDevKit/blob/main/docs/TRY_IT.md), then report an installation problem, a false positive, or useful results through [GitHub Issues](https://github.com/li851270302-hub/OpenDevKit/issues/new/choose). Share only sanitized examples you have permission to disclose. A report that it did not work is useful too.

If it helps your work, a GitHub Star is welcome. No Star or positive review is required to get help.

Maintainers can find the build, release, and PyPI setup steps in [Publishing](https://github.com/li851270302-hub/OpenDevKit/blob/main/docs/PUBLISHING.md).

## Development

```bash
pip install -e ".[dev]"
pytest -q
opendev security . --fail-on high
opendev deps . --json --fail-on medium
opendev prompt-scan . --json --fail-on medium
```

## License

MIT
