---
artifact_type: proposal
schema_version: 1
id: orchestration-skill-upgrade
title: Artifact-Driven Proposal, Planning, and Quarterback Orchestration Upgrade
status: draft
created_at: 2026-05-13
updated_at: 2026-05-13
owner: agent-architect
source_request: Upgrade planning and proposal skills with file artifacts, state management, and stricter delegation inspired by oh-my-openagent.
related_plan: null
review_gate: pending
---

# Proposal: Artifact-Driven Proposal, Planning, and Quarterback Orchestration Upgrade

## 1. Goal

Upgrade the OpenCode orchestration harness so `proposal` and `plan` become artifact-driven, stateful, review-gated workflows, inspired by `oh-my-openagent`, and change the orchestrator role into a strict “quarterback” that delegates nearly all substantive work to workers.

No implementation should begin until the target contract, artifact layout, and state model are reviewed and accepted.

## 2. Proposed Scope

### In Scope

1. Upgrade `skills/proposal/SKILL.md`.
   - Move from “return a proposal in chat” to “produce and maintain a proposal artifact.”
   - Introduce `.proposal` / `.proposal.md` files with a strict contract.
   - Add discovery, gap analysis, review, acceptance, amendment, and state transitions.
   - Require workers to draft, critique, and validate proposals instead of the orchestrator writing them directly.

2. Upgrade `skills/plan/SKILL.md`.
   - Move from “produce a runbook in chat” to “produce and maintain an executable plan artifact.”
   - Plans must be generated only from an accepted proposal or an explicitly user-authorized direct-plan request.
   - Add task decomposition, delegation map, verification gates, recovery, notepads/learnings, and state updates.

3. Upgrade `prompts/orchestrator-base.md`.
   - Reframe the orchestrator as a quarterback/conductor, not a doer.
   - It should classify intent, maintain state, dispatch workers, synthesize worker outputs, enforce gates, and report status.
   - It should avoid direct research, drafting, implementation, and review whenever a worker can do it.

4. Update `prompts/agent-architect.md`.
   - Align Agent Architect with the new quarterback contract.
   - Make harness changes plan-artifact driven.
   - Require independent review before reporting success.

5. Optionally update `commands/agent-architect.md`.
   - Teach the command to recognize proposal and plan files.
   - Add explicit behavior for:
     - create proposal,
     - revise proposal,
     - create plan from proposal,
     - execute plan,
     - resume active work.

6. Add artifact and state conventions.
   - Proposal files.
   - Plan files.
   - State file.
   - Notepad/learning files.
   - Review records.

### Out of Scope

- Changing existing worker agent names.
- Changing existing model IDs.
- Changing existing provider configuration.
- Changing fallback ordering.
- Editing generated/runtime files such as `node_modules/`, `.opencode/node_modules/`, lock files, or OpenCode runtime data.
- Implementing full `oh-my-openagent` team mode, mailbox tools, provider arbitration, infinite review loops, or complex lock management in the first iteration.

## 3. Recommended Approach

Adopt a lightweight version of `oh-my-openagent`’s strongest workflow ideas without importing its full complexity.

The most valuable ideas to adapt are:

1. **Planner → Conductor → Worker separation**
   - Proposal/plan authorship and critique should be worker-driven.
   - The orchestrator should coordinate, not personally solve everything.

2. **Artifact-first workflow**
   - Proposals and plans should live as files, not only chat responses.
   - Files become the source of truth across sessions.

3. **Quality gates**
   - Proposal and plan artifacts should be reviewed before downstream execution.
   - Use explicit acceptance/rejection criteria.

4. **State management**
   - Track active proposal, active plan, phase, workers, review status, and unresolved blockers.

5. **Wisdom accumulation**
   - Preserve decisions, learnings, issues, and verification results for later workers.

Do not copy the more complex parts of `oh-my-openagent` immediately, such as full team-mode tooling, complex mailbox systems, provider arbitration, infinite review loops, or multi-agent lock management. Those can become later iterations.

## 4. Inspiration From oh-my-openagent

Research identified several useful patterns from `oh-my-openagent`:

### 4.1 Three-Layer Orchestration

`oh-my-openagent` separates work into:

- a planning layer,
- an execution/conductor layer,
- worker/specialist layers.

