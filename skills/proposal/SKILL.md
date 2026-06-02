---
name: proposal
description: Create a bounded proposal before planning or execution, covering scope, alternatives, risks, and acceptance criteria. For deep proposals, use delegated worker-lane exploration and analysis to gather source-backed evidence before drafting.
---

# Proposal Skill

Use this skill before planning or editing when the requested outcome is non-trivial, ambiguous, or likely to affect agents, skills, commands, permissions, state, or orchestration behavior.

## Explore / Analyze / Specify Framing

Proposal mode is a **decision-artifact** workflow, not an implementation or execution plan. For deep or architecture-sensitive proposals, this workflow decomposes into three phases:

1. **Explore** — Launch bounded worker-lane exploration (local, historical, external) to gather source-backed facts about the current state, prior decisions, and relevant references.
2. **Analyze** — Delegate at least one bounded analysis lane (delegation-pattern, adversarial/gap, synthesis) to produce tradeoffs, risks, contradictions, framework-fit assessment, and decision impact.
3. **Specify** — Resolve blocking ambiguity with `[NEEDS CLARIFICATION: ...]` markers, express acceptance criteria as independently testable statements (optionally with Given/When/Then scenarios), and decide whether to revise, supersede, or create a new proposal artifact.

Light and standard proposals may skip one or more phases and rely on minimal local discovery. Deep proposals should run all three phases before drafting.

## Artifact Contract

Proposal artifacts live at:

```text
.proposals/<unix-timestamp>-slug/INDEX.md
```

- `<unix-timestamp>` is seconds since epoch at artifact creation time.
- `slug` is lowercase, hyphen-separated, and human-readable.
- The current proposal file stem becomes the proposal directory name.
- `INDEX.md` is a table of contents only: no YAML frontmatter, status, source request, decision body, summaries, or duplicated section prose.
- `metadata.md` owns proposal frontmatter and status metadata.
- Each canonical proposal section lives in its own markdown file inside the proposal directory.
- Existing historical `.proposals/*.md` proposal files remain valid read-only artifacts; do not migrate, rewrite, move, or split them unless a future accepted proposal explicitly authorizes migration.
- Preserve the original timestamp and slug when updating an existing directory proposal unless superseding it is explicitly intended.

## Lifecycle

1. **Classify intent and depth**: Determine proposal depth tier and intent classification before drafting.
2. **Explore** (deep): Decompose discovery into bounded worker-lane roles; launch lanes per the depth-tier lane matrix; record evidence in the ledger.
3. **Analyze** (deep): Delegate bounded analysis lanes; synthesize findings into decision-ready tradeoffs, risks, and impact.
4. **Specify**: Resolve blocking ambiguity with clarification markers; draft acceptance criteria as independently testable statements.
5. **Create or update artifact**: Write the proposal workspace to `.proposals/<unix-timestamp>-slug/INDEX.md` plus `metadata.md` and canonical section files.
6. **Run embedded critique**: Delegate critique to an appropriately sized `worker-*` worker with review-mode instructions and record findings directly in the proposal.
7. **Revise**: Incorporate user feedback and critique into the same proposal artifact.
8. **Decision**: Mark the proposal `accepted`, `needs-clarification`, `rejected`, or `superseded`.
9. **Return summary**: Report artifact path, status, key tradeoffs, and the next user decision.

## Routing

Worker sizing and escalation are governed by the `delegation` skill, which is the **canonical source of truth** for the configured worker matrix, dynamic sizing, and handoff packet construction. This skill describes lane intent; it does not duplicate the worker matrix.

| Work | Worker Family | Purpose |
| --- | --- | --- |
| Local discovery | `worker-*` with generic-mode instructions | Inventory files, conventions, and constraints |
| External research | `worker-*` with web-research-mode instructions | Gather current source-backed information |
| Proposal drafting and revision | `worker-*` with documentation-mode instructions | Write clear proposal prose |
| Embedded critique | `worker-*` with review-mode instructions | Identify gaps, risks, and acceptance problems |

Choose the smallest capable worker size for each bounded task. Escalate only when scope, ambiguity, or risk requires it. See the **Delegated Analysis Contract** section for deep-proposal lane sizing guidance.

## Proposal Artifact Format

Use the shared proposal workspace skeleton at:

```text
templates/proposal-workspace/
```

Create `.proposals/<unix-timestamp>-slug/`, copy the files from `templates/proposal-workspace/`, fill all placeholders, and preserve the canonical file map unless the proposal explicitly requires a justified deviation. Keep `INDEX.md` as a table of contents only. Put metadata/frontmatter in `metadata.md` and detailed content in section files.

