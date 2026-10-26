---
name: markdown-writing-guide
description: "Use as passive guidance when authoring or substantively revising prose in Markdown or Markdown-like content."
selection:
  role: reference
  tags:
    actions: [review prose, improve prose]
    inputs: [prose requirements, draft prose]
    outputs: [writing quality guidance]
    topics: [Markdown prose]
    constraints: [substantive prose authoring or revision]
  use_when:
    - Substantive prose is authored or revised in Markdown-like content, including structured or specialized formats.
  not_for:
    - Code or non-prose work with no authored prose.
    - Mechanical edits or deterministic rendering that does not author or revise prose.
  supports: [agent-factory, command-factory, generic-analysis, generic-research, proposal, skill-factory, skill-reviewer, plan-writer, breakdown-tasks, task-delegation, dispatch-decompose, generic-executor, task-executor]
class: documentation
---

# Markdown Writing Guide

Use this passive reference when a task asks you to author or substantively revise prose in Markdown or Markdown-like content. Select it because of the prose work, not a `.md` path, artifact type, or skill class.

## Documentation Files

- [Writing quality](reference/writing-quality.md) — reader fit, substance, evidence, specificity, concision, tone, examples, and format fit.
- [Writing methods by task](reference/writing-methods-by-task.md) — optional methods and examples for particular tasks and document forms.

## Keep Local Contracts Authoritative

The owning operation and artifact contract remain authoritative. Preserve required structure, fields, evidence rules, schemas, and meaning; apply this guidance only where compatible to prose actually being authored or substantively revised. Do not impose a general style on unchanged source text or let prose edits change task boundaries.

This skill is passive: it owns no workflow or authority, does not load references automatically or transitively, and does not provide semantic automation. For cross-skill use, load the documentation skill explicitly before relying on it, then read `markdown-writing-guide -> reference/writing-quality.md`.

## Docs

See the [Documentation Files](#documentation-files) listing above for file descriptions.

Base directory for this skill: `file:///home/michael/.config/opencode/skills/markdown-writing-guide`
