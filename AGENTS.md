# OpenCode Global Config

This directory (`~/.config/opencode`) is the **global OpenCode configuration** for this user. Changes here affect OpenCode sessions in every project.

## File Map

| Path                             | Purpose                                                                                                  |
| -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `opencode.json`                  | Main global config: default model, providers, plugins, custom agents, commands, permissions, MCP servers |
| `.opencode/`                     | OpenCode's own runtime support data for this config directory (not usually hand-edited)                  |
| `node_modules/`, `package*.json` | Plugin/runtime dependencies (auto-managed, not hand-edited)                                              |

## Editing Rules

- **Keep `opencode.json` valid JSON** — trailing commas and comments are not allowed (use `.jsonc` extension for those).
- **Use the schema** at `https://opencode.ai/config.json` for validation and autocomplete.
- **Validate JSON/YAML edits with the Python validators when available**:
  - JSON syntax: `uv run --project scripts/python validate-json <file>`
  - JSON schema: `uv run --project scripts/python validate-json <file> --schema <schema-file>`
  - JSON schemas for runbook/state artifacts live in `skills/runbook/schema.json` and `skills/runbook/schemas/`
  - YAML syntax: `uv run --project scripts/python validate-yaml <file>`
- **Never edit `node_modules/`**, `.opencode/node_modules/`, or auto-generated lock files, except updating `scripts/python/uv.lock` through `uv sync --project scripts/python` when Python script dependencies intentionally change.
- **Never commit or hardcode secrets** (API keys, tokens). Use `{env:VARIABLE}` or `{file:~/.path/to/secret}` substitution instead.
- **Preserve existing agent names, model IDs, plugin entries, and fallback model ordering** unless the change explicitly requires modifying them.
- **For new agents** in `agent:`, provide a concise `description` so other agents know when to delegate to it.
- **For new commands** in `command:`, follow the documented template/description/agent/model shape.

## OpenCode Documentation

- Config: <https://opencode.ai/docs/config/>
- Agents: <https://opencode.ai/docs/agents/>
- Commands: <https://opencode.ai/docs/commands/>
- Plugins: <https://opencode.ai/docs/plugins/>
- Permissions: <https://opencode.ai/docs/permissions/>
- Models: <https://opencode.ai/docs/models/>
- Rules/Instructions: <https://opencode.ai/docs/rules/>
- Tools: <https://opencode.ai/docs/tools/>
