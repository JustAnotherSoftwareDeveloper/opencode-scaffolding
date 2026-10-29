# Skill Cross-References

## Syntax

Write a cross-skill reference as one inline-code span: the canonical skill name,
a space, `->`, a space, and the destination. The destination is either a Markdown
document path relative to the loaded skill's base directory or a heading fragment
in the loaded entry point. A document path may also include a heading fragment.

Use concrete names and paths, not unresolved placeholders. Examples:

- `skill-authoring-guide -> reference/frontmatter-rules.md`
- `task-contract -> reference/atomicity-and-alignment.md#verification-alignment`
- `customize-opencode -> #core-contract`

The first example selects a document owned by the named documentation skill. The
second selects a section in a document owned by the named skill. The third selects
a section of the content returned by the skill tool; it does not instruct filesystem
inspection of `SKILL.md`.

## Resolution

1. Reconcile the canonical skill name and class with the applicable skill inventory
   or collector winner. Do not guess an owner from a similar name.
2. Load that skill through the skill tool before relying on its guidance. A previous
   successful load in the same invocation suffices. Reading `SKILL.md` from the
   filesystem does not satisfy this step.
3. For a document destination, resolve its path from the loaded skill's base directory
   and read the needed document explicitly. Keep the target within that workspace;
   reject absolute paths, traversal, missing documents, and missing heading fragments.
4. For a heading-only destination, use the corresponding section of the loaded
   content. Do not replace the load with a file read.
5. Report a missing skill, failed load, or unavailable required destination honestly.
   Block the dependent work when that failure prevents its result or verification.

## Authority

Planning and documentation loads provide passive, non-transitive context. Following
a reference does not assign an operation, execute a workflow, authorize writes or
delegation, or prove completion. A reference to another skill requires that skill's
own explicit load; it does not load transitively. Preserve the assigned operation
owner and the calling workflow's selection, scope, and failure rules.

Use ordinary relative Markdown links for documents inside the current skill workspace.
Do not use relative Markdown hyperlinks into sibling skill directories. Use this
skill-to-document syntax for cross-skill guidance so the required load is explicit.
