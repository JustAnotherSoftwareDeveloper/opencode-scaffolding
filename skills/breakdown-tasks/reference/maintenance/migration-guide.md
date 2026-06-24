# Migration Guide

How to update decompositions written under the old implicit schema to the new v2.0.0 schema.

## Key Mapping

| Old (Implicit) | New v2.0.0 | Notes |
|---|---|---|
| No `id` | `id` (UUID v4, required) | Generate a UUID v4 for each task. |
| No `dependencies` | `dependencies` (string array, optional) | Empty by default. Populate for serial ordering. |
| `purpose` (present) | `purpose` (unchanged) | No change needed. |
| `details` or inline preamble | `context` (maxLength 8000) | Move all background into the `context` field. |
| `filesToRead` (present) | `filesToRead` (unchanged) | No change needed. |
| `filesToWrite` (present) | `filesToWrite` (unchanged) | No change needed. |
| `skills` (present) | `skills` (unchanged) | No change needed. |
| Free-form `instructions` string | `executionInstructions` (array of objects) | Split into numbered steps. Add optional `verification` per step. |
| No `verification` | `verification` (string array, optional) | Add holistic checks on the complete deliverable. |
| `expectedOutput` (optional) | `expectedOutput` (required, maxLength 2000) | Make explicit and concrete. |
| No root `summary` | `summary` (required, maxLength 2000) | Write a one-paragraph summary of the overall request. |

## Migration Steps

### 1. Add A Summary Field

Write one paragraph at the root level describing the overall goal of the decomposition.

### 2. Generate UUID V4 IDs

Assign each task a unique UUID v4 in its `id` field.

### 3. Move Context Into The Context Field

Copy all relevant preamble, background, and constraints from the original prompt or inline notes into the `context` field.
Use the full 8000-character capacity.

### 4. Convert Instructions To ExecutionInstructions

Split the old free-form instruction string into numbered steps.
Each step gets a `step` integer, an `action` string, and an optional `verification` string.
Ensure steps are sequential starting at 1.

### 5. Add Verification Arrays

Write holistic checks that validate the complete task deliverable.
These complement any per-step verification.

### 6. Make ExpectedOutput Explicit And Required

Replace vague deliverables with concrete descriptions referencing file paths, function names, and data formats.

### 7. Remove Or Rename Deprecated Fields

Rename `details` to `context`.
Remove `tags` if present (functionality replaced by structured fields).