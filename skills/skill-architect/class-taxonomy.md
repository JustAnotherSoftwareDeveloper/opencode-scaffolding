# Skill Class Taxonomy

Every `SKILL.md` has a `class` field in its frontmatter.
Exactly six classes are valid.
No other classes are valid.
If uncertain, lean toward `operation`.
If the skill is a passive data store consumed by other skills, choose `documentation`.

## operation

**Template**: `./templates/operation.SKILL.template.md`

Broad/default class for single bounded procedures that are independent, self-validating, and do not sub-delegate.
A Normalize Input step absorbs free-form input, structured packets, files, or tool outputs into one internal input, avoiding separate modes for different invocation shapes.

- **Side effects**: Yes (file writes, tool calls).
- **Delegation**: Does not sub-delegate.
- **Execution steps**: Yes — numbered prefixes define the workflow.

Script invocation: Operation skills are the natural home for script-calling procedures.
When a step involves deterministic, repeatable, or token-intensive work, replace or augment the LLM step with a script invocation step.
The skill's procedure defines the orchestration around the script call — input preparation, invocation, output parsing, and validation.
Script invocation does not change the skill class.

## delegated

**Template**: `./templates/delegated.SKILL.template.md`

Receives delegation packets and performs bounded subtasks within a pipeline or orchestration.
Includes final workers and workflow stages (including decomposers) invoked by a delegator.

- **Side effects**: Yes (file writes, tool calls).
- **Delegation**: Participates in delegation pipelines as a subtask receiver.
- **Execution steps**: Yes — numbered prefixes define the workflow.

## inline

**Template**: `./templates/inline.SKILL.template.md`

Single-pass reasoning-heavy skill executed directly by the main agent.
Optional direct tool calls.
No worker or sub-skill orchestration as its own workflow.

- **Side effects**: Yes (file writes, tool calls).
- **Delegation**: Does not sub-delegate.
- **Execution steps**: Yes — numbered prefixes define the workflow.
- **Lifetime**: Ephemeral — load it for one reasoning pass, then discard.

## orchestrated

**Template**: `./templates/orchestrated.SKILL.template.md`

Coordinates sub-skills, workers, phases, or quality gates.
Uses the 7-section canonical layout: Frontmatter, Purpose/Intro, Execution Steps, Worker Strategy, Verification Checklist, Self-Validation, Cross-References.

- **Side effects**: Yes (file writes, tool calls, worker dispatch).
- **Delegation**: Owns sub-delegation and result collation.
- **Execution steps**: Yes — numbered prefixes define the workflow.

## planning

**Template**: `./templates/planning.SKILL.template.md`

Reference sources loaded during planning or architecting activities (formal plan creation, informal discussion, design review, onboarding, code review).
Documents structural knowledge about the codebase.

- **Side effects**: Must not produce side effects, modify files, or invoke tools.
- **Delegation**: Does not sub-delegate.
- **Execution steps**: Defines none — uses passive content sections instead.
- **Purpose**: Answers "what exists, how it fits together, and what constraints apply" — not "what steps do I execute."

## documentation

**Template**: `./templates/documentation.SKILL.template.md`

Passive data store for domain-shared reference content (docs, schemas, templates).
Consumed by other skills via relative-path references.

- **Side effects**: No side effects, no execution steps.
- **Delegation**: Does not sub-delegate.
- **Execution steps**: Defines none — uses passive content sections instead.
- **Primary consumer**: Other skills that load this skill for its reference data.

## Class Selection Rationale

Each of the six classes has a distinct contract for side effects, delegation, and output shape, enabling the agent to load the correct behavior without ambiguity.
A skill whose behavior spans multiple classes must be split or rewritten.
Hybrid classes are not supported.

Templates enforce structural consistency and reduce authoring errors (missing sections, wrong step prefixes).
Template divergence requires coordinated updates across all templates.