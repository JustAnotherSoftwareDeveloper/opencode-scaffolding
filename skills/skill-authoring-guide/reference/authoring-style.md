# Selection Profile Style

Use imperative, active prose and exact field names. Keep one decision per sentence.
Use one H1 per file, Title Case headings, ordered lists for procedures, and bullets for
rules. Use fenced YAML for metadata examples. Keep examples short and contrastive.

Choose prose structure by meaning:

- Use bullets for peer rules that readers may locate independently.
- Use ordered lists only when correctness depends on sequence.
- Use paragraphs for causal, definitional, transitional, or tightly connected
  reasoning.
- Use definition lists for term-and-definition material.
- Use subsection headings for concerns that need separate review.

Do not use Markdown tables in filled content. Do not create an accuracy or comparison
exception; use the semantic forms above instead.

Describe `selection` as evidence for direct selection. Name the six tag groups exactly:
`actions`, `inputs`, `outputs`, `topics`, `environments`, and `constraints`. Explain
`role`, `use_when`, `not_for`, and `supports` in their directional meanings.

Do not describe cues, signatures, facets, registries, rankers, renderers, compatibility
routing, popularity, or scoring. Do not make a heading or tag restate the skill name.
Put detailed rules in reference files and keep `SKILL.md` as an index.
