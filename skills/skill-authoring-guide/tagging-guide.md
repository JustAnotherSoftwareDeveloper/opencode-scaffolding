# Grouped Selection Tag Guide

Author grouped selection tags from the request-to-owner relationship.

## Authoring Procedure

1. State the request the skill owns, including its action, inputs, outputs, and constraints.
2. List the nearest neighboring skills and their owned requests.
3. Add only grouped tags whose presence or absence could change selection.
4. Add concise `use_when`, `not_for`, or `supports` values only when they clarify ownership.
5. Stop when the profile distinguishes the skill from its nearest neighbors.

## Quality Tests

Apply every test to every tag and condition.

- **Task-grounded:** Tie the value to request intent, input, output, constraint, environment, or repository language.
- **Discriminative:** Removing the value should make a neighboring skill harder to distinguish.
- **Atomic:** Express one concept per value.
- **Stable:** Prefer request concepts over implementation details.
- **Discoverable:** Use request language or a concise alias.
- **Non-redundant:** Remove synonyms and weaker duplicates.
- **Scoped:** Avoid values broad enough to select unrelated skills.

Use the six supported groups: `actions`, `inputs`, `outputs`, `topics`,
`environments`, and `constraints`. Keep aliases in the profile as lookup
vocabulary; they do not create additional tags.

## Contrastive Examples

### Software

- Choose `actions: [create]`, `inputs: [script requirements]`, and
  `outputs: [Node script]` for a skill that owns deterministic Node script creation.
- Add `environments: [CLI]` only when CLI behavior separates it from a library-only generator.
- Reject `typescript` when it merely describes an implementation detail shared by competing generators.

### Document And Business

- Choose `actions: [analyze]`, `topics: [contract]`, and `outputs: [risk findings]` for a contract review skill.
- Choose `actions: [approve]`, `topics: [expense]`, and `environments: [finance workflow]` for an approval skill.
- Reject `business` or `document` because those cues do not separate either owner from neighboring analysis or approval skills.

### Scientific And Repository-Specific

- Choose `actions: [fit]`, `topics: [calibration model, sensor series]` when those values distinguish model fitting from data cleaning.
- Reject a local value that duplicates a built-in value under another name or describes one ticket number.

## Direct Selection Evaluation

Evaluate the signature against owner tasks, nearest-neighbor tasks, unrelated tasks, paraphrases, and tasks with little lexical overlap.

- Confirm owner tasks select the skill directly.
- Confirm neighbor tasks select the distinct owner when the differentiating value changes.
- Confirm unrelated tasks do not select the skill from broad tags.
- Confirm aliases improve discovery without changing canonical identity.
- Record exact-set accuracy and review low-overlap paraphrases.

## Hard Rejections

Reject a profile that relies on generic filler, implementation-only details, or a
value that fails any quality test.
