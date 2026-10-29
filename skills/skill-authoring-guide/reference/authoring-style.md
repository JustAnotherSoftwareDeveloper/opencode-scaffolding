# Selection Profile Style

Use imperative, active prose and exact field names. Keep one decision per sentence.
Use one term consistently for each concept. Omit filler and tutorial preambles.
Use one H1 per file, Title Case headings, ordered lists for procedures, and bullets for
rules. Use fenced YAML for metadata examples. Keep examples short and contrastive.

Choose prose structure by meaning:

- Use bullets for peer rules that readers may locate independently.
- Use ordered lists only when correctness depends on sequence.
- Use paragraphs for causal, definitional, transitional, or tightly connected
  reasoning.
- Use definition lists for term-and-definition material.
- Use subsection headings for concerns that need separate review.

Do not use Markdown tables in filled content. Do not make table exceptions for accuracy
or comparison; use the semantic forms above instead.

`TABLE-001` has one exception, approved by the user, because `display-tasks` requires
both a concrete format example and a single-table renderer output. It applies only while
those requirements remain in force, and covers only the exact fenced table example under
`Output Format` in `skills/display-tasks/SKILL.md` and that skill's required single
Markdown table with no surrounding commentary. It does not permit any other table in
`display-tasks`, another skill, or proposal content.

Describe `selection` as evidence for direct selection. Name the six tag groups exactly:
`actions`, `inputs`, `outputs`, `topics`, `environments`, and `constraints`. Explain
`role`, `use_when`, `not_for`, and `supports` in their directional meanings.

Do not describe cues, signatures, facets, registries, rankers, renderers, compatibility
routing, popularity, or scoring. Do not make a heading or tag restate the skill name.
Put detailed rules in reference files and keep `SKILL.md` as an index.
