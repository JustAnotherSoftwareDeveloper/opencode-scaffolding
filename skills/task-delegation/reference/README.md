# Task Delegation Reference

- Read `~/.config/opencode/output-contract-template.md` as the sole worker-envelope
  grammar. Fixtures illustrate outcomes but never override that contract.
- Treat `SKILL.md` as the authoritative packet construction and worker result handling contract.
- Use [complete-no-files.txt](./fixtures/complete-no-files.txt) for complete analysis-only result validation.
- Use [complete-file-change.txt](./fixtures/complete-file-change.txt) for file reconciliation validation.
- Use [partial.txt](./fixtures/partial.txt) for partial result validation.
- Use [blocked.txt](./fixtures/blocked.txt) for blocked result validation.
- Use [malformed.txt](./fixtures/malformed.txt) for malformed envelope rejection.
- Use [malformed-status.txt](./fixtures/malformed-status.txt) for invalid status rejection.
- Use [decomposition-complete.txt](./fixtures/decomposition-complete.txt) for decomposition payload extraction validation.
- Use [complete-markdown-payload.txt](./fixtures/complete-markdown-payload.txt) for payload-heading boundary validation.
- Use [unknown-sentinel.txt](./fixtures/unknown-sentinel.txt) for unknown packet sentinel rejection.
- Use [skill-mismatch.txt](./fixtures/skill-mismatch.txt) for declared-skill reconciliation rejection.
- Use [unauthorized-file.txt](./fixtures/unauthorized-file.txt) and [unreconciled-output.txt](./fixtures/unreconciled-output.txt) for write-boundary rejection.
- Use [empty-success-payload.txt](./fixtures/empty-success-payload.txt) and [false-completion.txt](./fixtures/false-completion.txt) to reject success without an executed payload.
