# Changelog

## 0.5.0 - 2026-09-10

- Added optional SARIF 2.1.0 output for `security`, `deps`, and `prompt-scan`.
- Mapped OpenDevKit high, medium, and low findings to SARIF error, warning, and note levels.
- Included repository-relative artifact locations and source lines for code-scanning annotations.
- Preserved normal console or JSON output and ensured SARIF is written before `--fail-on` exits.
- Added regression tests for populated and empty SARIF reports, URI encoding, and threshold failures.
- Documented GitHub Code Scanning integration and its required workflow permissions.

## 0.4.0 - 2026-09-04

- Added optional `.opendevkit.toml` repository configuration with validated, repository-relative exclusion patterns.
- Applied configured exclusions consistently to analysis, security, dependency, prompt, report, and repository-wide AI context paths.
- Normalized reported repository-relative paths to POSIX separators on every operating system.
- Kept built-in ignored directories active and explicit `review --path` selection available.
- Skipped symbolic links during repository-wide traversal and rejected symlinked configuration files.
- Added visible exclusion metadata to analysis output, reports, and AI context.
- Added clear configuration errors and regression tests for exclusions and malformed settings.
- Documented that repository-controlled exclusions can hide findings and require review.

## 0.3.1 - 2026-08-28

- Added wheel and source-distribution build checks, clean-environment installation checks, and a Windows test job.
- Added a GitHub release workflow that publishes only artifacts from a successful main-branch test run.
- Added an opt-in PyPI Trusted Publishing workflow for already-published release artifacts.
- Added SPDX license metadata and project links for package indexes.
- Fixed installation instructions to include obtaining the source or release wheel.
- Added a local trial guide, bug reports, and honest usage-feedback templates.
- Clarified that reports write files and that optional AI review does not automatically redact secrets.

## 0.3.0 - 2026-08-23

- Added `--fail-on low|medium|high` to `security`, `deps`, and `prompt-scan` for CI enforcement.
- Preserved advisory exit behavior when no threshold is selected.
- Ensured human-readable and JSON results are emitted before a threshold failure exits with status 1.
- Added tests for passing, failing, JSON, and invalid-threshold behavior.


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