`templates/proposal-template.md` is retained only as a legacy reference for historical single-file proposals. Do not use it for new proposals unless recovering or reading an existing `.proposals/*.md` artifact.

## Section Guidance

- **Goal**: Restate the outcome and what success means.
- **Intent Classification**: Classify work type, risk, needed research, needed discovery, and whether user choices are required.
- **Current State**: Summarize discovered facts, exact files, conventions, and constraints.
- **Problem / Opportunity**: Explain the pain or improvement target.
- **In Scope / Out of Scope**: Draw explicit boundaries.
- **Recommended Approach**: State the preferred path and why it is the smallest correct direction.
- **Alternatives Considered**: Compare viable alternatives and explain why they are not preferred.
- **Artifact and State Impact**: Identify files, artifact paths, and state areas that will be created or modified later.
- **Delegation Model**: Identify worker families, skills, and review approach at a high level; detailed steps belong in a plan.
- **Risks and Unknowns**: Capture uncertainty, compatibility concerns, permission concerns, state drift, and user choices.
- **Discovery Evidence Ledger** (deep): Record source-backed findings with lane, source, claim/fact, inference, assumption, confidence, relevance, fit caveat, and decision impact.
- **Delegated Analysis Summary** (deep): Record tradeoffs, risks, contradictions, framework-fit assessment, and recommended decision impacts from analysis lanes.
- **Embedded Quality Check**: Record critique directly in this proposal artifact.
- **Acceptance Criteria**: Provide independently verifiable checks; use Given/When/Then scenarios when behavior is involved.
- **Decision**: Record current status, decision maker when known, and next action.

## Proposal Depth Tiers

Use the following depth tiers to determine the appropriate level of effort:

| Depth | When to use | Discovery needed | Research needed | Planning notes |
| --- | --- | --- | --- | --- |
| `none` | Trivial/direct execution; no proposal needed | None | None | Direct execution without proposal |
| `light` | Narrow, low-risk change with a short proposal | Minimal local check (file existence, constraints) | None | No formal handoff required |
| `standard` | Normal non-trivial harness/product/code change | Local discovery of files, constraints, and conventions | Optional, for syntax/config conventions or comparable examples | Handoff section required |
| `deep` | Ambiguous, architecture-sensitive, high-risk, or cross-cutting change | Parallel local analysis/research to stabilize understanding | External research as needed for standards or breaking changes | Full handoff with traceability into plan gates |

Use `none` for trivial tasks (e.g., typo fixes, surface changes). Use `light` for narrow changes in one file. Use `standard` for normal non-trivial work. Use `deep` for architecture-sensitive or harness-wide changes.

## Worker-Lane Topology

Explorer and analyst lanes are **proposal-phase roles** implemented with existing `worker-*` tiers, relevant skills, and bounded handoff packets. They are **not new agents** and do not require new agent configurations. The `delegation` skill governs which worker size and family routes each lane.

| Lane | Purpose | Typical worker size |
| --- | --- | --- |
| Local explorer | Inventory current harness files, commands, skills, conventions, and constraints. | `worker-sm` / `worker-md` |
| Historical explorer | Inspect prior proposals, plans, runbooks, state, and lessons for related decisions or conflicts. | `worker-sm` / `worker-md` |
| External reference explorer | Research one external source per lane with cited facts and fit caveats. | `worker-md` / `worker-lg` |
| Delegation-pattern analyst | Map external delegation concepts onto `worker-*` tiers and the `delegation` skill. | `worker-md` / `worker-lg` |
| Adversarial / gap analyst | Challenge assumptions, detect contradictions, shallow evidence, and plan leakage. | `worker-md` / `worker-lg`; escalate to `worker-xl` for high stakes. |
| Synthesis analyst | Merge lane outputs into proposal-ready decisions, risks, and acceptance criteria. | `worker-lg` |
| Embedded review analyst | Apply `review-work` and proposal quality checks before user decision. | `worker-sm` through `worker-xl` |

## Depth-Tier Lane Matrix

| Lane | `light` | `standard` | `deep` |
| --- | --- | --- | --- |
| Local explorer | Recommended if local facts unknown | Recommended | Required when local harness/code impact exists |
| Historical explorer | Optional | Optional | Required when similar artifacts or prior policy exist |
| External reference explorer | Not needed | Optional | Required when external frameworks are cited |
| Delegation-pattern analyst | Not needed | Not needed | Required for harness-routing / workflow changes |
| Adversarial / gap analyst | Not needed | Not needed | Required for core workflow changes |
| Synthesis analyst | Not needed | Not needed | Required when three or more lanes were launched |
| Embedded review analyst | Not needed | Recommended | Required |

