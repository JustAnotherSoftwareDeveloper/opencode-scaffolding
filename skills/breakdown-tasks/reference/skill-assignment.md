# Skill Assignment Procedure

Use one frozen inventory with one explicit assignment mode.
Treat generated assignments as authoritative.

## Prerequisites

- Provide a root `{summary, tasks}` object that matches `schema/task-input.schema.json`.
- Omit `skills` from every task draft.
- Collect one operation and documentation inventory from the caller root.
- Preserve the inventory through generation, audit, and validation.

## Qwen Mode

1. Validate the complete draft and frozen inventory before model initialization.
2. Validate every inventory source and resolved path against its declared root.
3. Render every complete task field in stable order.
4. Render candidate name, description, normalized tags, and class.
5. Exclude candidate source and path from model text.
6. Count every complete pair with the pinned tokenizer.
7. Reject any pair above 8,192 tokens before HTTP access.
8. Score every candidate sequentially with the checked local Qwen profile.
9. Stable-sort finite scores by descending value and original inventory order.
10. Select the top candidate.
11. Select ranks two and three only at scores greater than or equal to `0.8`.
12. Mark a top score below `0.8` as forced low confidence.
13. Publish only names supplied by the frozen inventory.

## Shadow Mode

1. Run the same Qwen validation and scoring path.
2. Require an atomic diagnostics file.
3. Publish lexical rollback assignments.
4. Record the Qwen comparison without mutating the packet after generation.
5. Abort task publication when diagnostics publication fails.

## Lexical Rollback Mode

1. Use lexical mode only through an explicit rollback decision.
2. Reuse the frozen inventory.
3. Skip manifest, tokenizer, and Ollama initialization.
4. Preserve zero-to-three historical schema compatibility.

## Read-Only Audit

1. Reuse the Phase B inventory.
2. Verify canonical names and inventory membership.
3. Verify semantic fit, atomicity, circular references, and cross-task consistency.
4. Block invalid assignments.
5. Do not add, remove, reorder, or replace generated assignments.

## Output

- Write one schema-valid `BreakdownTasksOutput` object.
- Preserve every non-skill draft field.
- Keep one to three assignments in Qwen mode.
- Keep zero to three assignments in lexical and historical packets.
- Return the relative generated task path.
