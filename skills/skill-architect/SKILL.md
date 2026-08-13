---
name: skill-architect
description: "Use as a passive planning reference for the approved skill-authoring architecture, six concern scope, class boundaries, layout, workflow semantics, dependencies, ownership, and acceptance evidence."
selection:
  role: reference
  tags:
    actions: [architect skill family]
    inputs: [skill architecture question]
    outputs: [passive architecture context]
    topics: [skill ownership, class boundaries, platform layout]
    constraints: [five-class contract, passive reference]
  use_when: [a request needs approved skill-authoring architecture or boundary context]
  not_for: [authoring files, running workflows, or making migration changes]
class: planning
---

# Skill Architect — Approved Passive Scope

This is a **passive planning index**, not an executable workflow or an approval authority.
It publishes one coupled six-concern scope for the approved architecture. The concern
documents describe context; they do not authorize execution, loading, changes, or
completion.

## Six concern documents

- [Taxonomy and ownership map](taxonomy-and-ownership-map.md) — five classes and one canonical owner per approved outcome.
- [Class boundary and loading matrix](class-boundary-loading-matrix.md) — class contracts and asymmetric passive loading.
- [Platform layout and discovery](platform-layout-and-discovery.md) — target locations, entry points, and discovery context.
- [Workflow document semantics](workflow-document-semantics.md) — passive workflow shape and handoff boundary.
- [Dependency direction and non-transitivity](dependency-direction-and-non-transitivity.md) — permitted context direction and authority limits.
- [Migration and acceptance evidence](migration-and-acceptance-evidence.md) — implementation gates and evidence posture.

## Supporting references

- [Class boundary rules](class-boundary-rules.md) — side-effect, delegation, and cross-skill boundary rules.
- [Skill class taxonomy](class-taxonomy.md) — the five valid classes and their passive or executable contracts.
- [Class decision flow](class-decision-flow.md) — descriptive criteria for distinguishing the five classes.
- [Platform layout context](platform-layout-context.md) — historical layout and script-resolution context.
- [Selection profile schema](references/skill-selection-profile.schema.json) — the local metadata schema used by this family.

## Shared contract

The six documents share the coupling rationale that taxonomy, ownership, class
boundaries, layout, workflow meaning, dependency direction, and acceptance evidence
must remain mutually consistent as one passive planning scope. None is a procedure,
tool specification, write authority, delegation contract, implicit load chain, or
completion authority. Passive-contract verification means that this index and every
support document are descriptive reference content only; execution remains owned by
an explicitly selected active skill.