Light and standard proposals must not be forced through the full deep analyst topology. Use the matrix above to select lanes proportionally.

## Lane Packet Contract

Each delegated lane uses a bounded handoff packet constructed via the `delegation` skill. The packet is the **input contract** for the worker; the evidence ledger is the **proposal artifact output** that records what the orchestrator accepted.

Every lane packet must include:

- **Objective**: One clear, bounded objective for the lane.
- **Source / file boundaries**: Exact files, paths, or URLs in scope.
- **Out-of-scope**: Files, URLs, or behaviors explicitly excluded.
- **Output contract**: Required return format (facts, inferences, assumptions, confidence, caveats, decision impact).
- **Evidence format**: How findings should be recorded (markdown table, bullet list, etc.).
- **Assumptions policy**: State any assumptions the worker may make; flag if uncertain.
- **Do / do-not rules**: Explicit boundaries, including proposal-only guardrails (no dependency graphs, no task breakdowns, no runbook state, no implementation planning).

Workers should return structured findings rather than broad narrative summaries. See the support reference for full packet examples.

## Evidence Ledger

Record accepted worker findings in a markdown table within the proposal artifact's Discovery Results section. Use the following fields:

| Field | Description |
| --- | --- |
| `Lane` | Lane name (e.g., Local explorer, External reference explorer) |
| `Worker` | Worker family and size used |
| `Source` | File path, URL, or artifact reference |
| `Claim / Fact` | The observed or reported finding |
| `Inference` | Any inference drawn by the worker or orchestrator |
| `Assumption` | Any assumption made, with rationale |
| `Confidence` | High / Medium / Low |
| `Relevance` | Why this finding matters to the proposal decision |
| `Fit Caveat` | Limitations, transferability concerns, or source staleness |
| `Decision Impact` | How this finding influences the recommended approach |

Workers should populate evidence rows during their lane work; the orchestrator selects which rows to include in the final ledger. External-source facts should be refreshed during planning if they become implementation-critical.

## Delegated Analysis Contract

Treat analysis as distinct from raw discovery. Deep proposals should delegate at least one bounded analysis lane when the request involves architecture, harness-wide workflow changes, external-framework adoption, or high downstream cost.

Analysis lanes return:

- **Tradeoffs**: Comparisons between viable approaches, including cost, risk, and downstream impact.
- **Risks**: Identified risks with severity and mitigation, separate from the proposal's own risk section.
- **Contradictions**: Conflicts between findings, assumptions, or prior decisions.
- **Framework-fit assessment**: How well an external concept maps to this harness's workers and skills.
- **Decision impact**: Explicit recommendation on how the analysis should influence the chosen approach.

Synthesis merges multiple lane outputs into a coherent decision model. When three or more lanes were launched, a synthesis analyst lane is required to merge findings into proposal-ready decisions, separating facts, inferences, and assumptions.

## Clarification / Specify Rules

Use these rules to discipline ambiguity handling and specification quality:

- **`[NEEDS CLARIFICATION: ...]` marker**: Use this exact syntax for unresolved blocking ambiguity. Example: `[NEEDS CLARIFICATION: Should the proposal revise the existing workflow or create a new one?]`
- **Ambiguity classification**: Tag each clarification as `blocking` (must resolve before proceeding) or `minor` (can proceed with a recommended default).
- **What / why before how**: Describe the problem and desired outcome before specifying implementation details. Defer how to the planning phase.
- **Recommended defaults**: When ambiguity is minor, state a recommended default and proceed. Do not block on solvable questions.
- **Given / When / Then scenarios**: Use this format for acceptance criteria involving behavior or user workflows. Optional for non-behavioral proposals.
- **Independently testable criteria**: Every acceptance criterion should be verifiable without ambiguity about success or failure.

Do not ask questions that can be resolved by discovery. Ask only questions that block a correct proposal.

## Update-vs-New Heuristics

When an existing proposal covers a related area, decide whether to revise, supersede, or create a new artifact:

- **Revise** the existing proposal when: the change is incremental, the existing artifact's scope still covers the new request, and the artifact is in `draft` or `needs-clarification` status.
- **Supersede** the existing proposal when: the new request materially changes the scope, intent, or recommended approach, and the existing proposal is `accepted` or `rejected`. Mark the old proposal status as `superseded` and create a new artifact.
- **Create new** when: the new request covers a distinct area, a different work type, or a separate decision that would conflate concerns with the existing proposal.

