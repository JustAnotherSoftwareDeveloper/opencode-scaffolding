# TaskPacket Field Reference

This table mirrors `../../schema/task-packet.schema.json`. The schema is authoritative
for types, requiredness, and constraints. The shared
[task-contract references](../../../task-contract/reference/README.md) are authoritative
for task identity, atomicity, result and verification alignment, dependency and
coupling meaning, traceability, and authoring metadata. This table does not duplicate
those semantics.

## Boundary Guidance

Review task boundaries using the shared [atomicity and alignment](../../../task-contract/reference/atomicity-and-alignment.md),
[dependencies and coupling](../../../task-contract/reference/dependencies-and-coupling.md),
and [traceability and metadata](../../../task-contract/reference/traceability-and-metadata.md)
references. The fields below are structural interface notes only.

## Root-Level Fields

- **`summary`**
  - Type: `string`
  - Required: yes
  - Constraints: `maxLength`: 2000
  - Description: Schema-level summary of the overall request, scope, and constraints.

- **`tasks`**
  - Type: `array` of `TaskPacket`
  - Required: yes
  - Constraints: `minItems`: 1; no maximum
  - Description: An ordered, uncapped list of delegation packets. The operation's
    concern inventory determines task count.

## TaskPacket Fields

- **`purpose`**
  - Type: `string`
  - Required: yes
  - Constraints: `maxLength`: 200
  - Description: Schema field whose shared semantic role is defined by
    [task identity](../../../task-contract/reference/task-identity.md).

- **`context`**
  - Type: `string`
  - Required: yes
  - Constraints: `minLength`: 200, `maxLength`: 8000
  - Description: Task-specific request details, constraints, decisions, and boundary
    rationale. Use the shared task identity and traceability references for meaning.

- **`filesToRead`**
  - Type: `array` of `string`
  - Required: yes
  - Constraints: `uniqueItems`: true
  - Description: Explicit input paths. Preserve predecessor artifacts and source
    references according to the shared dependency and traceability references.

- **`filesToWrite`**
  - Type: `array` of `string`
  - Required: yes
  - Constraints: `uniqueItems`: true
  - Description: Explicit paths or bounded patterns the worker may create, modify,
    or delete. Coupling meaning belongs to the shared dependencies and coupling
    reference.

- **`skills`**
  - Type: `array` of `string`
  - Required: yes
  - Constraints: `uniqueItems`: true, `minItems`: 1, `maxItems`: 3
  - Description: One to three skills the worker must load. This operation-specific
    assignment limit applies per task and does not limit task count.

- **`executionInstructions`**
  - Type: `array` of `object`
  - Required: yes
  - Constraints: `minItems`: 1, `maxItems`: 5
  - Item fields:
    - `step` (`integer`, required, `minimum`: 1)
    - `action` (`string`, required) — A concrete, verifiable action.
    - `verification` (`string`, optional) — Evidence that the step succeeded.
  - Description: Ordered actions that produce the task's result. The operation owns
    this packet procedure; result and verification alignment follow the shared
    task-contract reference.

- **`verification`**
  - Type: `array` of `string`
  - Required: no
  - Constraints: `minItems`: 1, `uniqueItems`: true
  - Description: Checks for the complete result. Use the shared verification
    alignment reference when defining coverage.

- **`expectedOutput`**
  - Type: `string`
  - Required: yes
  - Constraints: `maxLength`: 2000
  - Description: Precise description of the single `Deliverable` payload. Its
    semantic alignment is defined by the shared task-contract reference.
