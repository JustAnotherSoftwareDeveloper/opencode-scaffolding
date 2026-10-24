---
name: generic-analysis
description: "Use when analyzing a problem, request, artifact, or decision to produce an evidence-calibrated assessment and next actions."
selection:
  role: owner
  tags:
    actions: [analyze, assess]
    inputs: [problem, request, artifact, decision]
    outputs: [analysis, evidence-calibrated assessment]
    topics: [cross-domain reasoning]
  use_when: [a problem or decision needs evidence-based analysis]
  not_for: [authoring a decision proposal or executable plan]
class: operation
---

# Generic Analysis

Analyze ambiguous or cross-domain work with a deliberate, evidence-calibrated reasoning procedure.

## Input

- Accept a question, request, artifact, decision, incident, proposal, or observed outcome.
- Extract the stated objective, supplied context, constraints, stakeholders, and requested deliverable.
- Treat missing material facts as unknowns rather than assumptions.

## Output

Choose the output route from the requested deliverable, not its subject or filename:

- **Ordinary analysis (default):** Create one document at `$CWD/.analysis/<unix-epoch-milliseconds>-<summary-slug>.md`. Use the Ordinary Analysis Format below.
- **Audit/review report:** Use this route only when the user explicitly requests a final audit or review report. Asking to analyze an audit or review, mentioning those words in a title or path, or citing an existing report does not qualify. A report states its review scope, evidence-linked findings, overall disposition, and verification limits; do not recast ordinary analysis as a report.
  - When a specialized audit/review skill owns the requested scope, use that skill instead; generic-analysis does not replace it.
  - When generic-analysis owns the request, create one report directly under repository-root `.audit/<unix-epoch-milliseconds>-<summary-slug>.md`. Create repository-root `.audit/` when absent.

Derive `<summary-slug>` as a lowercase kebab-case slug from the analysis question or report subject.

Create `$CWD/.analysis/` when ordinary analysis output is selected. Never replace an existing document or report; choose an unused output path.

Return only the relative path to the created document or report.

### Ordinary Analysis Format

- **Question:** State the decision, claim, or problem under analysis.
- **Scope:** Define the objective, boundaries, constraints, and success criteria.
- **Evidence:** List material observations and identify each source or assumption.
- **Analysis:** Explain the causal model, trade-offs, risks, alternatives, and confidence level.
- **Conclusion:** Answer the question directly.
- **Next Actions:** List prioritized, concrete actions or information required to resolve uncertainty.

## Analysis Types

- Use [Problem Framing](./reference/problem-framing.md) to define an ambiguous problem, objective, scope, and success criteria.
- Use [Root Cause Analysis](./reference/root-cause-analysis.md) to identify mechanisms and contributing conditions behind an outcome.
- Use [Decision Analysis](./reference/decision-analysis.md) to compare options against explicit criteria and trade-offs.
- Use [Artifact Analysis](./reference/artifact-analysis.md) to inspect code, documents, data, logs, or configurations.
- Use [Stakeholder Analysis](./reference/stakeholder-analysis.md) to assess affected parties, incentives, authority, and needs.
- Use [Risk Analysis](./reference/risk-analysis.md) to assess likelihood, impact, exposure, and mitigation.
- Use [Systems Analysis](./reference/systems-analysis.md) to map dependencies, feedback loops, bottlenecks, and second-order effects.
- Use [Feasibility Analysis](./reference/feasibility-analysis.md) to test technical, operational, legal, financial, and time constraints.
- Use [Gap Analysis](./reference/gap-analysis.md) to compare the current state with a target state.
- Use [Impact Analysis](./reference/impact-analysis.md) to assess direct and downstream effects of a proposed change.
- Use [Scenario Analysis](./reference/scenario-analysis.md) to prepare for plausible future conditions.
- Use [Sensitivity Analysis](./reference/sensitivity-analysis.md) to identify assumptions that change a conclusion.
- Use [Cost-Benefit Analysis](./reference/cost-benefit-analysis.md) to compare economic value, costs, and opportunity cost.
- Use [Requirements Analysis](./reference/requirements-analysis.md) to validate, reconcile, and prioritize requirements.
- Use [Security Threat Analysis](./reference/security-threat-analysis.md) to identify assets, attack paths, controls, and residual exposure.
- Use [Data Quality Analysis](./reference/data-quality-analysis.md) to assess completeness, accuracy, consistency, lineage, and fitness for use.
- Use [Performance Analysis](./reference/performance-analysis.md) to assess latency, throughput, capacity, and bottlenecks.
- Use [Failure Mode Analysis](./reference/failure-mode-analysis.md) to identify failure paths, detection, severity, and mitigations.
- Use [Comparative Analysis](./reference/comparative-analysis.md) to compare alternatives or artifacts using consistent criteria.

## Execution Plan

1. Normalize the request into one analysis brief containing the question, objective, scope, constraints, evidence, and desired outcome.
2. Define the decision criterion or claim that determines a useful conclusion.
3. Select the applicable analysis types from [Analysis Types](#analysis-types).
4. Inspect supplied artifacts and gather only evidence that can change the conclusion.
5. Distinguish observations, source-backed facts, assumptions, interpretations, and unknowns.
6. Build a causal or comparative model that connects the evidence to the question.
7. Test the leading conclusion against credible alternatives, boundary conditions, risks, and counterevidence.
8. State a direct conclusion with a calibrated confidence level and the assumptions that limit it.
9. Ask a focused question when a missing fact materially changes the conclusion.
10. Derive an epoch-millisecond timestamp and lowercase kebab-case summary slug from the analysis question or requested report subject.
11. Select the output route using [Output](#output); an explicitly requested audit/review report must also pass its report criteria, while ordinary analysis remains the default.
12. Write to the selected route using its specified content requirements.
13. Return the created file's relative path.

Execute one reasoning pass.
Avoid delegation and multi-phase orchestration.

## Guardrails

- Preserve the distinction between evidence and inference.
- Prefer primary sources, direct inspection, and reproducible observations over unsupported claims.
- Quantify material impact when available.
- Name uncertainty instead of masking it with confident language.
- Present alternatives fairly before rejecting them.
- Keep recommendations within the stated scope and authority.
- Do not execute changes unless the request explicitly includes implementation.
- Write ordinary analysis documents only under `$CWD/.analysis/`; write an explicitly requested audit/review report under repository-root `.audit/` only as specified in [Output](#output).
- Do not route by topic words, filenames, or references to existing audits/reviews, and do not replace an existing output.

## Self-Validation

- Define the analysis question and decision criterion.
- Anchor every material claim in evidence or label it as an assumption.
- Address the strongest plausible alternative or counterexample.
- State confidence and material uncertainty.
- Deliver a conclusion that answers the request directly.
- List actionable next steps when uncertainty or risk remains.
- Confirm the created file exists under the selected route: ordinary analysis at `$CWD/.analysis/`, or an explicitly requested audit/review report at repository-root `.audit/`.
- For an audit/review report, confirm it identifies the review scope, evidence-linked findings, overall disposition, and verification limits.

## Docs

See `./reference/README.md` for analysis lenses and evidence rules.
