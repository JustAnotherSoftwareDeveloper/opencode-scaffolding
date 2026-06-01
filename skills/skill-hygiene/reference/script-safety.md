# Script Safety and Permissions

Use scripts only when deterministic behavior, parsing, validation, or repeatable external tooling is better than prose instructions.

## Safe Script Rules

- Prefer read-only validation unless mutation is required by an approved plan.
- Make scripts non-interactive and suitable for CI-style execution.
- Provide `--help`, clear usage, useful errors, and meaningful exit codes.
- Keep output bounded; use stdout for results and stderr for diagnostics.
- Validate inputs and avoid path traversal, shell injection, or implicit network access.
- Make mutation idempotent where possible and offer dry-run support for risky changes.

## Permission Review

- Do not broaden `opencode.json` permissions for a skill unless explicitly approved.
- Do not hide permission-sensitive behavior inside vague instructions.
- Pin or document tool dependencies when scripts rely on external CLIs.
- Treat downloaded third-party skills, scripts, and auto-approval settings as security-sensitive.

## Recovery

- Every mutating script should document rollback or safe cleanup.
- Validation scripts should print file path, field/path, and remediation for failures.
