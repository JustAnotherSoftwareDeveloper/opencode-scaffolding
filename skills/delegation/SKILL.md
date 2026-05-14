---
name: delegation
description: Build OpenCode Task tool delegation packets, select worker family/size dynamically by work type and task size/risk/ambiguity, consume worker results, and handle retry or escalation.
---

# Delegation Skill

Use this skill when a runbook step should be handed to a worker subagent through OpenCode's Task tool pattern. This skill is the **canonical source of truth** for the configured worker matrix, dynamic worker routing, and handoff packet construction. It does not replace the Task tool or create a new agent framework.

## Responsibilities

1. **Classify** an atomic work unit by its type (analysis, coding, doc-writing, synthesis, web research, visual) and its size/risk/ambiguity/cost-of-failure attributes.
2. **Identify** a relevant skill to load, or `null`.
3. **Select** the smallest capable worker family and size using the work-type matrix and the sizing rubric.
4. **Construct** a lean worker handoff prompt using the size-matched template from the tiered packet templates (`templates/delegation-packet-{size}.md`).
5. **Consume** the worker result and reconcile it into runbook state.
6. **Retry, redelegate, or escalate** only when the packet's recovery policy permits it.

## Non-Goals

- Do not replace OpenCode's Task tool.
- Do not add team-mode, tmux, plugin, MCP, model, provider, or agent-registration infrastructure.
- Do not create new worker families or model IDs.
- Do not bypass plan dependencies, file scopes, permissions, or state ownership.
- Do not recommend static worker sizes (e.g. "always use `*-md`") — every delegation must evaluate the atomic unit dynamically.

## Routing Workflow

For each atomic unit:

1. Classify the work type and pick the family from the map below.
2. Identify the skill to load, or `null`.
3. Pick the smallest capable size from the size table. Consider task size, risk, ambiguity, and cost of failure together; do not default to `md`.
4. Select the delegation-packet template matching the chosen size (`templates/delegation-packet-{size}.md`).
5. Build the worker handoff prompt from the selected template.

---

## Work-Type-to-Family Map

| Work type | Route to |
|-----------|----------|
| Analysis, reasoning, tradeoffs, risk, architecture, critique | `analysis-*` |
| Code editing, implementation, refactor, debugging, config writing | `coding-*` |
| Documentation, prompts, skills, commands, guides, structured prose | `doc-writer-*` |
| Synthesis, coordination, classification, extraction, general-purpose tasks | `generic-*` |
| Web research, current facts, source synthesis, evidence comparison | `websearch-*` |
| Image/screenshot/diagram/PDF analysis | `multimodal-looker` |

## Worker Matrix (Canonical Source of Truth)

All 26 configured workers. The matrix reflects the exact `agents/*.md` definitions. The **default model** is the model listed in the agent frontmatter; fallback models are defined in the agent files but omitted here for brevity.

### analysis-* family — Reasoning, tradeoffs, risk, architecture, critique

| Worker | Default model | When to use |
|--------|---------------|-------------|
| `analysis-xs` | `ollama/granite4.1:3b` | Bounded yes/no checks, obvious tradeoff notes, simple risk flags, quick reasoning over very small provided context. |
| `analysis-sm` | `ollama/qwen3-8b-12k` | Comparing options, identifying risks, sanity-checking shell commands, reviewing small design choices, reasoning over provided evidence. |
| `analysis-md` | `openrouter/deepseek/deepseek-v4-flash` | Nontrivial reasoning, multi-factor comparisons, root-cause analysis from supplied evidence, decisions where local analysis may be too weak. |
| `analysis-lg` | `openrouter/mistralai/mistral-small-2603` | Nuanced product, design, planning, and technical tradeoff analysis where judgment matters but the task is not the most expensive tier. |
| `analysis-xl` | `openrouter/deepseek/deepseek-v4-pro` | Hard reasoning, architecture decisions, conflicting evidence, failed prior attempts, high-stakes recommendations, final judgment passes. |

### coding-* family — Code, config, schema, template editing

| Worker | Default model | When to use |
|--------|---------------|-------------|
| `coding-xs` | `ollama/qwen2.5-coder:3b` | One function, one small file, simple syntax fixes, trivial helpers, very explicit low-risk edits. |
| `coding-sm` | `ollama/qwen3-8b-12k` | Narrow repo edits, simple refactors, direct bug fixes with clear context, test fixes, code explanation. |
| `coding-md` | `openrouter/qwen/qwen3-coder-30b-a3b-instruct` | Moderate implementation, several related file edits, bug fixes requiring investigation, repo-aware coding where local models are insufficient. |
| `coding-lg` | `openrouter/qwen/qwen3-coder` | Complex repo-aware implementation, significant refactors, difficult bugs, multi-step changes, tasks requiring strong code reasoning. |
| `coding-xl` | `openrouter/moonshotai/kimi-k2.5` | Hard repo work, large refactors, long-horizon debugging, architecture-sensitive code, tasks where failure is expensive. |

