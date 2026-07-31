# Routing Signature Guide

Author routing cues from the task-to-owner relationship.

## Authoring Procedure

1. List the tasks the skill owns, including the operation, subject, constraints, and expected outcome that recur in its trigger.
2. List the nearest competing skills and the task requests that belong to each competitor.
3. Compare the owned and competing task sets.
4. Add only cues whose presence or absence materially changes routing.
5. Mark one owned `operation` cue as primary for every executable owner skill.
6. Stop when the signature is sufficient to distinguish the skill from its nearest competitors.
7. Resolve every cue through the built-in or repository-local registry before publishing.

## Quality Tests

Apply every test to every cue.

- **Task-grounded:** Tie the cue to requested intent, input, output, constraint, audience, environment, or repository language.
- **Discriminative:** Remove the cue and verify that a plausible neighboring skill becomes harder to distinguish.
- **Atomic:** Express one routing concept per entry; split independent concepts.
- **Stable:** Keep the cue when ordinary implementation details change; retain implementation cues only when selection requires that implementation.
- **Discoverable:** Use request language, file language, repository vocabulary, or a declared alias.
- **Non-redundant:** Remove synonyms, restatements, aliases entered as separate cues, and weaker duplicates.
- **Scoped:** Avoid cues broad enough to select unrelated skills or narrow enough to describe one unrepeatable instance.

Facets organize evidence. They do not form a closed taxonomy. Use `operation`, `subject`, `outcome`, `interface`, `environment`, and `constraint` when they fit; introduce another facet when the task evidence requires it. Require only the primary operation for an owner skill.

## Registry Extensions

Declare repository vocabulary in a local registry owned by the repository.
Use one of the discovered repository filenames: `skill-facets.json`, `.skill-facets.json`, `.opencode/skill-facets.json`, or `.opencode/facets.json`.
Declare exactly one registry file at a repository scope; multiple recognized files at the same scope are an error.
Discovery uses the nearest declaration up to the Git repository root and never inherits a registry from a parent repository.

```json
{
  "namespace": "acme",
  "facets": [
    {
      "name": "release-train",
      "meaning": "Release stage that changes task ownership",
      "values": [
        {
          "value": "candidate-freeze",
          "aliases": ["release freeze"]
        }
      ]
    }
  ]
}
```

- Give each local facet a namespace, routing meaning, value shape, examples, aliases, and lifecycle status.
- Reuse a built-in canonical value when its meaning matches; do not create a local synonym.
- Keep local values under the repository namespace.
- Reject a declaration that redefines a built-in facet, claims a foreign namespace, or collides with an existing canonical value at the same scope.
- Treat aliases as lookup vocabulary, not additional cues.
- Represent parent and child relations explicitly; do not treat hierarchy as synonymy.
- Mark deprecated facets and values with an active replacement and migration date; reject new use after the declared cutoff while resolving existing metadata only through the published migration rule.
- Keep each registry within 128 facets, each facet within 256 declared values, and registry lists within 32 entries; these are safety ceilings, not completeness targets.
- Keep `value_shape` expressions within 256 characters and free of lookarounds, backreferences, or quantified groups so validation cannot trigger unbounded backtracking.

The current machine contract supports `status: deprecated` plus a required declared, active `replacement` for facets and values.
Record migration dates in repository documentation; the schema does not interpret dates.

Adding a valid namespaced facet or value requires a registry declaration and validation only. It does not require a core-schema or core-code change.

## Contrastive Examples

### Software

- Choose `operation:generate-node-script` for a skill that owns deterministic Node script creation, not for every skill that mentions Node.
- Add `interface:cli` only when CLI behavior separates it from a library-only generator.
- Reject `typescript` when it merely describes an implementation detail shared by the competing generators.

### Document And Business

- Choose `operation:analyze-contract` and `outcome:risk-findings` for a contract review skill.
- Choose `operation:approve-expense` and `interface:finance-workflow` for an approval skill.
- Reject `business` or `document` because those cues do not separate either owner from neighboring analysis or approval skills.

### Scientific And Repository-Specific

- Choose `operation:fit-calibration-model` and `subject:sensor-series` when those cues distinguish model fitting from data cleaning.
- A repository can declare `acme:release-train` with values such as `candidate-freeze` when that lifecycle vocabulary routes work inside the repository.
- Reject a local value that duplicates a built-in value under another name or describes one ticket number.

## Routing Evaluation

Evaluate the signature against owner tasks, nearest-neighbor tasks, unrelated tasks, paraphrases, and tasks with little lexical overlap.

- Confirm owner tasks rank the skill above competitors.
- Confirm neighbor tasks route to the distinct owner when the differentiating cue changes.
- Confirm unrelated tasks do not select the skill from broad facets.
- Confirm aliases improve discovery without changing canonical identity.
- Record precision, recall, exact-set accuracy, context clipping, and token impact.
- Treat cue frequency as a diagnostic for neighbor review, never as an invalidation rule.

## Hard Rejections

Reject a signature that relies on category completion, generic filler, global popularity, implementation-only details, undeclared vocabulary, or a cue that fails any quality test.
