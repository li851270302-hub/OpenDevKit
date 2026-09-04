# Publishing OpenDevKit

A GitHub release and a PyPI release are separate actions. Do not advertise a PyPI
installation until the package page and a fresh installation have been verified.

## Build and test locally

```bash
python -m pip install -e ".[dev]" build twine
python -m pytest -q
python -m build
python -m twine check --strict dist/*
```

Install the wheel in a **new** virtual environment, then use that environment's
Python to run `scripts/smoke_install.py 0.4.0`. It invokes the installed console
command from a temporary directory, exercises the local commands and an expected
high-severity failure, and never calls the OpenAI API.

## GitHub release

1. Update both version fields (`pyproject.toml` and `opendevkit/__init__.py`) and
   add a matching dated entry in `CHANGELOG.md`.
2. Open a PR and wait for all `tests` jobs, including Windows and the distribution
   build, to pass. Review the diff before merging.
3. After merge, a successful `tests` push run on `main` starts `GitHub Release`.
   The release uses the exact tested commit and the distribution artifacts from
   that run, not a new build from a later commit.
4. Check the published tag, wheel, source archive, and `SHA256SUMS` on GitHub.
   The workflow never overwrites an existing release. If it leaves a draft after
   an upload error, inspect the draft before completing or retrying publication.

This does not certify the tool as production-ready or prove third-party use.

## First PyPI publication: one-time account setup

You need your own PyPI account, a verified email, and the account's required
two-factor authentication. Never put a password, recovery code, or API token in
the repository, an issue, or a chat message.

Create a pending Trusted Publisher in your PyPI account's Publishing settings:

| Field | Value |
| --- | --- |
| PyPI project name | `opendevkit` |
| GitHub owner | `li851270302-hub` |
| Repository | `OpenDevKit` |
| Workflow filename | `publish-pypi.yml` |
| Environment | `pypi` |

In the GitHub repository settings, create the `pypi` environment, restrict it to
`main`, and enable a required reviewer if available. The pending publisher does
not reserve the package name. If someone else owns it, stop and choose an honest,
distinct project name; do not upload to an unrelated package.

See the official [pending publisher setup](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
and [publishing guide](https://docs.pypi.org/trusted-publishers/using-a-publisher/).

## Publish and verify

1. In GitHub Actions, run **Publish to PyPI** on `main` with the already-published
   release tag (for this version, `v0.4.0`). Approve the environment if prompted.
2. The workflow verifies release checksums, checks package metadata, and submits
   the same wheel and source archive using short-lived OIDC credentials.
3. A green workflow is not enough: check the PyPI version, owner, and repository
   links, then install `opendevkit==0.4.0` from PyPI in a fresh environment and run
   `opendev version` and `opendev analyze . --json`.
4. Only after that verification should README's installation section recommend
   `python -m pip install opendevkit==0.4.0`.

PyPI does not allow replacing a previously uploaded release file. Fix a bad
release with a new version rather than attempting to overwrite it. Tests and
maintainer installs are verification, not independent adoption statistics.
