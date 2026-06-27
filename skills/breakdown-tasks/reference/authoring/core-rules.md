# Core Rules

Five atomicity rules for decomposing work into delegation packets.

## 1. Single Unit Of Work

Each task performs exactly one logical change **or** answers exactly one analytical question.
If a task modifies two files, makes two unrelated edits in one file, or answers two independent questions, split it.

## 2. Single Output Artifact

Each task produces exactly one verifiable result — either one output artifact **or** one documented finding.
If a task produces two outputs (e.g., writes a file *and* runs a test, or produces two distinct findings), split verification from production.

## 3. Logical Step Pipeline

Tasks form a pipeline where each is one discrete step in a sequence.
Independent steps become separate parallel-capable tasks.
Dependent steps remain sequential but still individually atomic.

## 4. Dependent Work Serialization

When multiple changes to the same file or multiple analysis steps on the same subject are needed, serialize them as separate sequential tasks.
Each task lists the target file or subject in `## FILES TO READ` or `## FILES TO WRITE`.
Run tasks in order so each sees the prior task's output.

## 5. Skill-Aware But Not Skill-Bound

Available skills inform task decomposition but do not override atomicity.
Use the discovered skill list to assign matching skills, shape task boundaries, and identify missing capabilities.
Never merge or split tasks to match skill scope.
If a skill covers two adjacent concerns, keep them as separate atomic packets — assign the skill to the matching packet only.
Do not adjust task granularity to fit a skill's scope; atomicity rules take precedence.
