# Five-minute local trial

This trial is for someone who wants to inspect a small Python or Node.js project.
It is optional and requires no API key, payment, Star, or positive review.

1. Install the release wheel using [README](../README.md#installation).
2. Choose a small local repository you own or have permission to inspect. Replace
   `PATH_TO_PROJECT` below with that directory.

```bash
opendev version
opendev analyze PATH_TO_PROJECT --json
opendev security PATH_TO_PROJECT --json
opendev deps PATH_TO_PROJECT --json
opendev prompt-scan PATH_TO_PROJECT --json
opendev report PATH_TO_PROJECT --output trial-report.md
```

Scans read files without executing the scanned code. `report` creates or replaces
the requested output file. No API calls are made by these commands.

## What to look for

- Did installation and `opendev --help` work on your operating system?
- Are file counts and language detection useful?
- Is a finding actionable, a false positive, or missing something you expected?
- Would you use this in a real review or CI workflow? Why, or why not?

An unpinned dependency is not automatically a vulnerability. A prompt-scan match
is a heuristic, not proof that a file is malicious. Read findings before acting.

## Share only what you choose

Use the [issue chooser](https://github.com/li851270302-hub/OpenDevKit/issues/new/choose)
to submit an installation bug or usage feedback. Include the version, OS, Python
version, command, and a minimal sanitized example. Check reports for private file
paths or project names before sharing. Do not post credentials or private code.

Maintainer tests and CI runs are not counted as external feedback. Feedback can
be negative, and you may use the project without submitting anything.
