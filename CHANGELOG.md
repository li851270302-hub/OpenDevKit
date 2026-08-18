# Changelog

## 0.2.1 - 2026-08-18

- Fixed `review --path` so only the selected file is added to AI source context.
- Added clear errors for review paths outside the repository or paths that are not files.
- Added dependency findings to Markdown maintenance reports.
- Added CLI, AI-context, and report tests without calling the live OpenAI API.


## 0.2.0 - 2026-08-14

- Added dependency manifest scanning for Python and Node.js projects.
- Added untrusted-instruction scanning for AI-assisted maintenance workflows.
- Added detection for GitHub tokens, bearer tokens, and pipe-to-shell patterns.
- Added dedicated `deps` and `prompt-scan` CLI commands with JSON output.
- Expanded automated tests and CI coverage for the new security commands.
- Documented the advisory, human-reviewed security model.

## 0.1.0 - 2026-08-12

- Initial public release.
- Added repository analysis.
- Added conservative static security checks.
- Added optional OpenAI-assisted review, test planning, and documentation drafting.
- Added Markdown maintenance reports.
- Added automated tests and GitHub Actions.
