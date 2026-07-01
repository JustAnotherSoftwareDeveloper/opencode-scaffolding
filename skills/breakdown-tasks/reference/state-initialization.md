# State File Initialization

Deterministic procedure for deriving and initializing the task-decomposition state file.

## Directory Location

- **Path:** `~/.config/opencode/.tasks/`
- **Behavior:** Create the directory if it does not exist.

## Filename Derivation

The state file uses the naming pattern: `<epoch>-<slug>.json`

Where:

- **epoch:** Unix timestamp (seconds since Unix epoch) captured at the start of decomposition.
- **slug:** URL-safe truncation of the request summary (max 64 characters).
  - Sanitization: Convert to lowercase.
    Replace non-alphanumeric characters with hyphens.
    Trim leading/trailing hyphens.
  - If the resulting slug is empty after sanitization, use `decomposition` as the fallback value.

## Collision Behavior

If the derived filename already exists in `.tasks/`:

1. Emit `BLOCKED: State file <path> already exists — remove manually or wait for next epoch second.`
2. Halt execution immediately.

This ensures no state file is accidentally overwritten during concurrent decomposition runs.

## Initial State Structure

Initialize the file with a JSON object containing:

- `summary`: Empty string placeholder (to be populated in Step 2).
- `tasks`: Empty array (to be populated in Step 3).

Example initial content:

```json
{ "summary": "", "tasks": [] }
```

## Retention Policy

The `.tasks/` directory is ephemeral working state.

- Files may be cleaned after the workflow completes.
- Files may be retained for debugging at the operator's discretion.
- This is internal state, not output to downstream workers.

## Environment Variable

Set `STATE_FILE=~/.config/opencode/.tasks/<derived-filename>.json` for use throughout the pipeline.