### doc-writer-* family — Documentation, prompts, skills, command prose

| Worker | Default model | When to use |
|--------|---------------|-------------|
| `doc-writer-xs` | `ollama/granite4.1:3b` | Headings, short summaries, bullet cleanup, formatting, small prose rewrites from provided facts. |
| `doc-writer-sm` | `ollama/granite41-8b-12k` | README sections, short docs, changelog notes, small guides, structured prose from known facts. |
| `doc-writer-md` | `openrouter/deepseek/deepseek-v4-flash` | Longer guides, structured documentation, synthesis from multiple worker outputs, clear technical prose. |
| `doc-writer-lg` | `openrouter/mistralai/mistral-small-2603` | Polished guides, longer technical documents, product-style explanations, substantial rewrite/synthesis work. |
| `doc-writer-xl` | `openrouter/minimax/minimax-m2.5` | Polished, coherent, structured prose. Preserves technical truth. Flags missing facts rather than fabricating. |

### generic-* family — Synthesis, coordination, extraction, classification

| Worker | Default model | When to use |
|--------|---------------|-------------|
| `generic-xs` | `ollama/granite4.1:3b` | Trivial classification, short summarization, obvious extraction, naming, simple cleanup, low-risk mechanical answers. |
| `generic-sm` | `ollama/granite41-8b-12k` | Short explanations, small comparisons, bounded synthesis from provided context, simple task decomposition. |
| `generic-md` | `openrouter/deepseek/deepseek-v4-flash` | Moderate synthesis, nontrivial explanation, multi-part tasks, cases where local workers may be too weak. |
| `generic-lg` | `openrouter/qwen/qwen3.6-35b-a3b` | Difficult synthesis, complex task coordination support, cross-domain reasoning, higher-quality answers where cost is acceptable. |
| `generic-xl` | `openrouter/deepseek/deepseek-v4-pro` | High-judgment, high-ambiguity, or high-cost-of-error work. |

### websearch-* family — Web research, current facts, source synthesis

| Worker | Default model | When to use |
|--------|---------------|-------------|
| `websearch-xs` | `ollama/granite4.1:3b` | Extraction and snippet-only summarization from web results. Does not make final recommendations. |
| `websearch-sm` | `ollama/granite41-8b-12k` | Evidence summaries and source-claim separation from web research. |
| `websearch-md` | `openrouter/deepseek/deepseek-v4-flash` | Normal research tasks, current factual lookups, comparison across sources, evidence summaries requiring judgment. |
| `websearch-lg` | `openrouter/qwen/qwen3.6-35b-a3b` | Source-critical synthesis using primary and corroborated sources. |
| `websearch-xl` | `openrouter/moonshotai/kimi-k2.5` | Complex, high-value, high-ambiguity research where source quality, currentness, and judgment are critical. |

### multimodal-* family — Visual analysis

| Worker | Default model | When to use |
|--------|---------------|-------------|
| `multimodal-looker` | `ollama/qwen3-vl:2b-thinking` | Visual analysis for images, screenshots, diagrams, and PDFs. No size variants — this is the only visual worker. |

## Size Selection

Choose the smallest size that matches the task's scope, risk, ambiguity, and cost of failure. Size is not just file count: a one-file architecture decision can require `analysis-lg`, while a broad mechanical inventory can be split across smaller `generic-sm` tasks.

| Size | Use when | Avoid when |
|------|----------|------------|
| `xs` | Exact, supplied-context work: extraction, naming, formatting, tiny summaries, simple checks, one explicit low-risk helper/fix. | Discovery, open-ended reasoning, multi-file edits, final judgment, source-critical research. |
| `sm` | Bounded local work: short synthesis, simple comparisons, small docs, narrow clear-context edits, small design/risk checks. | Architecture decisions, ambiguous debugging, multi-file refactors, high-risk review. |
| `md` | Nontrivial but bounded work: moderate synthesis, normal research, several related edits, root-cause analysis, tasks where local workers may be weak. | High-stakes architecture/final judgment, large refactors, long-horizon debugging. |
| `lg` | Complex or nuanced work: planning/tradeoff analysis, source-critical synthesis, significant refactors, polished guides, difficult bugs. | Routine mechanical work that can be split smaller. |
| `xl` | Highest-risk work: architecture decisions, conflicting evidence, failed prior attempts, high-stakes recommendations, hard repo work. | Routine drafting or small fixes. |

## Escalation and De-Escalation

### When to Escalate (choose a larger size or a more capable family)

