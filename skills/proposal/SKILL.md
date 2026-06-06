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
- **Required workspace files (13 total)**: Every future proposal workspace must contain exactly these markdown files:

  | File | Purpose |
  | --- | --- |
  | `INDEX.md` | Table of contents only; no frontmatter, status, or duplicated prose. |
  | `metadata.md` | Proposal frontmatter and status metadata owner. |
  | `goal.md` | Outcome definition and success criteria. |
  | `problem-opportunity.md` | Current state (under "Current State" heading) plus problem/opportunity statement. |
  | `scope.md` | In-scope/out-of-scope boundaries. |
  | `recommended-approach.md` | Preferred path with rationale. |
  | `alternatives-considered.md` | Viable alternatives comparison and rejection reasons. |
  | `risks-and-unknowns.md` | Uncertainty, compatibility concerns, and mitigations. |
  | `acceptance-criteria.md` | Independently verifiable success checks (Given/When/Then for behavior). |
  | `decision.md` | Status (`draft`/`accepted`/etc.), decision maker, next action, quality-check summary. |
  | `clarification-questions.md` | Blocking unknowns; explicitly state "None required" when applicable. |
  | `artifact-and-state-impact.md` | Files/artifact paths that will be created or modified later. |
  | `discovery-results.md` | Source-backed evidence ledger, lane rationale, and delegated analysis summary (if any). |

- File presence is **not** gated by ambiguity, depth tier, or proposal type; all 13 files are required for every future workspace. Use "None" / "Not applicable" content when a section has nothing to report.
- Existing historical `.proposals/*.md` proposal files remain valid read-only artifacts; do not migrate, rewrite, move, or split them unless a future accepted proposal explicitly authorizes migration.
- Preserve the original timestamp and slug when updating an existing directory proposal unless superseding it is explicitly intended.

## Lifecycle

1. **Classify intent and depth**: Determine proposal depth tier and intent classification before drafting.
2. **Explore** (deep): Decompose discovery into bounded worker-lane roles; launch lanes per the depth-tier lane matrix; record evidence in the ledger.
3. **Analyze** (deep): Delegate bounded analysis lanes; synthesize findings into decision-ready tradeoffs, risks, and impact. For deep proposals that require harness-wide or architecture-sensitive analysis, delegate to `worker` with the proposal-skill's lane topology guidance.
4. **Specify**: Resolve blocking ambiguity with clarification markers; draft acceptance criteria as independently testable statements.
5. **Create or update artifact**: Write the proposal workspace to `.proposals/<unix-timestamp>-slug/INDEX.md` plus `metadata.md` and canonical section files.
6. **Run embedded critique**: Delegate critique to `worker` with review-mode instructions and record findings directly in the proposal.
7. **Revise**: Incorporate user feedback and critique into the same proposal artifact.
8. **Decision**: Mark the proposal `accepted`, `needs-clarification`, `rejected`, or `superseded`.
9. **Return summary**: Report artifact path, status, key tradeoffs, and the next user decision.

## Routing

Worker sizing and escalation are governed by the `delegation` skill, which is the **canonical source of truth** for the configured worker matrix. This skill describes lane intent; it does not duplicate the full worker configuration.

| Work | Worker Family | Purpose |
| --- | --- | --- |
| Local discovery | `worker` with generic-mode instructions | Inventory files, conventions, and constraints |
| External research | `worker` with web-research-mode instructions | Gather current source-backed information |
| Proposal drafting and revision | `worker` with documentation-mode instructions | Write clear proposal prose |
| Embedded critique | `worker` with review-mode instructions | Identify gaps, risks, and acceptance problems |

Choose the appropriate worker for each bounded task.

## Proposal Artifact Format

Create `.proposals/<unix-timestamp>-slug/` with all 13 required files as specified in the Artifact Contract section. Each file should document its respective concern using the linked guidance above. When a section has no meaningful contribution for the current proposal (e.g., deep-lane work not triggered), explicitly state "None" or "Not applicable to this proposal."

`templates/proposal-template.md` is retained only as a legacy reference for historical single-file proposals. Do not use it for new proposals unless recovering or reading an existing `.proposals/*.md` artifact.

