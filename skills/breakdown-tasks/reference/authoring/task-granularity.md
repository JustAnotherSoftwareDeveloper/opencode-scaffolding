# Task Granularity Guidelines

Heuristics for splitting work into atomic delegation packets.

## One Task Per File Change

Each task modifies exactly one file.
Changes to multiple files are permitted only when tightly coupled.
Adding a function to `utils.py` is one task.
Adding a function to `utils.py` and writing its test is two tasks.
Adding a type in `types.ts` and importing it in `handler.ts` is one task.
These changes are tightly coupled.
Adding a type in `types.ts` and adding unrelated helpers in `utils.ts` is two tasks.

## One Task Per Conceptual Change

Each task addresses exactly one concern.
Do not bundle unrelated changes.
"Add validation" is one task.
"Add validation + update tests + update docs" is three tasks.
"Refactor checkout + add error handling" is two tasks.
"Create component + wire to store + add tests" is three tasks.

## Single Action Verbs

Purpose statements must contain exactly one action verb.
Split "Create and configure" into "Create config file" then "Configure application".
Split "Implement and test" into "Implement function" then "Write unit tests".
Split "Analyze and report" into "Run analysis" then "Write findings report".

## One Purpose, One Expected Output

Each task must have exactly one `purpose` sentence and exactly one `expectedOutput` paragraph.
If a task needs two sentences to state its purpose, split it.
Good: purpose: "Add input validation to the checkout form." expectedOutput: "Updated checkout form component with input validation for all required fields."
Bad: purpose: "Add input validation to the checkout form and update the backend to validate on submission." (two concerns)