The key idea to adapt is strict separation of responsibility. The planning workflow creates artifacts. The conductor reads artifacts, delegates, tracks state, and verifies. Workers do the actual research, drafting, editing, and review.

### 4.2 Plan Artifacts

Plans in `oh-my-openagent` are durable markdown files that bridge planning and execution. They contain task breakdowns, acceptance criteria, references, and verification criteria.

OpenCode should adopt the same core idea for both proposals and plans.

### 4.3 Quality Pipeline

`oh-my-openagent` uses multiple review personas for gap analysis and ruthless plan review. OpenCode can adapt this with existing agents:

- `analysis-*` for gap analysis and design critique.
- `oracle` for final artifact review.
- `doc-writer-*` for artifact drafting and revision.

### 4.4 Boulder-Style State

`oh-my-openagent` tracks active work across sessions through state files. OpenCode should introduce a lightweight equivalent that tracks the active proposal, active plan, current phase, status, worker runs, open questions, blockers, and last verification.

### 4.5 Wisdom / Notepad Accumulation

The notepad idea is valuable because worker learnings should not be lost between delegations. OpenCode should preserve:

- decisions,
- learnings,
- issues,
- verification outcomes,
- handoff summaries.

### 4.6 Concepts To Avoid Initially

Avoid immediately importing:

- full team mode,
- shared mailboxes,
- file locks,
- tmux visualization,
- provider-arbitration logic,
- per-agent fallback chains,
- infinite review loops,
- autonomous continuation loops without explicit bounds.

These are powerful but too heavy for the first upgrade.

## 5. Proposed Artifact Layout

Because this is global OpenCode config, distinguish between:

- global harness files under `/home/michael/.config/opencode`, and
- per-project workflow artifacts created in whichever project OpenCode is operating on.

Recommended default per-project artifact root:

```text
.opencode-work/
  state.json
  proposals/
    <slug>.proposal.md
  plans/
    <slug>.plan.md
  reviews/
    <slug>.proposal.review.md
    <slug>.plan.review.md
  notepads/
    <slug>/
      decisions.md
      learnings.md
      issues.md
      verification.md
      handoff.md
```

Reason: this avoids colliding with OpenCode’s own `.opencode/` runtime directory while still making artifacts obviously OpenCode-related.

If exact extensions are preferred, use:

```text
.opencode-work/proposals/<slug>.proposal
.opencode-work/plans/<slug>.plan
```

Recommended readable option:

```text
.opencode-work/proposals/<slug>.proposal.md
.opencode-work/plans/<slug>.plan.md
```

## 6. Proposal Artifact Contract

A proposal should become a durable decision artifact.

### Proposed File: `<slug>.proposal.md`

```md
---
artifact_type: proposal
schema_version: 1
id: <slug>
title: <human title>
status: draft | needs-clarification | under-review | accepted | rejected | superseded
created_at: <iso timestamp>
updated_at: <iso timestamp>
owner: orchestrator
source_request: <short user request>
related_plan: null
review_gate: pending | passed | failed | waived-by-user
---

# Proposal: <title>

## 1. Goal

<What the user wants, restated clearly.>

## 2. Intent Classification

- Intent: research | design | harness-change | implementation | bugfix | review | mixed
- Urgency:
- Risk:
- Requires external research: yes/no
- Requires codebase discovery: yes/no
- Requires user decision before planning: yes/no

## 3. Current State

<Summarized facts discovered by workers. Include exact files, conventions, constraints.>

## 4. Problem / Opportunity

<Why change is needed. What pain this solves.>

## 5. Proposed Scope

### In Scope

- ...

### Out of Scope

- ...

## 6. Recommended Approach

<The preferred direction and why.>

## 7. Alternatives Considered

| Alternative | Pros | Cons | Decision |
| --- | --- | --- | --- |

## 8. Contract Changes

<If changing a skill, agent, command, state file, permission, or workflow, define the new contract here.>

## 9. State Management Impact

<What persistent state will be created or modified.>

## 10. Delegation Model

<Which work should be delegated, to whom, and what the orchestrator must not do itself.>

## 11. Risks And Unknowns

| Risk | Impact | Mitigation |
| --- | --- | --- |

## 12. Acceptance Criteria

- [ ] ...
- [ ] ...

## 13. Review Findings

<Worker/oracle review summary, or link to review artifact.>

## 14. Decision

Status: accepted | rejected | needs changes

Decision maker:
Decision date:
Notes:
```