## Section Guidance

For each section, use the dedicated file and provide substantive content. When a section has no meaningful contribution for the current proposal: explicitly state "None required" or "Not applicable to this proposal." Deep proposals follow the same rule—results go in required files even if they require minimal effort.

- **Goal** (`goal.md`): Outcome definition and success criteria.
- **Current State / Problem-Opportunity**: Use `problem-opportunity.md` with a "Current State" heading for discovered facts, then the problem/opportunity statement.
- **Problem / Opportunity** (`problem-opportunity.md`): The pain point or improvement target after current state summary.
- **Scope** (`scope.md`): In-scope/out-of-scope boundaries drawn explicitly.
- **Recommended Approach** (`recommended-approach.md`): Preferred path with rationale for why it is the smallest correct direction.
- **Alternatives Considered** (`alternatives-considered.md`): Compare viable alternatives; explain why they are not preferred or provide explicit explanation of why no meaningful alternative exists.
- **Artifact and State Impact** (`artifact-and-state-impact.md`): Files, artifact paths, and state areas that will be created or modified later.
- **Risks and Unknowns** (`risks-and-unknowns.md`): Uncertainty, compatibility concerns, permission concerns, state drift, mitigation strategies (severity + mitigation).
- **Discovery Results** (`discovery-results.md`): Source-backed evidence ledger with lane, worker, source, claim/fact, inference, assumption, confidence, relevance, fit caveat, decision impact; also includes delegated analysis summary if any lanes were launched.
- **Clarification Questions** (`clarification-questions.md`): Blocking unknowns marked for user resolution or explicitly state "None required."
- **Acceptance Criteria** (`acceptance-criteria.md`): Independently verifiable checks using Given/When/Then when behavior is involved.
- **Decision** (`decision.md`): Current status, decision maker when known, next action, and embedded quality-check summary.

## Proposal Depth Tiers

Use the following depth tiers to determine the appropriate level of effort:

| Depth | When to use | Discovery needed | Research needed | Planning notes |
| --- | --- | --- | --- | --- |
| `none` | Trivial/direct execution; no proposal needed | None | None | Direct execution without proposal |
| `light` | Narrow, low-risk change with a short proposal | Minimal local check (file existence, constraints) or explicit "None" in required files | None | Plan extracts goals/scope/acceptance from workspace |
 | `standard` | Normal non-trivial harness/product/code change | Local discovery of files, constraints, and conventions documented in `discovery-results.md` | Optional, for syntax/config conventions or comparable examples | Plan derives handoff from accepted proposal sections |
| `deep` | Ambiguous, architecture-sensitive, high-risk, or cross-cutting change | Serial local analysis/research to stabilize understanding; results recorded in required files | External research as needed for standards or breaking changes | All lane findings consolidated into the 13-file workspace |

Use `none` for trivial tasks (e.g., typo fixes, surface changes). Use `light` for narrow changes in one file. Use `standard` for normal non-trivial work. Use `deep` for architecture-sensitive or harness-wide changes.

## Worker-Lane Topology

Explorer and analyst lanes are **proposal-phase roles** implemented with the configured text worker, relevant skills, and bounded handoff packets. They are **not new agents** and do not require new agent configurations. The `delegation` skill governs lane intent and worker routing for each bounded task.

| Lane | Purpose | Worker |
| --- | --- | --- |
| Local explorer | Inventory current harness files, commands, skills, conventions, and constraints. | `worker` |
| Historical explorer | Inspect prior proposals, plans, runbooks, state, and lessons for related decisions or conflicts. | `worker` |
| External reference explorer | Research one external source per lane with cited facts and fit caveats. | `worker` |
| Delegation-pattern analyst | Map external delegation concepts onto the harness; review the proposal skill's depth-tier matrix guidance. | `worker` |
| Adversarial / gap analyst | Challenge assumptions, detect contradictions, shallow evidence, and plan leakage. | `worker` |
| Synthesis analyst | Merge lane outputs into proposal-ready decisions, risks, and acceptance criteria. Required when three or more lanes were launched. | `worker` |
| Embedded review analyst | Apply `review-work` and proposal quality checks before user decision. Route to `worker`. | `worker`

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

