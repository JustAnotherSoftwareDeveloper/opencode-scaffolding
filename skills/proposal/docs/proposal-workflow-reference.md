# Proposal Workflow Reference

This document provides detailed support material for the proposal skill's explore/analyze/specify workflow. It includes illustrative examples, matrices, and checklists that would make `SKILL.md` too long. For operational guidance, see `skills/proposal/SKILL.md`.

## Lane Packet Examples

### Local Explorer Lane Packet

A local explorer lane packet for a deep proposal about changing the runbook format:

```markdown
### Orchestrator
primary

### Skill
none

### Objective
Inventory all runbook-related files in the current harness, including their current state, conventions, and constraints.

### Context
We are considering upgrading the runbook format from XML to a new structured format. Before drafting a proposal, we need to understand the current implementation.

### Files In Scope
- `.runbooks/`
- `skills/runbook/`
- `commands/runbook.md`
- `agents/*.md` (look for runbook-related agents)
- `opencode.json` (look for runbook-related config)

### Files Out of Scope
- Any files outside the current repository
- Any implementation changes
- Any new file creation

### Do / Do-Not Instructions
- DO: List exact file paths, their purposes, and any constraints mentioned in the files.
- DO: Note any conventions used in runbook files (naming, structure, metadata).
- DO: Identify any dependencies between runbook components.
- DO NOT: Suggest implementation approaches or propose changes.
- DO NOT: Modify any files.
- DO NOT: Create new files.
- DO NOT: Perform web research.

### State File
.state/<runbook-id>/<local-explorer-step-id>.json

### Verification
- All files in scope have been examined
- No files outside scope were accessed
- No file modifications were made
- Output is in markdown format with clear section headings

### Return Format
A markdown document with the following sections:
- **Files Found**: List of all runbook-related files with brief descriptions
- **Current Conventions**: Summary of naming, structure, and metadata conventions
- **Constraints**: Any explicit or implicit constraints on runbook format or execution
- **Dependencies**: Relationships between runbook components
- **Open Questions**: Any ambiguities that prevent complete analysis
```

### External Reference Explorer Lane Packet

An external reference explorer lane packet for researching Oh My OpenCode's Sisyphus workflow:

```markdown
### Orchestrator
primary

### Skill
none

### Objective
Research Oh My OpenCode's Sisyphus workflow, focusing on its delegation model, worker roles, and research protocols.

### Context
We are considering incorporating elements of the Sisyphus research and delegation workflow into our proposal process.

### URLs In Scope
- https://github.com/opensoft/oh-my-opencode
- https://raw.githubusercontent.com/opensoft/oh-my-opencode/dev/sisyphus-prompt.md

### Files Out of Scope
- Any files in the local repository
- Any implementation changes
- Any new file creation

### Do / Do-Not Instructions
- DO: Extract the core concepts of Sisyphus's delegation model, worker roles, and research protocols.
- DO: Note any specific practices for worker-tier exploration and analysis.
- DO: Identify transferable ideas for our proposal workflow.
- DO: Record any fit caveats or limitations of applying Sisyphus concepts to our harness.
- DO NOT: Suggest direct adoption of OMO agents or categories.
- DO NOT: Modify any local files.
- DO NOT: Create new files.
- DO NOT: Perform local discovery beyond what's needed to contextualize findings.

### State File
.state/<runbook-id>/<external-reference-explorer-step-id>.json

### Verification
- Only the specified URLs were accessed
- No local files were modified
- No new files were created
- Output distinguishes facts from inferences and assumptions

### Return Format
A markdown document with the following sections:
- **Core Concepts**: Summary of Sisyphus's delegation model, worker roles, and research protocols
- **Transferable Ideas**: Specific practices that could improve our proposal workflow
- **Fit Caveats**: Limitations or concerns about applying these concepts to our existing harness
- **Source Confidence**: Assessment of source reliability and potential staleness
- **Decision Impact**: How these findings should influence our proposal decision
```

## Evidence Ledger Examples

### Example Evidence Ledger from a Deep Proposal

| Lane | Worker | Source | Claim / Fact | Inference | Assumption | Confidence | Relevance | Fit Caveat | Decision Impact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Local explorer | worker-md | skills/runbook/SKILL.md | The current runbook skill uses XML format for state management | The XML format is deeply integrated into the runbook lifecycle | None | High | High | None | Supports maintaining XML format due to integration depth |
| External reference explorer | worker-md | https://raw.githubusercontent.com/opensoft/oh-my-opencode/dev/sisyphus-prompt.md | Sisyphus uses a strong Phase 0 intent gate and parallel exploration/research | We could improve our proposal workflow with more structured exploration phases | Sisyphus concepts can be adapted without adopting its agents | Medium | High | Sisyphus uses different agent names and categories that don't match our configured worker | Supports adding structured exploration to proposals using the configured text worker |
| Historical explorer | worker-md | .proposals/1778883198-xml-runbook-format-replacement.md | A previous proposal considered replacing XML format but was rejected due to migration complexity | Similar migration concerns would apply to any format change | The migration complexity assessment is still valid | High | High | None | Strengthens the case for incremental improvement over format replacement |
| Adversarial / gap analyst | worker-md | Internal analysis | The proposal underestimates the risk of format migration | A full migration would require changes to runbook state initialization, validation, and execution | None | High | High | None | Requires adding stronger risk mitigation strategies to the proposal |

## Lane Requirement Matrix

The following table defines the requirement level for each analysis lane based on evidence needs. All requirements reflect the unified deep-proposal approach:

| Lane | Requirement Level | Evidence Need Trigger |
|------|-------------------|----------------------|
| Local explorer | Required | When local harness files, skills, runbooks, or configuration may be impacted by changes |
| Historical explorer | Optional | When similar artifacts or prior policy decisions exist that could inform the proposal |
 | External reference explorer | Recommended | When external frameworks or comparable solutions should be evaluated for fit |
| Delegation-pattern analyst | Required | For harness-routing, workflow changes, or delegation infrastructure modifications |
| Adversarial / gap analyst | Required | For core workflow changes where risk analysis is critical to decision quality |
| Synthesis analyst | Required | When two or more exploration lanes are launched and tradeoffs need synthesis |
| Embedded review analyst | Recommended | Before final user decision to validate completeness and scope boundaries |

*Note: Lane requirements are determined by evidence needs, not proposal tier. All lanes follow unified deep-proposal approach with comprehensive discovery expectations.*

## Delegated Analysis Examples

### Delegated Analysis Return Guidance

When delegating analysis tasks, workers should return structured findings that include:

- **Tradeoffs**: Comparisons between viable approaches, including cost, risk, and downstream impact
- **Risks**: Identified risks with severity and mitigation, separate from the proposal's own risk section
- **Contradictions**: Conflicts between findings, assumptions, or prior decisions
- **Framework-fit assessment**: How well an external concept maps to this harness's workers and skills
- **Decision impact**: Explicit recommendation on how the analysis should influence the chosen approach

Example return format:

```markdown
## Tradeoffs
- **Approach A (Incremental improvement)**: Lower risk, shorter timeline, but doesn't address long-term limitations
- **Approach B (Full replacement)**: Addresses all limitations, but high migration cost and risk

## Risks
- **Migration risk**: High - format changes could break existing runbooks
- **Adoption risk**: Medium - users would need to learn a new format
- **Maintenance risk**: Low - new format could reduce long-term maintenance

## Contradictions
- Previous proposal assumed XML could be easily replaced, but current analysis shows deep integration
- External reference suggests full replacement is common, but our constraints make this risky

## Framework-fit Assessment
- Sisyphus delegation concepts are valuable but must be adapted to the configured text worker
- We cannot adopt OMO's agent names or categories as they don't match our configured worker model

## Decision Impact
Recommend incremental improvement approach with a phased migration strategy to address both short-term needs and long-term goals.
```

## Specification Checklist

Use this checklist to ensure proposal quality before the embedded critique phase:

- [ ] **Intent clear**: The goal and success criteria are clearly stated
- [ ] **Scope boundaries**: In-scope and out-of-scope items are explicitly defined
- [ ] **Alternatives considered**: At least one viable alternative is discussed
- [ ] **Risks documented**: Key risks are identified with severity and mitigation
- [ ] **Evidence quality**: Discovery findings are source-backed with confidence and fit caveats
- [ ] **Ambiguity handled**: Blocking unknowns are marked with `[NEEDS CLARIFICATION: ...]`
- [ ] **What/why before how**: Problem and desired outcome are described before implementation details
- [ ] **Independently testable**: Acceptance criteria can be verified without ambiguity
- [ ] **Scenarios included**: Given/When/Then scenarios are provided when behavior is involved
- [ ] **Update-vs-new decided**: Decision made on whether to revise, supersede, or create new proposal
- [ ] **Proposal-only**: No dependency graphs, task breakdowns, or implementation steps are included

*Note: This checklist verifies complete artifact structure per the unified deep proposal approach.*

## Update-vs-New Examples

### Example 1: Revise

**Situation**: A new request to add minor improvements to the existing proposal workflow, while the original proposal is still in `draft` status.

**Decision**: Revise the existing proposal.

**Justification**: The change is incremental, the existing artifact's scope still covers the new request, and the artifact is in `draft` status. The improvements will be added to the same proposal document.

### Example 2: Supersede

**Situation**: A new request that fundamentally changes the approach to proposal workflow, while the original proposal has been `accepted` but not yet implemented.

**Decision**: Supersede the existing proposal.

**Justification**: The new request materially changes the scope and recommended approach, and the existing proposal is `accepted`. The old proposal will be marked as `superseded` and a new proposal artifact will be created.

### Example 3: Create New

**Situation**: A request to improve the planning workflow, which is a distinct area from the existing proposal workflow.

**Decision**: Create a new proposal.

**Justification**: The new request covers a different work type and decision that would conflate concerns with the existing proposal. A separate decision artifact is needed.

## Important Reminder

**Explorer and analyst lanes are roles, not new agents.** These labels represent proposal-phase activities that are implemented using the configured text worker and the `delegation` skill. No new worker agents, agent families, or provider configurations are created by this workflow. The `delegation` skill remains the canonical source of truth for worker routing and handoff construction.
