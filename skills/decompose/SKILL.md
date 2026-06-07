---
name: decompose
description: Decompose work into maximally atomic serial units with bounded objectives and files suitable for step-by-step execution by workers. May delegate to worker for scope clarification when boundaries are ambiguous.
class: planning
---

# Decompose Skill

Use this skill when you need to analyze, classify, or break down work into atomic units but are uncertain about scope boundaries, step sequencing, or file groupings.

## When to Use

- You are unsure how to decompose a task or phase into atomic units.
- The work spans unclear boundaries or multiple capability domains.
- You need to validate that your decomposition is sufficiently atomic.
- The task has mixed complexity levels or intertwined concerns.

## Output Format

Decomposition results are structured as numbered unit sections ready for worker handoff via delegation packets. Each unit MUST include all required fields:

1. **Unit ID/Description**: Sequential number with brief descriptor (e.g., "01 - Add authentication middleware")

2. **Objective**: Single, actionable goal statement scoped to bounded files and context

3. **Files In Scope / Files Out of Scope**: Explicit file lists or glob patterns defining unit boundaries; out-of-scope items explicitly excluded

4. **Context Inputs**: Required prior knowledge, previous outputs, or external dependencies needed for correct execution (may reference earlier units). **Rule**: Must cite specific artifacts/sections rather than broad "read whole repo" instructions to enable worker-context minimization.

5. **State File** *(optional)*: Path to state file this unit updates and/or consumes; use "none" if stateless or orchestrator-managed. Enables cross-unit dependency tracking.

6. **Do's/Don'ts**: Specific guidance on required actions and prohibited changes within this unit

7. **Verification**: Validation criteria to confirm successful completion; maps to worker return/evidence requirements

8. **Suggested Skill**: Recommended skill routing (`worker`, `decompose`, or other) for execution (or "none" if orchestrator-handled)

9. **Expected Return/Evidence**: Description of what the worker should produce and how it will be structured in their response

10. **Dependencies/Previous Step**: Sequential ordering metadata linking to upstream units when serial execution is required; empty or "parallel" for independent units

### Validation Examples

**Good atomic unit patterns:**

✅ *Single-file edit*:  
Unit 07 - Update decomposition rule references in SKILL.md  
Objective: Change line references from old format to new format (lines 89-123)  
Files In Scope: `skills/decompose/SKILL.md` / Files Out of Scope: all other files  
Dependencies: none

✅ *Bounded multi-file*:  
Unit 04 - Refactor validation rules across two schemas  
Objective: Apply identical rule changes to config-schema.json and worker-schema.json  
Files In Scope: `schemas/config-schema.json`, `schemas/worker-schema.json` / Out of Scope: docs, examples  
Dependencies: none (parallel-safe)

**Needs refinement:**

❌ *Too large*: "Implement the full feature X" — split into distinct units per file/concern.

❌ *"Update all documentation"* → Split by document/file with specific objectives per unit.

**Quality checklist for decomposition:**

1. **Atomicity pass**: One objective, one validation mode, bounded files
2. **Serial order check**: Dependencies explicitly listed or "none"/"parallel"
3. **File boundary test**: Clear in-scope/out-of-scope lists present
4. **Context minimality**: Inputs cite specific artifacts, not "read everything"

```markdown
## Analysis

Brief summary of the work and key considerations.

## Atomic Units (Example)

1. **Unit 01** - Example decomposition step  
   Objective: [single objective]  
   Files In Scope: [bounded files]  
   Files Out of Scope: [explicitly excluded items]  
   Context Inputs: [cite specific artifacts/sections, e.g., "state.xml lines 56-64", "previous unit output"]  
   State File: [path or "none"]  
   Do's: [specific actions required]  
   Don'ts: [prohibited changes]  
   Verification: [how to confirm completion]  
   Suggested Skill: worker | none  
   Expected Return/Evidence: [structured response format with evidence markers]  
   Dependencies/Previous Step: 01, 02 → parallel

## Decomposition Patterns

### Single-file changes
- Identify the file and the required change.
- Return one atomic unit scoped to that file.

### Multi-file implementation
- Group files by similar change type (edits, creates, deletes).
- Separate unrelated file sets into distinct units.

### Cross-cutting changes
- Identify the core change and its dependencies.
- Return units in dependency order if sequential work is needed.

### Ambiguous scope
- Delegate analysis to `worker` with this skill loaded.
- The worker may run discovery to clarify boundaries.

## Delegation Guidance

When uncertainty is high:
1. Load this skill with `worker` using analysis-mode instructions.
2. Include the original user request and any available context.
3. Request: recommended phase, atomic breakdown, and risk assessment.
4. Review the worker's analysis, then proceed with actual delegation.

**Worker-Context Minimization**: When constructing units for delegation packets, ensure Context Inputs cites specific artifacts/sections (e.g., "state.xml lines 12-20", "proposal section 3"). This enables workers to receive minimal but sufficient context without overstuffing packets. Reference `delegation` skill's Context Fit Rule for boundary decisions.

## Rules

### Maximally Atomic Unit Criteria

A maximally atomic decomposition splits work into the smallest worker-dispatchable unit with:

1. **Single Objective**: One clear, actionable outcome statement scoped to bounded files and context. The worker should not need to reason about unrelated concerns or file sets within this unit.

2. **Bounded Scope**: Explicit boundaries defined by:
   - Files In Scope (and out of scope)
   - Required context inputs from prior units
   - Independent when possible; dependent only on explicit upstream work

3. **Minimal Context Requirements**: Workers should need no more information than what is provided in the unit's fields plus any explicitly listed dependencies. If analysis requires broad discovery, delegate to `worker` with this skill loaded for scope clarification before decomposition.

**Split whenever:**
- A worker would need to reason about unrelated files across different decision domains
- Distinct validation modes or completion criteria exist within a single unit
- Broader context is needed beyond the stated dependencies and objectives

### Serial Execution Support

Units may have explicit sequential ordering via Dependencies/Previous Step field:

- **Empty**: Independent unit; can execute in parallel with other independent units
- **Unit ID reference (e.g., "01")**: Sequential dependency on prior unit completion
- **"parallel"**: Explicitly intended for concurrent dispatch alongside sibling units
- **Multiple references (e.g., "01, 03 → parallel")**: Depends on multiple upstream units; can run concurrently with other independent work

**Dependency indicators:**
- Units producing outputs consumed by later steps should list those dependencies
- Serial chains should be numbered and referenced explicitly to guide execution order
- Parallelization notes help orchestrators group dispatchable units while respecting constraints

### Delegation Routing

When decomposition boundaries are unclear or analysis needs broader context:
1. Delegate to `worker` with this skill loaded for scope clarification
2. Include the original request and available context in the delegation packet
3. The worker may run discovery skills to inform boundary decisions before returning a refined atomic breakdown