Each delegated lane uses a bounded handoff packet constructed via the `delegation` skill. The packet is the **input contract** for the worker; the evidence ledger in `discovery-results.md` is the **proposal artifact output** that records what the orchestrator accepted.

Every lane packet must include:

- **Objective**: One clear, bounded objective for the lane.
- **Source / file boundaries**: Exact files, paths, or URLs in scope.
- **Out-of-scope**: Files, URLs, or behaviors explicitly excluded.
- **Output contract**: Required return format (facts, inferences, assumptions with rationale, confidence levels, caveats, decision impact). All findings go into `discovery-results.md` regardless of depth tier.
- **Evidence format**: How findings should be recorded (markdown table, bullet list, etc.).
- **Assumptions policy**: State any assumptions the worker may make; flag if uncertain.
- **Do / do-not rules**: Explicit boundaries including proposal-only guardrails—workers must not create dependency graphs, task breakdowns, runbook states, or implementation planning deliverables.

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

The proposal contains all information a plan needs via the required workspace files. Planning derives handoff content from accepted decisions in `decision.md`, scope boundaries in `scope.md`, constraints noted across relevant section files, and acceptance criteria documented in `acceptance-criteria.md`. A separate structured "Planning Handoff" file is **not** required; plans extract what they need directly from the 13-file workspace.

Historical proposals may contain a "Planning Handoff" section as evidence of prior practice; such sections are preserved read-only but not replicated for new workspaces.

## Enhanced Embedded Critique Criteria

Critique should check:

- **Completeness**: All 13 required files are present and minimally populated.
- **Clarity**: Language is precise and unambiguous; what/why separated from how.
- **Scope boundaries**: In/out of scope are explicit in `scope.md`.
- **Alternatives**: At least one plausible non-trivial alternative considered or explicit explanation why none.
- **Risk handling**: Risks listed with severity, impact, and mitigation.
- **Acceptance criteria**: Criteria are independently testable; Given/When/Then used when behavior is involved.
- **Evidence quality**: Findings are source-backed with confidence and fit caveats in `discovery-results.md`.
- **Ambiguity handling**: Blocking unknowns marked with `[NEEDS CLARIFICATION: ...]`; minor ambiguity has recommended defaults.
- **Proposal-vs-plan boundary**: No dependency graphs, task breakdowns, implementation steps, or runbook state behavior. Plans use `tasks/` for instructions; runbooks use isolated `steps/` XML.

Critique should not turn the proposal into an execution plan.

## Future Proposal Validity Criteria

A proposal is valid when:

- Depth and intent classification are fully populated (may be documented in `metadata.md`).
- Discovery results are recorded as facts rather than assumptions.
- Clarification questions are asked only when critical to set boundaries; otherwise, `clarification-questions.md` explicitly states no clarification is required.
- Unresolved gaps are tagged as critical, minor, or ambiguous.
- Assumptions are explicitly listed with rationale in `discovery-results.md`.
- All 13 required workspace files are present and populated (use "None" / "Not applicable" when appropriate).
- Alternatives include at least one plausible non-trivial alternative or an explicit explanation of why alternatives are not meaningful.
- Risks are listed with severity and mitigation strategy.
- Evidence ledger includes confidence and fit caveats for accepted findings.
- `[NEEDS CLARIFICATION: ...]` markers are used for blocking ambiguity.
- Acceptance criteria are independently testable.

## Rules

- Do not implement changes while using this skill.
- Do not write the execution plan here; use the `plan` skill only after the proposal is accepted.
- Keep critique embedded in the proposal artifact rather than creating a separate review lane.
- Use only the configured text worker (`worker`) for delegation, plus `multimodal-looker` only for visual/PDF/image work.
- Do not create new worker agents, change model IDs, alter provider configuration, or edit generated/runtime directories unless explicitly requested.
- Ask targeted questions when critical facts are missing.
- Worker-lane roles are implemented by the configured text worker and the `delegation` skill; do not introduce new agents or agent families.
- The `delegation` skill is the routing source of truth; do not duplicate the full worker matrix here.
- All proposal workspaces contain exactly 13 required files regardless of depth tier.
