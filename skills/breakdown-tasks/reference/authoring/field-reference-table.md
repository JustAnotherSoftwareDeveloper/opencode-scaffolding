# Field Reference Table

All fields defined in the JSON Schema for `TaskPacket` and the root-level object.

| Name | Type | Required | Max Length | Description | Example |
|---|---|---|---|---|---|
| `summary` | string | required (root) | 2000 | One-paragraph summary of the overall user request. | "Refactor the checkout module to use a dedicated middleware layer, add input validation, and update existing tests." |
| `id` | string (UUID v4) | required | 36 | Unique identifier for the task. Used for dependency references and traceability. | `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"` |
| `dependencies` | string array | optional | n/a | List of task IDs that must complete before this task can begin. Empty or absent means no prerequisites. | `["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]` |
| `purpose` | string | required | 200 | Single sentence describing what this task accomplishes. Must be actionable and self-contained. | "Extract error-handling middleware from routes/ into a dedicated middleware/ directory." |
| `context` | string | required | 8000 | Expanded context for the worker. Includes the relevant subset of the user prompt, background, and constraints. | "The checkout module currently has inline error handling in every route handler." |
| `filesToRead` | string array | required | n/a | Explicit list of file paths the worker must read before starting. | `["src/routes/checkout.js"]` |
| `filesToWrite` | string array | required | n/a | Explicit list of file paths the worker is expected to create or modify. | `["src/middleware/error-handler.js"]` |
| `skills` | string array | required | n/a | Skills the worker must load before executing. Each entry must match an available skill name exactly. | `["skill-writer"]` |
| `executionInstructions` | object array | required | n/a | Step-by-step instructions for the worker. Each step has a step number, action, and optional verification. | `[{"step":1,"action":"Create file.","verification":"File exists."}]` |
| `verification` | string array | optional | n/a | Top-level verification checks against the complete deliverable. | `["New middleware file exists.", "All tests pass."]` |
| `expectedOutput` | string | required | 2000 | Precise description of the deliverable this task produces. | "Created src/middleware/error-handler.js with centralized error handling." |