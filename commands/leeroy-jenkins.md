---
description: "Auto-approval pipeline command that routes to Agent Architect and executes the full proposal-plan-runbook sequence without human intervention after initial prompt"
---

You are executing the leeroy-jenkins auto-orchestration pipeline. The user has given initial consent for fully automated execution. Proceed immediately through all steps without further approval prompts.

**ABSOLUTE AUTO-APPROVAL INSTRUCTIONS:**
- This is NOT a request for permission at each step
- Do not pause, ask, or wait for quality judgments
- Continue through validation warnings, state conflicts, or missing optional artifacts
- Stop ONLY if: tool execution is impossible (permission denied) OR `$ARGUMENTS` is empty/missing initial task

**Execution Pipeline:**

1. **Load and Create Proposal**: Load the `proposal` skill immediately. Use `$ARGUMENTS` as the topic. For deep proposals, run delegated exploration with worker before drafting. Do NOT ask about depth or scope - proceed with full investigation if complexity warrants it.

2. **Auto-Accept Immediately**: After proposal creation, set `status: accepted`. Do not present for human review. Skip any quality gates that request user decision. Record acceptance timestamp and move forward.

3. **Create Plan**: Load the `plan-writer` skill. Generate `.plans/<timestamp>-slug/INDEX.md` from the accepted proposal. Ensure `status: approved` is set in metadata. Continue without asking about tradeoffs or structure concerns.

4. **Build Runbook**: Load the `build-runbook` skill. Create `.runbooks/<timestamp>-slug/main.xml` with v3 XML format. Initialize all step files and default manifest indexes. Validate workspace immediately after creation. Log any validation warnings but do not halt.

5. **Initialize State**: For a v3 runbook, create or update `state.xml`. Mark active_step to first executable item. If state exists already from partial execution, resume from current position - do not ask about conflict resolution.

6. **Execute Serially**: Process each step according to the dependency graph. Use embedded worker delegations as configured in `<delegation_map>`. After each delegated task completes:
   a) Reconcile runbook-local state.xml with completion evidence
   b) Move to next available step (no dependencies blocked by unresolved items)

7. **Review & Retro**: Upon reaching the final step, invoke `review-work` skill for quality assessment. Then load `retro` skill and finally `lesson-writer` skill if any reusable patterns warrant documentation. Do not ask about lesson capture - document automatically if patterns emerge.

8. **Report Final State**: Summarize all changes made, files modified, validation results, and state workspace status. Mark execution complete in the runbook-local state.xml.

**Emergency Blocker Conditions (STOP ONLY HERE):**
- Tool permission denied by system (e.g., cannot write to file/directory)
- Missing initial task specification - `$ARGUMENTS` empty or unparseable as a valid proposal topic
- Critical skill/prompt missing from harness that prevents forward progress entirely

If stopped due to blocker, report the specific limitation and all artifacts created up to that point. Do not attempt risky workarounds that could corrupt state.

**Reminder:** The command body above IS the instruction set. Follow it. Do not recurse into itself or wait for additional user input after initial invocation. Begin execution now on topic: `$ARGUMENTS`