1. **Worker reports partial success**: the task exceeded the worker's capability. Redelegate to the next size up in the same family.
2. **Failed prior attempts**: if a first attempt failed, redelegate to `*-lg` or `*-xl` in the same family. Do not retry the same size.
3. **High ambiguity discovered mid-task**: if the worker uncovers ambiguity the packet did not anticipate, escalate to `analysis-lg` or `analysis-xl` for the ambiguity-resolution part, then resume the original work.
4. **Cross-family escalation**: if the task was misclassified (e.g., a "generic" task turned out to need deep code reasoning), redelegate to the correct family at the same or one-larger size.
5. **Cost-of-failure escalation**: if review reveals the failure cost was underestimated, escalate to `*-xl` for the redo.

### When to De-Escalate (choose a smaller size or a local worker)

1. **Oversized packet**: if the packet asked for a `*-xl` analysis but the atomic unit is trivially bounded (one short file, low risk), downgrade to `*-sm` or `*-xs`.
2. **Local worker sufficient**: if the task can be handled by an Ollama worker (`*-xs` or `*-sm`) without quality loss, prefer it over a cloud worker (`*-md` or larger). This saves cost and keeps work offline.
3. **Subtask decomposition**: after an `*-xl` worker produces a plan, delegate subsequent execution subtasks to appropriately smaller workers.

## Handoff Prompt Construction

Select the delegation-packet template matching the chosen worker size from the size chosen in Routing Workflow step 4. Each worker size has a dedicated template in `skills/delegation/templates/`. The compatibility index at `templates/delegation-packet.md` is the canonical size-to-template reference.

| Worker size | Template |
|-------------|----------|
| `xs` | `skills/delegation/templates/delegation-packet-xs.md` |
| `sm` | `skills/delegation/templates/delegation-packet-sm.md` |
| `md` | `skills/delegation/templates/delegation-packet-md.md` |
| `lg` | `skills/delegation/templates/delegation-packet-lg.md` |
| `xl` | `skills/delegation/templates/delegation-packet-xl.md` |

The handoff prompt constructed from the selected template must include:

- orchestrator name;
- skill to load, or `none`;
- one bounded objective;
- relevant context and inputs;
- files in and out of scope;
- explicit do / do-not instructions;
- state file the worker may update, if any;
- verification expectations;
- required return format.

**context fit rule**: If the required context cannot fit within the selected tier's template without overstuffing (e.g., cramming excessive detail, omitting necessary files or instructions), do not overstuff the packet. Instead, decompose the atomic unit into smaller sub-units and delegate each to an appropriately sized worker, or select a larger worker/template size. An overstuffed packet degrades worker focus, increases token waste, and raises the risk of partial or low-quality results.

If delegated work creates or edits JSON/YAML, include the appropriate validator in `verification` when available:

- `uv run --project scripts/python validate-json <file>`
- `uv run --project scripts/python validate-json <file> --schema <schema-file>`
- `uv run --project scripts/python validate-yaml <file>`

## Result Consumption

OpenCode does not provide a documented structured child-session result protocol. Use explicit conventions:

- The worker must end with a concise final summary.
- For plan execution, the worker should also write the assigned `.state/<plan_slug>/<step>.json` file when write access is in scope.
- The orchestrator reconciles `metadata.json` and `MAIN.json`; workers should not edit those unless explicitly assigned.
- If a worker cannot complete the task, it must report the blocker, attempted actions, partial outputs, and recommended recovery.

## Failure Handling

1. **Ambiguous packet** — Repair the packet before retrying. Clarify the objective, scope, acceptance criteria, or context.
2. **Worker lacks capability** — Redelegate to the next capable family/size. Refer to size selection and escalation rules above.
3. **Permission or scope blocker** — Stop and report rather than expanding scope silently. Do not ask the worker to find workarounds.
4. **Repeated attempts fail** — Escalate to `analysis-lg` or `coding-lg` depending on whether the blocker is reasoning or implementation. If those also fail, escalate to `analysis-xl` or `coding-xl`.
5. **Misclassified work type** — Reclassify the atomic unit and redelegate to the correct family. Record the misclassification in the step state so future routing improves.
6. **Record decisions** — Log all retries, reclassifications, and escalation decisions in the relevant step state file.

## Safety Rules

- Do not delegate work that lacks clear objective, scope, acceptance criteria, and expected output.
- Do not ask a worker to modify files outside `files_in_scope`.
- Do not delegate destructive git operations or provider/model/config edits unless a plan explicitly authorizes them.
- Do not hide unresolved assumptions; include them in the packet or stop for clarification.
- Do not route work to workers that are not configured in `agents/*.md`. Only the 26 workers in this matrix (5 families × 5 sizes + `multimodal-looker`) are available.
- Do not hardcode worker sizes in orchestrator prompts or runbook steps. Worker selection must be evaluated dynamically for each atomic unit.