## 7. Proposal Skill Behavior

The upgraded `proposal` skill should require this lifecycle:

1. **Classify intent**
   - The orchestrator performs only lightweight classification.
   - If non-trivial, delegate discovery/research.

2. **Create proposal artifact**
   - A drafting worker writes the first proposal.
   - The orchestrator should not author the full proposal itself unless no worker is available.

3. **Run gap analysis**
   - Use `analysis-*` or `oracle`.
   - Check ambiguity, hidden assumptions, missing acceptance criteria, unsafe scope, and unclear state impacts.

4. **Revise proposal**
   - A doc/prompt worker revises the artifact.

5. **Review gate**
   - Proposal must be marked `accepted` before planning, unless the user explicitly requests direct planning.

6. **Return concise summary**
   - Final chat response should summarize the artifact path and decision needed.

## 8. Plan Artifact Contract

A plan should become an executable orchestration runbook, not just a checklist.

### Proposed File: `<slug>.plan.md`

```md
---
artifact_type: plan
schema_version: 1
id: <slug>
title: <human title>
status: draft | under-review | approved | executing | blocked | complete | superseded
created_at: <iso timestamp>
updated_at: <iso timestamp>
proposal: ../proposals/<slug>.proposal.md
active_phase: discovery | execution | review | retro | complete
review_gate: pending | passed | failed | waived-by-user
---

# Plan: <title>

## 1. Objective

<What success means.>

## 2. Proposal Summary

<Link to accepted proposal and summarize accepted direction.>

## 3. Inputs

- User request:
- Proposal:
- Relevant files:
- Worker findings:
- External references:

## 4. Constraints

- Permissions:
- Files not to touch:
- Compatibility:
- Model/tool limits:
- State constraints:

## 5. Execution Strategy

<High-level approach.>

## 6. Delegation Map

| Work ID | Work Item | Agent | Skill | Parallel | Writes Files | Expected Output |
| --- | --- | --- | --- | --- | --- | --- |

## 7. Task Graph

| Task ID | Depends On | Owner | Status | Acceptance Criteria |
| --- | --- | --- | --- | --- |

## 8. Phase Runbook

### Phase 1: Discovery

- Delegations:
- Required outputs:
- Gate to proceed:

### Phase 2: Draft / Design

- Delegations:
- Required outputs:
- Gate to proceed:

### Phase 3: Execute

- Delegations:
- Required outputs:
- Gate to proceed:

### Phase 4: Review

- Delegations:
- Required outputs:
- Gate to proceed:

### Phase 5: Retro / Handoff

- Delegations:
- Required outputs:
- Gate to complete:

## 9. Verification Gates

| Gate | Command / Check | Required Result |
| --- | --- | --- |

## 10. State Updates

<What state.json fields must change at each phase.>

## 11. Notepad Updates

Required updates:

- `decisions.md`
- `learnings.md`
- `issues.md`
- `verification.md`
- `handoff.md`

## 12. Rollback / Recovery

<How to recover from partial edits, failed validation, bad worker output, or interrupted session.>

## 13. Final Report Contract

The orchestrator must report:

- What changed.
- Files modified.
- Workers used.
- Validation results.
- Risks/skipped checks.
- Follow-ups.
```

## 9. State Management Proposal

### Proposed File: `.opencode-work/state.json`

```json
{
  "schema_version": 1,
  "active_proposal": null,
  "active_plan": null,
  "phase": "idle",
  "status": "idle",
  "created_at": null,
  "updated_at": null,
  "session_ids": [],
  "worker_runs": [],
  "open_questions": [],
  "blocked_on": null,
  "last_verification": null
}
```

### State Transitions

```text
idle
  → proposing
  → proposal-review
  → proposal-accepted
  → planning
  → plan-review
  → plan-approved
  → executing
  → reviewing
  → retro
  → complete
```

Blocked paths:

```text
proposing → blocked
planning → blocked
executing → blocked
reviewing → blocked
```

Recovery paths:

```text
blocked → proposing
blocked → planning
blocked → executing
blocked → idle
```

### State Rules

- The orchestrator may update state directly.
- Workers may propose state updates but should not blindly mutate state unless explicitly delegated.
- Every phase transition should be explainable.
- State should reference artifact paths, not duplicate all artifact content.
- If state and artifact disagree, artifact frontmatter wins, and state should be repaired.

