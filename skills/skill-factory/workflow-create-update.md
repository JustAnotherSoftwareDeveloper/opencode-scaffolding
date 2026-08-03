# Skill Factory Create And Update Workflow

## Create And Update Workflow

1. Identify the owned request, class, inputs, outputs, and nearest neighbors.
2. Write only the current `name`, `description`, `selection`, and `class` profile.
3. Set `selection.role` and the smallest sufficient grouped tag set.
4. Add `aliases`, `use_when`, `not_for`, or `supports` only when they clarify direct selection.
5. Preserve the body and update relevant examples with the current profile.
6. Validate the profile and Markdown syntax.

## Validation

- Confirm YAML parses and the class is valid.
- Confirm every profile has a valid role and at least one non-empty tag group.
- Confirm every tag and condition is task-grounded, discriminative, concise, stable, discoverable, and scoped.
- Confirm `supports` targets resolve against the active collector inventory.
- Confirm direct semantic selection uses the collector snapshot without a secondary ranking path.
- Run `bun run --cwd ~/.config/opencode/scripts/node lint:md -- <path>` for every modified Markdown file.
- Search modified documentation for obsolete count, popularity, implementation, and metadata-shape guidance.
