# Atomicity And Alignment

An atomic task is the smallest useful piece of a problem that one worker can complete
and hand off. Decomposition is deliberately aggressive: when a boundary is uncertain,
split it. A false split is preferable to hidden compound work.

## Split Rule

A valid decomposition derives every required intermediate and final result from the
requested outcome. Any proposed result that still contains separate discovery,
research, analysis, decisions, authoring, changes, verification, or deliverables is
not atomic. Split it again.

Required predecessor results are treated as fixed and available when testing a
boundary. Two results are separate when either can then be accepted, rejected,
retried, completed, or verified without redoing the other. A dependency preserves
order; it does not make the results one task.

Apply this rule to analysis, documentation, implementation, verification, and
operations. Distinct lifecycle stages are separate tasks by default. Do not merge
them because they share a file, final artifact, workflow, skill, or requested
outcome. Do not target or cap the number of tasks.

## One Result

One task has one purpose, one expected result, and one completion decision. Its
purpose names the immediate result, not a container such as "complete the proposal,"
"implement the feature," or "finish the migration."

A proposed task requires splitting when it contains:

- separately answerable questions;
- source discovery or research followed by analysis of what was found;
- a finding or decision consumed by later work;
- analysis followed by recommendation, planning, authoring, or implementation;
- changes that can be accepted or retried separately;
- implementation followed by an independently executable verification or review;
- independently useful deliverables; or
- an investigation whose answer determines the scope, design, interface, or
  acceptance criteria of later work.

An intermediate result is a real task even when the user did not request a separate
document. Give it the smallest concise handoff its consumer needs. The handoff may be
a finding, inventory, decision, diff, test result, or short written record.

Treat each requested action verb and each distinct object of work as a candidate
task. Split candidates unless they are demonstrably the same indivisible state
change. In particular, default to separate tasks for:

- discovery and inventory;
- research and evidence collection;
- analysis and findings;
- decisions and recommendations;
- proposal, plan, or documentation authoring;
- implementation changes;
- verification, audit, or review; and
- final synthesis or reporting.

## Keep Rule

Keep activities together only when no meaningful intermediate result can be stated or
handed off and separation would leave an invalid, misleading, or unsafe state. This
is a narrow exception, not a balancing preference. The author must state the concrete
failure caused by separation. If that failure is uncertain, speculative, or merely
inconvenient, split the work.

Reading an explicitly known source may remain an execution step. Discovering which
sources matter, interpreting them, deciding from them, or producing findings from
them creates a separate result. Multiple files may still implement one indivisible
state change, but shared topic, file, final document, release, skill, sequence, or
dependency never justifies merging tasks.

## Verification Alignment

Verification is a separate task by default when another worker could run it against a
fixed predecessor result and accept, reject, or retry the check independently. Keep a
check inside the producing task only when it is inseparable from producing a valid
artifact, such as syntax validation required to write the artifact at all. The user
does not need to request a separate verification report for verification to be a
separate task.

## Stopping Rule

Splitting stops only when the task has one immediate result, known inputs, one clear
stopping condition, and no subordinate finding, decision, change, or independently
executable check. Do not stop merely because further splitting feels fine-grained.
When unsure whether a subordinate action has its own result, create the smaller task.