## 10. Orchestrator Quarterback Contract

The upgraded orchestrator should be explicitly forbidden from doing substantive work that can be delegated.

### The Orchestrator Should Do

- Classify user intent.
- Decide whether proposal, plan, direct execution, review, or retro is needed.
- Create bounded worker prompts.
- Dispatch workers in parallel.
- Track state.
- Enforce proposal/plan/review gates.
- Synthesize worker outputs.
- Decide when to escalate to stronger agents.
- Ask the user for decisions when required.
- Report concise status.

### The Orchestrator Should Not Do

- Personally perform broad codebase discovery.
- Personally research external repos.
- Personally draft long proposals/plans when a worker can.
- Personally implement file edits except tiny mechanical/state updates.
- Personally review its own final work as the only review.
- Skip artifact creation for non-trivial work.
- Collapse proposal, plan, execution, and review into one response.

### Recommended Wording

Add a strong rule to `orchestrator-base.md`:

> You are the quarterback, not the runner. Your default action is to delegate. You may classify, route, synthesize, enforce gates, update orchestration state, and report. You should not personally perform discovery, drafting, implementation, or final review when a suitable worker exists.

## 11. Delegation Model

### Proposal Workflow Delegations

| Work | Agent | Purpose |
| --- | --- | --- |
| Harness/codebase discovery | `explore` or `librarian` | Inventory relevant files and conventions |
| External research | `websearch-md` / `websearch-lg` | Summarize source repo/docs |
| Proposal draft | `doc-writer-md` / `doc-writer-lg` | Write artifact |
| Risk critique | `analysis-md` / `analysis-lg` | Find gaps and alternatives |
| Final review | `oracle` | Validate clarity, risk, scope, acceptance criteria |

### Plan Workflow Delegations

| Work | Agent | Purpose |
| --- | --- | --- |
| Proposal digestion | `analysis-sm` | Extract accepted decisions |
| Runbook draft | `doc-writer-md` | Write plan artifact |
| Task decomposition | `analysis-md` | Validate dependency graph and delegation map |
| Execution feasibility | `coding-md` or `analysis-md` | Check whether plan can be executed safely |
| Final plan review | `oracle` | Approve/reject plan artifact |

### Execution Workflow Delegations

| Work | Agent | Purpose |
| --- | --- | --- |
| Read-only discovery | `explore` | Locate files and conventions |
| Implementation | `coding-*` | Apply bounded edits |
| Prompt/skill/command prose | `doc-writer-*` | Draft or revise harness prose |
| Config safety | `oracle` or `analysis-*` | Review correctness and safety |
| Documentation | `doc-writer-*` | Write docs and reports |
| Web/source research | `websearch-*` | Research current external sources |

## 12. Review Gate Proposal

Borrowing from `oh-my-openagent`, introduce two quality gates.

### Proposal Review Gate

A proposal passes only if:

- Goal is clear.
- Scope and out-of-scope are explicit.
- At least one alternative is considered.
- Risks are concrete.
- Acceptance criteria are testable.
- State/artifact impacts are described.
- User decision needed is explicit.

### Plan Review Gate

A plan passes only if:

- It references an accepted proposal or explicit direct-plan authorization.
- Every task has an owner.
- Every task has acceptance criteria.
- Parallel work is marked safely.
- Verification gates are concrete.
- Rollback/recovery exists.
- State updates are defined.
- Final report contract is clear.

### Suggested Review Statuses

```text
pending
passed
failed
waived-by-user
```

## 13. Command Upgrade Proposal

Current command:

```text
commands/agent-architect.md
```

It currently routes a goal or runbook path to Agent Architect.

Recommended enhancement:

```md
If arguments name a `.proposal.md` file:
- Read it.
- If accepted, offer to create a plan.
- If draft/needs-clarification, continue proposal workflow.

If arguments name a `.plan.md` file:
- Read it.
- Validate it.
- Execute only if approved or user explicitly authorizes execution.

If arguments are a goal:
- Start proposal workflow unless the task is trivial.

If arguments include `resume`:
- Read `.opencode-work/state.json`.
- Resume the active artifact.
```

Potential future commands:

```text
/propose <goal>
/plan <proposal-path>
/execute-plan <plan-path>
/resume-work
/handoff
```

Do not add all of these immediately unless a larger command surface is desired. First upgrade the core skill/orchestrator contracts.

