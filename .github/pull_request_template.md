## Summary
Explain what changed and why.

## Validation
- [ ] `pytest -q`
- [ ] `opendev security .`
- [ ] Documentation updated if behavior changed

## Security review
Check any relevant areas:
- [ ] Untrusted repository content / prompt injection
- [ ] File-system access / path handling
- [ ] Shell or subprocess behavior
- [ ] Network requests
- [ ] API keys / credentials
- [ ] Dependency or supply-chain changes
- [ ] None of the above

## Notes for reviewers
Call out assumptions, limitations, or follow-up work.
