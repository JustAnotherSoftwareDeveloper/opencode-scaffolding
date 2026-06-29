# Field Reference Table

All fields defined in the JSON Schema for `TaskPacket` and the root-level object.

- **`summary`**
  - **Type:** string
  - **Required:** required (root)
  - **Max Length:** 2000
  - **Description:** One-paragraph summary of the overall user request.
  - **Example:** "Refactor the checkout module to use a dedicated middleware layer, add input validation, and update existing tests."

- **`id`**
  - **Type:** string (UUID v4)
  - **Required:** required
  - **Max Length:** 36
  - **Description:** Unique identifier for the task.
    Used for dependency references and traceability.
  - **Example:** `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`

- **`dependencies`**
  - **Type:** string array
  - **Required:** optional
  - **Max Length:** n/a
  - **Description:** List of task IDs that must complete before this task can begin.
    Empty or absent means no prerequisites.
  - **Example:** `["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]`

- **`purpose`**
  - **Type:** string
  - **Required:** required
  - **Max Length:** 200
  - **Description:** Single sentence describing what this task accomplishes.
    Must be actionable and self-contained.
  - **Example:** "Extract error-handling middleware from routes/ into a dedicated middleware/ directory."

- **`context`**
  - **Type:** string
  - **Required:** required
  - **Max Length:** 8000
  - **Description:** Expanded context for the worker.
    Includes the relevant subset of the user prompt, background, and constraints.
  - **Example:** "The checkout module currently has inline error handling in every route handler."

- **`filesToRead`**
  - **Type:** string array
  - **Required:** required
  - **Max Length:** n/a
  - **Description:** Explicit list of file paths the worker must read before starting.
  - **Example:** `["src/routes/checkout.js"]`

- **`filesToWrite`**
  - **Type:** string array
  - **Required:** required
  - **Max Length:** n/a
  - **Description:** Explicit list of file paths the worker is expected to create or modify.
  - **Example:** `["src/middleware/error-handler.js"]`

- **`skills`**
  - **Type:** string array
  - **Required:** required
  - **Max Length:** n/a
  - **Description:** Skills the worker must load before executing.
    Each entry must match an available skill name exactly.
  - **Example:** `["skill-writer"]`

- **`executionInstructions`**
  - **Type:** object array
  - **Required:** required
  - **Max Length:** n/a
  - **Description:** Step-by-step instructions for the worker.
    Each step has a step number, action, and optional verification.
  - **Example:** `[{"step":1,"action":"Create file.","verification":"File exists."}]`

- **`verification`**
  - **Type:** string array
  - **Required:** optional
  - **Max Length:** n/a
  - **Description:** Top-level verification checks against the complete deliverable.
  - **Example:** `["New middleware file exists.", "All tests pass."]`

- **`expectedOutput`**
  - **Type:** string
  - **Required:** required
  - **Max Length:** 2000
  - **Description:** Precise description of the deliverable this task produces.
  - **Example:** "Created src/middleware/error-handler.js with centralized error handling."
