# Function Naming

Follow these naming conventions:

- **Script-level functions** — Lowercase snake_case.
  Example: `parse_args()`, `validate_input()`.
- **Library functions** — Lowercase snake_case with library namespace prefix.
  Example: `io::read_json()`, `git::current_branch()`.
- **Constants** — Uppercase with `readonly`.
  Example: `readonly SCRIPT_DIR`, `readonly EXIT_SUCCESS`.
- **Private functions** (within script) — Prefixed with `_`.
  Example: `_validate_path()`, `_normalize_input()`.