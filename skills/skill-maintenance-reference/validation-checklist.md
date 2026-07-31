# Validation Checklist

Verify every authored or migrated skill before publication.

## Metadata

- Confirm `name` matches the directory.
- Confirm `description` uses the class-specific trigger prefix.
- Confirm `class` is valid.
- Confirm structured cues contain canonical values and resolved facets.
- Confirm each executable owner has one primary operation.
- Confirm owner, support, and reference relationships are explicit.

## Routing Rubric

- Confirm every cue is task-grounded, discriminative, atomic, stable, discoverable, non-redundant, and scoped.
- Confirm the signature is the smallest sufficient evidence set.
- Confirm aliases are vocabulary metadata and hierarchy is explicit.
- Confirm deprecated values have replacement and lifecycle rules.

## Registry

- Confirm local facets and values use the repository namespace.
- Confirm declarations include meaning, shape, aliases, relations, and lifecycle status.
- Reject built-in redefinition, foreign namespace use, and same-scope canonical collisions.
- Confirm a valid local extension needs no core-code change.

## Runtime And Evaluation

- Run the same validator for authoring and discovery.
- Confirm lexical and model renderers consume normalized cues directly.
- Confirm the renderer safety cap protects context bounds.
- Evaluate owner, neighbor, unrelated, paraphrased, and low-overlap tasks.
- Record precision, recall, exact-set accuracy, clipping, and token impact.

## Documentation Hygiene

- Search related documentation for obsolete count, popularity, implementation, and metadata-shape instructions.
- Confirm all related documents name the same required metadata and validation behavior.
