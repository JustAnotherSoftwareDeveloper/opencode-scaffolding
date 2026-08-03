# Migration Guide

Migrate each active skill directly to the current profile. Do not preserve the
old metadata shape as compatibility data.

1. Inventory active skill `SKILL.md` files and identify historical artifacts that
   must remain unchanged.
2. Replace obsolete frontmatter with `name`, `description`, `selection`, and
   `class`.
3. Set the role and smallest sufficient grouped tags from the skill's owned
   request, inputs, and outputs.
4. Rewrite conditions and support targets in direct-selection vocabulary.
5. Remove old routing, registry, scoring, location, version, and compatibility
   migration advice. Do not migrate template-library content in this workflow.
6. Validate the full active inventory and inspect for stale obsolete-field or
   facet references.

Historical analyses and reports may be preserved as historical artifacts, but
they are not active guidance and must not be used to construct profiles.
