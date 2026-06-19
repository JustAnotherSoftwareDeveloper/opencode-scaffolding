---
name: skill-architect
description: "Use when planning or architecting OpenCode skills."
class: planning
---

# Skill Architect — Domain Planning Reference

Planning context for designing OpenCode skills using the skill-writer conventions.
See `./REFERENCE.md` for class rules and frontmatter requirements.

## When to Use

- Load during a new skill planning session (e.g., defining scope, class, and interfaces for a proposed skill) to anchor decisions in existing platform conventions.
- Load when reviewing a pull request or proposal that creates or modifies an OpenCode skill (`skills/<name>/SKILL.md`) to verify class selection, frontmatter correctness, and structural compliance.
- Load during onboarding to skill-authoring workflows to understand the skill class taxonomy, template selection rules, and progressive disclosure pattern without reading the full skill-writer reference.
- Load before writing an ADR for a platform-level skill architecture decision (e.g., shared skill contracts, cross-skill coordination patterns) to ensure consistency with established design invariants.

## Decision Records

- **Class selection model**: Every skill maps to exactly one of five classes (operation, delegated, inline, orchestrated, planning). Rationale: each class has a distinct contract for side effects, delegation, and output shape, enabling the agent to load the correct behavior without ambiguity. Trade-off: a skill whose behavior spans multiple classes must be split or rewritten; hybrid classes are not supported.
- **Frontmatter-driven discovery**: The agent selects a skill by matching its `description` field against the current task context, not by structural indexing. Rationale: string matching is fast, deterministic, and requires no external index. Trade-off: generic descriptions cause false-positive loads; descriptions must be precise and trigger-specific (action + domain + qualifier).
- **Progressive disclosure pattern**: SKILL.md contains only procedural body and cross-references; depth material lives in REFERENCE.md and reference/*.md. Rationale: keeping SKILL.md under 100 lines reduces token overhead during loading; the agent fetches depth on demand. Trade-off: authors must maintain two files per skill and ensure cross-references stay accurate.
- **Template-driven authoring**: Each class has a canonical template under templates/<class>.SKILL.template.md. Rationale: templates enforce structural consistency and reduce authoring errors (missing sections, wrong step prefixes). Trade-off: template divergence requires coordinated updates across all templates.

## Constraints & Assumptions

- A skill owns exactly one directory under `skills/<name>/` with an entry point at `SKILL.md`. Support files (REFERENCE.md, reference/) share the same directory but are never loaded automatically by the agent.
- Skill names must match `^[a-z][a-z0-9-]*$` and match the directory name exactly. Renaming a published skill breaks all existing references and discovery.
- The agent only reads the `description` field for skill selection. Filenames, directory structures, and internal content do not influence discovery.
- Planning skills are read-only reference contexts. They do not produce side effects, modify files, invoke tools, or define execution steps.
- Skill versioning is not supported. Each skill directory holds one live version; archived versions live under `archive/<name>/SKILL.md` for shape reference only.

## Verification Criteria

- Frontmatter contains exactly three keys (`name`, `description`, `class`) and is valid YAML.
- `name` matches the directory name under `skills/`.
- `description` starts with `"Use when"` and captures a specific trigger intent (action + domain + qualifier).
- `class` is one of the five allowed values and matches the template used.
- Every section in the planning artifact contains domain-specific content, not template scaffolding.
- Body contains no procedure steps, no tool invocation instructions, and no examples section.
- Reference detail is not inlined — cross-references point to `./REFERENCE.md` or `./templates/` instead.
- File is under 200 lines with one sentence per line and Title Case headings.
