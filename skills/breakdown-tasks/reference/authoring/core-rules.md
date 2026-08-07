# Core Rules

Five atomicity rules for decomposing work into delegation packets.

## 1. Single Unit Of Work

Each task performs exactly one logical change **or** answers exactly one analytical question.
If a task modifies two files, makes two unrelated edits in one file, or answers two independent questions, split it.

*Rationale: A task with multiple logical changes cannot be verified against a single expected output, creates ambiguity about which change caused a failure, and prevents clean rollback or independent review. Atomicity ensures each task is independently verifiable, testable, and reversible.*

## 2. Single Output Artifact

Each task produces exactly one verifiable result — either one output artifact **or** one documented finding.
If a task produces two outputs (e.g., writes a file *and* runs a test, or produces two distinct findings), split verification from production.

*Rationale: A task that produces two outputs (e.g., writes a file and runs a test) has two success/failure conditions. The delegator expects one verifiable result per packet; multiple outputs make the success signal ambiguous.*

## 3. Logical Step Pipeline

Tasks form a pipeline where each is one discrete step in a sequence.
Independent steps become separate parallel-capable tasks.
Dependent steps remain sequential but still individually atomic.

*Rationale: A pipeline model (vs. a flat list) communicates dependency order to the delegator. Independent steps can run in parallel; dependent steps must run sequentially. Without this structure, the orchestrator cannot parallelize safely.*

## 4. Dependent Work Serialization

When multiple changes to the same file or multiple analysis steps on the same subject are needed, serialize them as separate sequential tasks.
Each task lists the target file or subject in `## FILES TO READ` or `## FILES TO WRITE`.
Run tasks in order so each sees the prior task's output.

When the exact path of a prior task's output is not known at decomposition time, use a bounded glob pattern (e.g., `.plans/*-<slug>/tasks.json`) in `filesToRead`. The worker discovers the exact file by matching the pattern. Never use template variables such as `{{TASK_1_OUTPUT}}` or placeholder syntax.

*Rationale: Concurrent edits to the same file cause merge conflicts. Serializing dependent work ensures each task sees a consistent state. Listing the target file in `## FILES TO READ` or `## FILES TO WRITE` makes the dependency explicit.*

## 5. Skill-Aware But Not Skill-Bound

Available skills inform task decomposition but do not override atomicity.
Use the discovered skill list to assign matching skills, shape task boundaries, and identify missing capabilities.
Never merge or split tasks to match skill scope.
If a skill covers two adjacent concerns, keep them as separate atomic packets.
Assign the skill to the matching packet only.
Do not adjust task granularity to fit a skill's scope.
Atomicity rules take precedence.

*Rationale: Skills are tools for executing work, not boundaries that define work. Merging tasks to match a skill's scope destroys atomicity and makes verification ambiguous. Atomicity rules take precedence because verifiability is more important than skill convenience.*
