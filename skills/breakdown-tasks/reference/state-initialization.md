# State File Initialization

Procedure for initializing the task-decomposition state file.

## Directory Location

- **Path:** `~/.config/opencode/.tasks/`
- **Behavior:** Create the directory if it does not exist.

## Filename Derivation

The state file uses the naming pattern: `<epoch>-decomposition.json`

Where:

- **epoch:** Unix timestamp (seconds since Unix epoch) captured at the start of decomposition.
- **decomposition:** Fixed suffix used for all state files.

## Collision Behavior

If the derived filename already exists in `.tasks/`:

1. Increment the epoch value and retry.
2. Retry up to 10 candidate filenames.
3. If all attempts collide or file creation fails, emit `BLOCKED:` and halt.

State files are created with exclusive file creation, so existing files are never overwritten during concurrent decomposition runs.

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

Set `STATE_FILE=~/.config/opencode/.tasks/<epoch>-decomposition.json` for internal pipeline commands.
Return `.tasks/<epoch>-decomposition.json` to the delegator as the relative output path.
