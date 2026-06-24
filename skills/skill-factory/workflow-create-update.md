# Skill Factory — Create and Update Workflows

## Create Workflow

Produce a new skill directory from scratch.

1. Select class per the loaded `skill-authoring-guide` frontmatter rules.
   Copy the matching template from the loaded `skill-template-library`.
2. Write YAML frontmatter with exactly three fields: `name`, `description`, `class`.
   - `name` is the skill directory name.
   - `description` starts with "Use when ".
   - `class` is one of: operation, planning, documentation, delegated, inline, orchestrated.
3. Draft body content following editorial conventions from the loaded `skill-authoring-guide`.
   - Use imperative voice, active voice.
   - Write one sentence per line.
   - Use Title Case for H1 and H2 headings.
4. Write a thin procedural body with: trigger guidance, step-by-step workflow, quality rules, validation checklist, expected output.
   - Reference the loaded documentation skills by name for depth — never by file path.
5. For operation-class skills: include "Normalize Input" as the first procedural step after the H1 intro.
6. For documentation-class skills: the body contains structured reference data (schema, field definitions, conventions) with no execution steps, no tool invocations.
7. For planning-class skills: the body contains decision frameworks, taxonomy rules, and boundary definitions.
8. For orchestrated-class skills: follow the 7-section layout from `skill-orchestration-reference`.
9. For delegated-class and inline-class skills: follow the template structure from `skill-template-library`.
10. Do not add optional sections (examples, gotchas, extended descriptions).
11. Add a `## Docs` section as the final section.
    Content: `See \`./reference/README.md\` for documentation of supporting files.`
12. Verify manually — see Validation section below.

## Update Workflow

Edit one or more files in an existing skill directory.

1. Load relevant documentation skills:
   - Load `skill-maintenance-reference` for update workflow reference, migration guide, and validation checklist.
   - Load `skill-authoring-guide` for editorial conventions needed during edits.
2. Read every existing file under `skills/<name>/`: SKILL.md, reference/*, templates/*, schemas/*, snippets/*.
3. Determine which files the request targets from DETAILS or user instructions.
4. For each targeted file:
   - Read its full current content.
   - Apply targeted edits — do not rewrite the entire file unless explicitly requested.
   - Preserve existing frontmatter, structure, and prose outside the edit scope.
5. If creating a new supporting file (e.g., a new reference or template), write it following conventions from `skill-authoring-guide` and matching templates from `skill-template-library`.
6. Re-validate all modified files against the Validation section below.

## Validation

**Shape checks:**
- YAML frontmatter is valid and contains exactly `name`, `description`, `class`.
- `name` matches the skill directory name.
- `description` begins with "Use when ".
- `class` is a valid OpenCode class.
- One H1 per file; all subsections are H2 or deeper.
- All headings use Title Case.

**Voice and wording:**
- Step descriptions begin with an imperative verb.
- No passive-voice constructions in step bodies.
- Sentences are commands, not observations (except factual definitions in reference files).
- No hedging words ("should", "may", "could", "might", "try", "best", "recommend") in instructions.
- No fluff words ("please", "simply", "just", "obviously", "essentially", "basically").
- No tutorial language — no concept explanations, no background justifications, no choice rationales.

**Reference discipline:**
- Reference detail is not inlined — cross-references via loaded skill names instead.
- No external file paths to other skill directories appear.
- Cross-skill interaction uses skill loading only, never file paths.

**Formatting:**
- One sentence per line.
- No trailing whitespace.
- No tables for simple rule-to-scope mappings (use bullet lists).
- List nesting limited to two levels.
- Minimal inline formatting — no bold entire sentences, no combined inline styles on one line.

**UPDATE-specific checks:**
- Existing content not silently deleted — every edit preserves surrounding context.
- Update path references current file content, not assumed content.
- Targeted edits are scoped to the request — no unrelated sections modified.