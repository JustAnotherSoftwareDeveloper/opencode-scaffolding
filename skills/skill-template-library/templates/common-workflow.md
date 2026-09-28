<!--
Template-only slot declarations. On instantiation, replace every declared slot with
the value from its source below; no slot may remain. Use one Workflow Name value in
both occurrences. Remove this comment from the instantiated workflow; it is not part
of the workflow output.

- Workflow Name (title and metadata line): replace both occurrences with the author-
  supplied name of the practice described by Purpose and Descriptive Sequence.
- optional skill (metadata line): replace with the author-supplied name of a skill
  actually associated with this workflow, or with empty text when none is associated.
- Description (metadata line): replace with an author-supplied brief description of
  the workflow, grounded in the scope described by Purpose.
- one-sentence trigger condition: replace with one sentence stating the intended-use
  condition under which the described practice applies, supplied by the workflow
  author.
- Purpose prompt: replace with one or two author-supplied sentences describing the
  practice's actual outcome and scope.
- Phase 1 Name, Phase 2 Name, and Phase 3 Name: replace each with the author-supplied
  name of that actual phase in the practice's sequence.
- Each phase description: replace with the author-supplied account of that phase's
  actual practice, inputs, outputs, and key decisions.
- Artifacts prompt: replace with a bullet list of actual files, configuration,
  evidence, or state associated with the practice as inputs or outputs, supplied by
  the workflow author.
- Validation Context prompt: replace with a bullet list of actual evidence or
  criteria by which a consuming operation may assess the workflow outcome, supplied
  by the workflow author.
- Prerequisites prompt: replace with a bullet list of the actual context, decisions,
  access, or inputs assumed by the practice, supplied by the workflow author.
- Notes prompt: replace with a bullet list of actual assumptions, boundaries, failure
  modes, or gotchas specific to the practice, supplied by the workflow author.
-->
# `<<Workflow Name>>`

> **Editorial constraint:** Do not use Markdown tables when filling this template. Use bullet lists, definition lists, or subsection headings for structured data.

> **Authority boundary:** This is a passive workflow document. It describes a scoped
> practice for reference only; it is not an executable procedure or a source of
> execution authority.

`<<Workflow Name>>` - `<<optional skill>>` - `<<Description>>`

**Use when:** `<<one-sentence trigger condition>>`

## Purpose

<<1-2 sentences describing what this workflow accomplishes and its scope.>>

## Descriptive Sequence

Describe the practice in sequence. These entries are descriptive context, not
imperative steps, commands, or instructions for the reader to execute.

1. **<<Phase 1 Name>>** — <<description of the practice, its inputs, outputs, and key decisions>>
2. **<<Phase 2 Name>>** — <<description of the practice, its inputs, outputs, and key decisions>>
3. **<<Phase 3 Name>>** — <<description of the practice, its inputs, outputs, and key decisions>>

## Artifacts

<<List of artifacts associated with the practice, including files, configuration,
evidence, or state described as inputs or outputs. This list does not authorize
creating, modifying, or deleting anything. Use bullet points.>>

## Validation Context

<<Describe the evidence or criteria by which a consuming operation may assess the
workflow outcome. This is validation context, not a completion check performed by
this document. Use bullet points.>>

## Prerequisites

<<List required context, decisions, access, or inputs assumed by the described
practice. Do not prescribe tool use or execution. Use bullet points.>>

## Notes

<<Assumptions, boundaries, failure modes, or gotchas specific to this workflow.
Use bullet points.>>

## Operation Handoff

The consuming operation owns the imperative procedure and all execution decisions.
It translates this passive context into its own bounded steps and owns any tools,
writes, delegation, output, and completion validation. This document does not
execute, call tools, modify files, delegate work, load other skills transitively,
grant authority, or establish completion evidence. Any additional reference must
be explicitly loaded by the consuming operation.
