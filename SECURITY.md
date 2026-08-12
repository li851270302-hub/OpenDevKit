# Security Policy

## Scope

OpenDevKit is designed to inspect repositories without executing repository code. Security issues involving file handling, secret exposure, unsafe subprocess patterns, dependency handling, or the optional AI integration are in scope.

## Reporting

Please do not publish credentials, tokens, private source code, or a complete exploit in a public issue. Open a private security report through GitHub if the repository enables GitHub Security Advisories, or contact the maintainer privately.

## Security principles

- Repository content is untrusted.
- LLM output is advisory and must not be treated as executable instructions.
- API keys stay outside source control.
- The CLI avoids arbitrary shell execution.
- Security findings are heuristics and require human validation.
