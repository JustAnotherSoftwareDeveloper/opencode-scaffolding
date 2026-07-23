# Task Delegation Reference

- Treat `SKILL.md` as the authoritative packet construction and worker result handling contract.
- Use `./fixtures/complete-no-files.txt` for complete analysis-only result validation.
- Use `./fixtures/complete-file-change.txt` for file reconciliation validation.
- Use `./fixtures/partial.txt` for partial result validation.
- Use `./fixtures/blocked.txt` for blocked result validation.
- Use `./fixtures/malformed.txt` for malformed envelope rejection.
- Use `./fixtures/malformed-status.txt` for invalid status rejection.
- Use `./fixtures/decomposition-complete.txt` for decomposition payload extraction validation.
- Use `./fixtures/complete-markdown-payload.txt` for payload-heading boundary validation.
- Use `./fixtures/unknown-sentinel.txt` for unknown packet sentinel rejection.
- Use `./fixtures/skill-mismatch.txt` for declared-skill reconciliation rejection.
- Use `./fixtures/unauthorized-file.txt` and `./fixtures/unreconciled-output.txt` for write-boundary rejection.
- Use `./fixtures/empty-success-payload.txt` and `./fixtures/false-completion.txt` to reject success without an executed payload.
