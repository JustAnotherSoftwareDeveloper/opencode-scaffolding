---
name: generic-analysis
description: "Use as a fallback generic analysis/execution skill when no more specific skill matches the task domain. Provides a very loose guideline for task execution."
tags: [fallback, generic-task, catch-all, last-resort]
class: operation
---

# Generic Analysis

This is a **fallback** operation-level skill. Use it only when no other skill in the index matches the task domain.

## Role

Provide a minimal procedural framework for tasks that lack a dedicated skill. The delegation packet's PURPOSE, DETAILS, and EXECUTION INSTRUCTIONS sections are the sole authoritative directives — this skill does not impose any additional requirements, constraints, or procedures beyond what the packet already defines.

## Boundaries

- **Authority**: The delegation packet is always authoritative. This skill adds no requirements.
- **No override**: Nothing in this skill overrides, augments, or constrains the packet's instructions.
- **Minimal guidance**: Use the packet's sections as-is. Follow EXECUTION INSTRUCTIONS step by step. No extra workflow is defined here.
