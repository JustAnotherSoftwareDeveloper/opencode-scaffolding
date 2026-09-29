# TaskPacket Field Reference

This reference summarizes the structure in
[`task-packet.schema.json`](../../schema/task-packet.schema.json). The schema is
authoritative for types, requiredness, and constraints. The loaded `task-contract`
documentation skill is authoritative for task identity, atomicity, result and
verification alignment, dependency and coupling meaning, traceability, and
authoring metadata. These notes cover structure, not those shared semantics.

## Boundary Guidance

Review task boundaries using the loaded documentation skill's named **Atomicity
and alignment**, **Dependencies and coupling**, and **Traceability and metadata**
references. The fields below describe the JSON interface only.

## Root-Level Fields

The root must be an object with exactly these required fields:

- **`summary`** — Required string describing the overall request, goal, scope, and
  constraints.
- **`slug`** — Required author-selected string identifying the packet. It has a
  `minLength` of 1, a `maxLength` of 80, and must match the schema's lowercase
  ASCII kebab-case pattern. Publishers and consumers preserve it unchanged.
- **`tasks`** — Required array of `TaskPacket` objects with at least one item and
  no maximum item count.
- **`boundaryReview`** — Required object containing the required
  `requestResultInventory`, `taskReviews`, and `warningDispositions` members. The
  schema defines their nested structures and constraints.

The root schema rejects additional properties.

## Required TaskPacket Fields

Each task must contain the following fields. The task schema rejects additional
properties.

- **`taskId`** — Required string matching the schema's stable task-identity
  pattern.
- **`purpose`** — Required string. The shared
  **Task identity** reference defines its meaning.
- **`context`** — Required string. Use the shared task identity and traceability
  references for its meaning.
- **`filesToRead`** — Required array of strings with unique items. It may be empty.
  These are explicit input paths.
- **`filesToWrite`** — Required array of strings with unique items. It may be
  empty. These paths or bounded patterns define the write boundary.
- **`skills`** — Required array of unique strings with at least one and at most
  three entries. The assignment contract defines the required class composition.
- **`executionInstructions`** — Required array with one to five step objects.
  Each step requires an integer `step` of at least 1 and a string `action`; its
  string `verification` is optional. The operation owns the ordered procedure.
- **`expectedOutput`** — Required string describing the precise `Deliverable`
  payload.
- **`verificationCoverage`** — Required object with an `observable` array of at
  least one unique string. Its `coverage` value is optional and, when present,
  must be `complete`, `partial`, or `unknown`.
- **`dependencies`** — Required array of unique edge objects. Each edge requires
  a schema-valid `taskId`; its non-empty string `reason` is optional.
- **`antiPatternSignals`** — Required array of unique strings. Values must come
  from the schema's declared signal enum.
- **`purposeOutputAlignment`** — Required object with both `status` and
  non-empty string `evidence`. `status` must be `aligned`, `needs-review`, or
  `not-aligned`.

## Optional TaskPacket Fields

- **`verification`** — Optional array of unique strings. If present, it must
  contain at least one item.
- **`couplingRationale`** — Optional object. It requires non-empty string values
  for `rationale`, `sharedResult`, and `verification`; the non-empty string
  `group` is optional.
