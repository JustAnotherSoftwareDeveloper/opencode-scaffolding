# Skill Factory Create And Update Workflow

## Create Workflow

1. Select the class from the authoring guide and load the matching template.
2. Write `name`, `description`, `schema_version`, structured `cues`, `relationships`, and `class` frontmatter.
3. Identify owned tasks and nearest competing skills before selecting cues.
4. Declare repository-local facets and values in a namespaced registry.
5. Write the body using the class and authoring-style rules.
6. Validate metadata, relationships, registry resolution, and Markdown syntax.

## Update Workflow

1. Load maintenance and authoring guidance.
2. Read every existing file in the target skill directory.
3. Preserve content outside the requested change.
4. Re-derive affected cues from owned tasks and nearest competitors.
5. Migrate aliases, hierarchy, and lifecycle metadata through the registry.
6. Re-run the shared validation and routing evaluation.

## Registry Rules

- Define facet meaning, value shape, canonical values, aliases, parent or child relations, and lifecycle status.
- Permit repositories to add namespaced declarations without core changes.
- Reject built-in redefinitions, foreign namespaces, and same-scope canonical collisions.
- Treat deprecated values as migration metadata, not new routing cues.

## Validation

- Confirm YAML parses and the class is valid.
- Confirm every executable owner has one primary operation.
- Confirm every cue passes task grounding, discrimination, atomicity, stability, discoverability, non-redundancy, and scope tests.
- Confirm every facet and value resolves through the applicable registry.
- Confirm one shared result serves authoring validation, discovery, lexical scoring, and model rendering.
- Confirm the renderer safety cap is the only cardinality safeguard.
- Run `bun run --cwd ~/.config/opencode/scripts/node lint:md -- <path>` for every modified Markdown file.
- Search modified documentation for obsolete count, popularity, implementation, and metadata-shape guidance.
