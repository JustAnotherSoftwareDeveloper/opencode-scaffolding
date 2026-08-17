# TaskPacket Field Reference

These definitions summarize `../../schema/task-packet.schema.json`. The schema is
authoritative for types, requirements, and constraints.

## Boundary Guidance

Metadata records the author's boundary decision. It does not prove conceptual
atomicity. Review the purpose, result, verification, dependencies, and coupling
evidence together.

## Root-Level Fields

- **`summary`**
  - Type: `string`
  - Required: yes
  - Constraints: `maxLength`: 2000
  - Description: One-paragraph summary of the overall request, scope, and constraints.

- **`tasks`**
  - Type: `array` of `TaskPacket`
  - Required: yes
  - Constraints: `minItems`: 1; no maximum
  - Description: An ordered, uncapped list of delegation packets. Independent work
    determines task count.

## TaskPacket Fields

- **`purpose`**
  - Type: `string`
  - Required: yes
  - Constraints: `maxLength`: 200
  - Description: One actionable sentence naming the task's result.

- **`context`**
  - Type: `string`
  - Required: yes
  - Constraints: `minLength`: 200, `maxLength`: 8000
  - Description: Task-specific request details, constraints, decisions, and boundary
    rationale. Do not add filler text.

- **`filesToRead`**
  - Type: `array` of `string`
  - Required: yes
  - Constraints: `uniqueItems`: true
  - Description: Explicit input paths. Include predecessor artifacts for dependent
    tasks. Use a bounded glob only when an earlier task determines the exact path.

- **`filesToWrite`**
  - Type: `array` of `string`
  - Required: yes
  - Constraints: `uniqueItems`: true
  - Description: Explicit paths or bounded patterns the worker may create, modify,
    or delete. A shared destination does not prove coupling.

- **`skills`**
  - Type: `array` of `string`
  - Required: yes
  - Constraints: `uniqueItems`: true, `minItems`: 1, `maxItems`: 3
  - Description: One to three skills the worker must load. This limit applies per
    task and does not limit task count.

- **`executionInstructions`**
  - Type: `array` of `object`
  - Required: yes
  - Constraints: `minItems`: 1, `maxItems`: 5
  - Item fields:
    - `step` (`integer`, required, `minimum`: 1)
    - `action` (`string`, required) — A concrete, verifiable action.
    - `verification` (`string`, optional) — Evidence that the step succeeded.
  - Description: Ordered actions that produce the task's result. Attach verification
    to that result unless verification is a requested deliverable.

- **`verification`**
  - Type: `array` of `string`
  - Required: no
  - Constraints: `minItems`: 1, `uniqueItems`: true
  - Description: Checks for the complete result. Several checks may verify one result.

- **`expectedOutput`**
  - Type: `string`
  - Required: yes
  - Constraints: `maxLength`: 2000
  - Description: Precise description of the single `Deliverable` payload. It must
    align with `purpose` and verification.