## 14. Alternatives Considered

### Alternative 1: Minimal Skill Edits Only

Update `proposal` and `plan` text but do not add files/state.

Pros:

- Simple.
- Low risk.

Cons:

- Does not satisfy the requested massive upgrade.
- No cross-session continuity.
- No durable source of truth.

Decision: not recommended.

### Alternative 2: Fully Clone oh-my-openagent Patterns

Add planner/conductor/worker agents, boulder state, notepads, team mode, mailbox, strict review agents, command suite, and continuation enforcement.

Pros:

- Very powerful.
- Closest to inspiration source.

Cons:

- Too much complexity at once.
- Higher risk of brittle prompts.
- More permissions and state edge cases.
- Might overfit to another harness’s assumptions.

Decision: not recommended for first iteration.

### Alternative 3: Artifact-First Workflow With Lightweight State

Add proposal/plan artifacts, state file, notepads, strict delegation, and review gates, but avoid team-mode complexity.

Pros:

- Satisfies the core request.
- Strongly improves continuity and delegation.
- Keeps changes understandable and reversible.
- Maps cleanly to current OpenCode skills/agents.

Cons:

- Requires careful prompt writing.
- Some state handling will initially be convention-based, not enforced by tooling.
- Workers may still need orchestration discipline until commands mature.

Decision: recommended.

## 15. Risks And Unknowns

1. **Artifact root choice**
   - Recommended: `.opencode-work/`.
   - Alternatives: `.opencode/`, `.sisyphus/`, or another directory.

2. **File extension preference**
   - User mentioned `(.plan, .proposal)`.
   - Need to decide whether exact extensions are desired:
     - `foo.plan`
     - `foo.proposal`
   - Or Markdown-readable:
     - `foo.plan.md`
     - `foo.proposal.md`

3. **How strict should “orchestrator delegates everything” be?**
   - Absolute delegation may be inefficient for tiny mechanical steps.
   - Recommended allowance: orchestrator may update state, perform tiny path checks, synthesize final answers, and ask user decisions.
   - It should not draft, research, implement, or review substantive work.

4. **State mutation safety**
   - Multiple workers editing `state.json` could conflict.
   - Recommendation: orchestrator owns state writes; workers return proposed updates.

5. **Current config has limited explicit primary agents**
   - `agent-architect` is config-registered.
   - Worker agents exist as markdown agents.
   - Need validation after edits to ensure all agents are discoverable.

6. **Review loop depth**
   - `oh-my-openagent` allows strict repeated review.
   - Recommend max 2–3 loops by default, then ask user.

## 16. Acceptance Criteria

This upgrade should be considered successful when:

1. `skills/proposal/SKILL.md` defines:
   - proposal artifact format,
   - lifecycle,
   - state updates,
   - delegation requirements,
   - review gate,
   - acceptance/rejection behavior.

2. `skills/plan/SKILL.md` defines:
   - plan artifact format,
   - lifecycle from accepted proposal,
   - delegation map,
   - task graph,
   - verification gates,
   - rollback/recovery,
   - state/notepad updates.

3. `prompts/orchestrator-base.md` clearly says:
   - orchestrator is quarterback only,
   - delegate by default,
   - no direct substantive work when workers exist,
   - artifact/state lifecycle must be followed.

4. `prompts/agent-architect.md` aligns with the upgraded harness workflow.

5. Optional command update teaches `commands/agent-architect.md` to handle:
   - proposal files,
   - plan files,
   - goals,
   - resume behavior.

6. Validation passes:
   - JSON config remains valid.
   - Skill frontmatter remains valid.
   - Skill names still match directories.
   - Command frontmatter remains valid.
   - No model IDs or worker names are changed.
   - No generated/runtime files are edited.

## 17. Decision Needed

Recommended decision: proceed with **Alternative 3: artifact-first workflow with lightweight state**.

Before implementation, decide:

1. Preferred artifact directory:
   - Recommended: `.opencode-work/`

2. Preferred file naming:
   - Recommended: `<slug>.proposal.md` and `<slug>.plan.md`
   - Exact-extension option: `<slug>.proposal` and `<slug>.plan`

3. Strictness of quarterback mode:
   - Recommended: strict delegation for substantive work, with direct orchestrator handling allowed only for classification, state updates, routing, synthesis, and final reporting.
