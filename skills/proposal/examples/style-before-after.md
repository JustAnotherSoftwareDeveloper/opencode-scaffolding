# Engineering writing before and after

These paired examples demonstrate precision, density, and technical scanability.
Together, the rewrites preserve technical meaning while demonstrating how to remove
robotic phrasing, add concrete detail, distinguish research gaps from owner decisions,
expose compatibility effects, and make verification observable.

## Robotic Prose

**Before**

> Performance of validation for the source path correctness condition shall be
> executed by the validation component in accordance with the workspace contract.

**After**

> The validator rejects a source path when it is not a regular file inside the
> workspace boundary.

**Why:** The rewrite names the component (`validator`), action (`rejects`), condition
(`not a regular file`), and boundary (`inside the workspace`). It removes passive
construction and empty qualifiers without losing the rule.

## Weak Implementation Detail

**Before**

> Update the lint-md program to handle new proposal format.

**After**

> `lint-md` accepts a proposal workspace directory. It reads `PROPOSAL.md`
> frontmatter with a YAML parser, checks required heading order, reconciles
> `source-documents` entries with in-document Sources, and reports each violation
> with a stable rule ID and responsible path.

**Why:** The rewrite identifies the target program, the input contract change, the
exact checks, and the diagnostic output shape. A reviewer can locate the boundary
without guessing.

## Ambiguous Uncertainty

**Before**

> Open Question: Should we validate TOC entries?

> Evidence Gap: Haven't checked what consumers link to.

**After**

> Evidence Gap: Active repository consumers of proposal index links have not been
> inventoried. This does not block review because the TOC contract is testable in
> isolation once the format is stable.

**Why:** Inspection can answer "what consumers exist," so it is a research gap, not
an owner decision. The rewrite makes the task discoverable and states whether the
gap blocks readiness.

## Hidden Compatibility Impact

**Before**

> The plan command will look for PROPOSAL.md instead of INDEX.md.

**After**

> `/plan` reads `PROPOSAL.md` frontmatter for status and readiness. Previous
> behavior searched for `INDEX.md` and `metadata.md`. Automation or aliases that
> depended on those filenames will need updating. No workspace metadata is silently
> migrated.

**Why:** The rewrite names the old path, the new path, and the explicit consequence
for callers. A reviewer can assess the migration surface without searching.

## Unverifiable Acceptance Language

**Before**

> Acceptance criteria: The format is better than before.

**After**

> Verification Criteria: A snapshot workspace with invalid frontmatter and a
> missing source exits with a validation-failure code. A valid workspace exits
> successfully.

**Why:** The rewrite replaces a subjective quality claim with observable
completion evidence. The reader does not need to agree with an assessment; they
can run the workspace.

## Evidence Boundary

These examples demonstrate information density and precision, not measured reader
outcomes. A human reviewer still judges whether a proposal's prose, structure, and
evidence are complete for its decision. Lint success does not establish readability
or comprehension.
