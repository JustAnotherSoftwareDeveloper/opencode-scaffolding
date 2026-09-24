---
name: skill-script-python-writer
description: "Use when creating or editing deterministic Python scripts under scripts/python/, including CLI entry points, libraries, registration, and implementation-coupled tests."
selection:
  role: owner
  tags:
    actions: [create Python script, edit Python script]
    inputs: [Python script requirements, existing Python script]
    outputs: [Python implementation, project registration]
    topics: [script implementation, script maintenance]
    constraints: [deterministic implementation]
  use_when: [a Python script must be created or an existing Python script implementation must be modified]
  not_for: [test-only work that does not change the Python implementation]
class: operation
---

# Skill Script Python Writer

Create or edit one deterministic Python script implementation under `scripts/python/`.
Own the implementation lifecycle for the selected script: CLI, library code,
dependencies, registration, and directly coupled regression tests when they are needed
to verify an implementation change. Test-only creation or maintenance belongs to
`skill-script-python-test-writer`.

## Normalize Input

Map invocation context to one internal input object. Infer create versus edit from the
request and repository state; do not require a separate mode flag.

Capture these fields:

- **Script identity** — Kebab-case entry point name or an existing script path/name.
- **Requested result** — The implementation behavior to create, fix, refactor, or otherwise change.
- **Input contract** — CLI arguments, stdin format, or file paths the script reads, including which parts must remain compatible.
- **Output contract** — stdout format, exit codes, stderr behavior, including which parts must remain compatible.
- **Dependencies** — Existing or required Python packages.
- **Skill consumers** — Skills or workflows that invoke the script when relevant.

For a new script, require enough information to establish its purpose and interface.
For an existing script, read the current implementation and use it as the baseline;
only require clarification when the requested change cannot be determined safely from
the request and repository evidence.

`BLOCKED: Missing script identity — provide or identify the Python script to create or edit.`
`BLOCKED: Missing requested result — describe the implementation behavior to create or change.`

## Procedure

Each step is one imperative action. Do not delegate sub-tasks.

1. **Resolve the script and baseline.** Determine whether the requested script already
   exists. For an edit, read the existing CLI, library modules, registration,
   dependencies, paired tests, and materially relevant shared modules before changing
   anything. For a create, confirm the target does not conflict with an unrelated
   existing entry point. Follow `./reference/path-conventions.md`.

2. **Implement the requested result.** Create missing implementation files or edit the
   existing implementation as required. Preserve unrelated behavior and public
   interfaces unless the request requires changing them.
   - CLI entry points live at `src/cli/<script_name>.py` and follow
     `./reference/cli-conventions.md`.
   - Library code lives under `src/lib/<script_name>/` and follows
     `./reference/python-style-guide.md` and `./reference/shared-lib-rules.md`.
   - Prefer `pathlib.Path`, typed signatures, shared library helpers, deterministic
     output, and the repository's existing conventions.

3. **Reconcile dependencies and registration.** Add, update, or remove dependencies
   only when required by the implementation. Create or update the `[project.scripts]`
   entry and hatchling package configuration only when the requested implementation
   requires it. Do not duplicate existing registration or rewrite unrelated
   `pyproject.toml` content.

4. **Maintain implementation-coupled tests.** Create or edit paired unit/CLI tests
   when the implementation change requires regression coverage or an existing test
   must change to reflect the requested behavior. Keep this work limited to tests that
   directly verify the implementation result. Route independent test-suite-only work
   to `skill-script-python-test-writer`.

5. **Run validation.** Format and lint changed Python files, type-check the affected
   implementation, run the relevant tests and coverage checks, and verify the CLI
   entry point when applicable. Remediate failures that remain within the requested
   implementation scope. Return `BLOCKED` only when a concrete unresolved dependency,
   contradiction, or external decision prevents the requested implementation result.

## Validation

Use the strongest checks applicable to the changed script rather than assuming every
script has identical files:

- Format changed Python files with `uv run ruff format`.
- Lint changed implementation and coupled test files with `uv run ruff check`.
- Type-check affected implementation with `uv run pyright` using the project config.
- Run the relevant pytest targets; run project coverage enforcement when the affected
  package participates in the configured coverage gate.
- For a registered CLI, verify `uv run --project ~/.config/opencode/scripts/python <script-name> --help` exits zero.

Do not require creation of files that the selected script architecture does not need.
Do not weaken existing validation or coverage requirements merely to make an edit pass.

## Expected Output

A created or updated Python script implementation under `scripts/python/`, including
only the files required by the requested result. Typical affected files include:

- `src/cli/<script_name>.py`
- `src/lib/<script_name>/__init__.py`
- `src/lib/<script_name>/core.py` or other existing package modules
- `tests/test_<script_name>.py`
- `tests/test_<script_name>_cli.py`
- `pyproject.toml`

Report which files were created versus edited, which interfaces or registrations
changed, and the validation actually run.

## Self-Validation

- [ ] Existing implementation was read before an edit.
- [ ] The requested implementation result is complete without unrelated rewrites.
- [ ] Public behavior was preserved unless the request explicitly changed it.
- [ ] Dependencies and registration match the resulting implementation without duplicates.
- [ ] Coupled tests were created or edited only when needed for the implementation result.
- [ ] Formatting, lint, type checks, relevant tests, and applicable CLI verification were run or truthfully reported as blocked.
- [ ] Test-only work was not claimed as implementation ownership.

## Docs

See `./reference/README.md` for the reference file index.
