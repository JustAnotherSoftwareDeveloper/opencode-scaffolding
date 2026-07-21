# TaskPacket Field Reference

Field definitions extracted from `../../schema/task-packet.schema.json`. All fields are documented with their JSON type, required/optional status, constraints, and schema description.

## Root-Level Fields

- **`summary`**
  - Type: `string`
  - Required: yes
  - Constraints: `maxLength`: 2000
  - Description: One-paragraph summary of the overall user request, capturing its goal, scope, and constraints. This gives downstream workers context without requiring them to re-read the full prompt.

- **`tasks`**
  - Type: `array` of `TaskPacket`
  - Required: yes
  - Constraints: `minItems`: 1
  - Description: An ordered list of atomic delegation packets. Each task must represent a single unit of work that can be completed independently.

## TaskPacket Fields

- **`purpose`**
  - Type: `string`
  - Required: yes
  - Constraints: `maxLength`: 200
  - Description: Single sentence describing what this task accomplishes. Must be actionable and self-contained.

- **`context`**
  - Type: `string`
  - Required: yes
  - Constraints: `minLength`: 200, `maxLength`: 8000
  - Description: Task-specific context for the worker. Include the relevant user-request details, background information, and constraints. Do not add filler text. Supports longer prompts up to 8000 characters.

- **`filesToRead`**
  - Type: `array` of `string`
  - Required: yes
  - Constraints: `uniqueItems`: true
  - Description: Explicit list of file paths the worker must read before starting. Purposeful task-related discovery remains permitted under the worker contract.

- **`filesToWrite`**
  - Type: `array` of `string`
  - Required: yes
  - Constraints: `uniqueItems`: true
  - Description: Explicit write boundary containing file paths or bounded path patterns the worker is authorized to create, modify, or delete.

- **`skills`**
  - Type: `array` of `string`
  - Required: yes
  - Constraints: `uniqueItems`: true, `maxItems`: 3
  - Description: Zero to three skills the worker must load before executing. An empty array authorizes direct packet execution without specialized skill guidance.

- **`executionInstructions`**
  - Type: `array` of `object`
  - Required: yes
  - Constraints: `minItems`: 1, `maxItems`: 5
  - Item fields:
    - `step` (`integer`, required, `minimum`: 1)
    - `action` (`string`, required) — What to do in this step. Must be concrete and verifiable.
    - `verification` (`string`, optional) — How to verify this step succeeded (e.g., "File exists at path X", "Tests pass", "No error output").
  - Description: Step-by-step instructions for the worker. Each step is a discrete, verifiable action. Steps must be ordered and numbered.

- **`verification`**
  - Type: `array` of `string`
  - Required: no
  - Constraints: `minItems`: 1, `uniqueItems`: true
  - Description: Top-level verification checks the worker must run against their output before finishing. These are checks on the complete deliverable, not per-step checks.

- **`expectedOutput`**
  - Type: `string`
  - Required: yes
  - Constraints: `maxLength`: 2000
  - Description: Precise description of the `Deliverable` payload this task produces. Use concrete language such as file paths, function names, and data formats.