Record the Update-vs-New decision in the proposal artifact with a brief justification.

## Proposal-to-Plan Handoff

For `standard` and `deep` proposals, include a structured handoff section that planning can consume:

```md
## Planning Handoff

### Agreed Objective
<One or two sentences that become plan.objective.>

### Accepted Decisions
- <Decision and reason.>

### Scope Boundaries
In scope:
- ...

Out of scope:
- ...

### Constraints
- ...

### Acceptance Criteria to Preserve
- <Criterion that planning must map to gates/steps.>

### Risks to Monitor During Planning
- ...

### Suggested Delegation / Skills
- discovery: worker-* with generic-mode instructions
- analysis: worker-* with review-mode instructions
- implementation: worker-* with coding-mode instructions
- docs/templates: worker-* with documentation-mode instructions

### OpenCode Docs Required for Handoff / Delegation Design
- Agents: <https://opencode.ai/docs/agents/>
- Skills: <https://opencode.ai/docs/skills/>
- Permissions: <https://opencode.ai/docs/permissions/>
- Tools: <https://opencode.ai/docs/tools/>
- Rules / AGENTS.md: <https://opencode.ai/docs/rules/>
- Commands, when command handoffs are in scope: <https://opencode.ai/docs/commands/>
- Config, when agent or permission registration is in scope: <https://opencode.ai/docs/config/>

### Required Planning Analysis
- problem breakdown
- dependency graph
- parallel groups
- delegation packet inventory
```

This section should be human-readable markdown with consistent headings so the planning skill can consume it reliably.

## Enhanced Embedded Critique Criteria

Critique should check:

- **Completeness**: All required sections are filled
- **Clarity**: Language is precise and unambiguous
- **Scope boundaries**: In/out of scope are explicit
- **Alternatives**: At least one plausible non-trivial alternative is considered
- **Risk handling**: Risks are listed with severity and mitigation
- **Acceptance criteria**: Criteria are independently verifiable; scenarios used when behavior is involved
- **Plan-readiness**: Standard/deep proposals contain a complete planning handoff section
- **Evidence quality**: Deep proposals include a structured evidence ledger with confidence and fit caveats; findings are source-backed, not assumed
- **Ambiguity handling**: Blocking unknowns are marked with `[NEEDS CLARIFICATION: ...]`; minor ambiguity has recommended defaults
- **Specification clarity**: What/why is separated from how; acceptance criteria are independently testable
- **Depth-tier appropriateness**: Deep proposals launched appropriate lanes; light/standard proposals were not over-delegated
- **Proposal-vs-plan boundary**: The artifact does not contain dependency graphs, task breakdowns, implementation steps, or runbook state behavior

Critique should not turn the proposal into an execution plan.

## Future Proposal Validity Criteria

A proposal is valid when:

- Depth and intent classification are fully populated
- Discovery results are recorded as facts rather than assumptions
- Clarification questions are asked only when critical to set boundaries
- Unresolved gaps are tagged as critical, minor, or ambiguous
- Assumptions are explicitly listed with rationale
- Standard/deep proposals contain a planning handoff section with agreed objective, scope boundaries, acceptance criteria, risks, and suggested delegation
- Alternatives include at least one plausible non-trivial alternative or an explicit explanation of why alternatives are not meaningful
- Risks are listed with severity and mitigation strategy
- Deep proposals include a depth-tier-appropriate lane matrix with lane-selection rationale
- Deep proposals include an evidence ledger with confidence and fit caveats for accepted findings
- Deep proposals include a delegated analysis summary with tradeoffs and decision impact
- `[NEEDS CLARIFICATION: ...]` markers are used for blocking ambiguity
- Acceptance criteria are independently testable
- Update-vs-New decision is recorded when revising related proposals

## Rules

- Do not implement changes while using this skill.
- Do not write the execution plan here; use the `plan` skill only after the proposal is accepted.
- Keep critique embedded in the proposal artifact rather than creating a separate review lane.
- Use only currently available sized worker families for delegation, plus `multimodal-looker` only for visual/PDF/image work.
- Do not create new worker agents, change model IDs, alter provider configuration, or edit generated/runtime directories unless explicitly requested.
- Ask targeted questions when critical facts are missing.
- Worker-lane roles are implemented by existing `worker-*` tiers and the `delegation` skill; do not introduce new agents or agent families.
- The `delegation` skill is the routing source of truth; do not duplicate the full worker matrix here.
- Deep proposals must not produce implementation plans, task breakdowns, dependency graphs, or runbook state behavior.
