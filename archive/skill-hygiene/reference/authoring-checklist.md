# Skill Authoring Checklist

Use this checklist when drafting or reviewing any new framework-authored skill.

## Scope

- The skill addresses repeated work or specialized local knowledge.
- The skill has one clear primary job and a short list of explicit non-goals.
- The selected class matches the actual behavior:
  - `operation`: small and independently verifiable.
  - `orchestrated`: procedural coordinator that delegates/works through workers; does not execute worker tasks directly, only coordinates state/quality gates/failure handling.
  - `delegated`: worker-executed backing specialist spawned by an orchestrator with explicit input/output contracts.
  - `planning`: artifact/lifecycle creation or review.
- The skill does not duplicate always-on agent prompts or base model knowledge.

## Frontmatter

- `name` matches `skills/<name>/`.
- `description` is specific, action-oriented, and under 1024 characters.
- `class` is one of `operation`, `orchestrated`, `delegated`, or `planning` for framework-authored skills.
- Optional frontmatter stays compatible with OpenCode conventions.

## Body

- The first section tells agents when and why to use the skill.
- Instructions are imperative and operational, not personality claims.
- Defaults are preferred over long menus of options.
- Gotchas and recovery paths are included where failure is common.
- Required output formats and validation commands are explicit.

## Progressive Disclosure

- Keep `SKILL.md` compact enough to load without bloating context.
- Move long references to `reference/` and deterministic helpers to `scripts/`.
- Reference supporting files by relative path and say when to read them.

## Review

- Test with positive trigger requests and near-miss negative requests.
- Compare with-skill vs without-skill behavior for nontrivial skills.
- Check that permissions and shell commands are no broader than necessary.
- Confirm no existing skills were migrated unless the approved plan requires it.
