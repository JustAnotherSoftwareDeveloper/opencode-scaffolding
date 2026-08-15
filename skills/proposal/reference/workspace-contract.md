# Workspace Contract

This contract governs newly created or intentionally revised proposal workspaces.
It is forward-only: it does not rewrite historical workspaces or provide legacy
heading aliases or other compatibility behavior.

## Workspace boundaries

Use this layout for a proposal workspace:

```text
.proposals/<epoch-ms>-<summary-slug>/
  PROPOSAL.md
  01-summary.md
  02-problem-and-rationale.md
  03-scope.md
  04-criteria.md
  05-alternatives-and-trade-offs.md
  06-selected-direction.md
  07-design-constraints.md
  08-open-owner-choices.md
  09-acceptance-criteria.md
  10-implementation.md
  11-supporting-sources.md
  analysis/
  research/
  requirements/
  design/
  notes/
  other/
```

Create only category directories that contain copied source documents. Require an
epoch-millisecond prefix and a lowercase kebab-case summary slug. Copy each supplied
source into its declared category, preserve its filename unless a deterministic
collision suffix is required, and reject a collision that cannot preserve both
documents distinctly. Follow a symbolic link only when its resolved target is a
regular file inside `$CWD`.

The workspace contains an index, one file per canonical decision section, a source
index, and, when implementation detail applies, one separate implementation overview.
It does not contain import commands,
assignments, estimates, or runbook steps.

## Canonical artifacts

`PROPOSAL.md` is the canonical workspace entry point and metadata owner. Its body is
an ordered index linking the canonical numbered files. It MUST NOT duplicate decision
prose from those files.

Each canonical decision section owns exactly one numbered file. The filename, H2
heading, and index label MUST agree. `11-supporting-sources.md` is the canonical
source index. Substantial conditional detail may use an additional numbered companion
file only when `PROPOSAL.md` and the governing canonical section both link it.

Link `10-implementation.md` from `06-selected-direction.md` and from `PROPOSAL.md`.

`10-implementation.md` is the canonical implementation overview. Its substantive body
is limited to concrete artifact or behavior changes, evidence-supported dependencies,
decision gates, and validation criteria. Use an H2 for each affected area and an H3
for each concrete change; name the affected artifact, interface, workflow, or policy.
Do not turn it into a generic lifecycle document or place decision rationale that
belongs in the canonical section files there.

## Frontmatter and readiness

Use YAML frontmatter as the only workspace metadata store. `PROPOSAL.md` MUST define
`title`, `slug`, `created`, `created-at`, `status`, `readiness`, `decision-owner`,
and `source-documents`. List every copied source by its workspace-relative path.
`10-implementation.md` MUST define `title`, `proposal`, `slug`, `created`, and `status`.
New workspaces start with `status: draft` and `readiness: not-ready`.

`status` is lifecycle metadata; `readiness` is an evidence-and-decision-closure
assessment. They MUST be validated independently. Allowed readiness values are:

- `not-ready`: the decision path or evidence is not yet reviewable.
- `review-ready`: the path and evidence are reviewable and all open owner choices
  are resolved.
- `decision-ready`: blocking evidence gaps are resolved and the remaining decision
  record is explicit and ready for an owner decision.

Readiness may move between these values only when the corresponding conditions are
true. Readiness is not approval and MUST NOT silently become acceptance. Acceptance
is recorded separately by an authorized owner, either manually or when a plan is
triggered from the proposal; this contract does not add an `accepted` readiness
value or speculative checker roles and timestamps.

## Sources and citation identity

Every copied source MUST appear exactly once in `11-supporting-sources.md`, using a
descriptive relative Markdown link and its workspace-relative path. That entry is
the canonical identity for the source. A claim may also use the same source's
Chicago note, but the source MUST NOT be duplicated under another identity.

Use Chicago notes and bibliography metadata for copied internal sources and external
research. Include available author, title, site or publisher, date, URL or path, and
an access date when needed; never fabricate missing facts. Internal sources retain
their descriptive relative copied-source link. External sources use their stable URL.
Citation completeness is validated separately from evidence strength or applicability.

## Evidence and owner questions

Every material claim affecting the decision, scope, requirement, acceptance criterion,
risk, or option rejection MUST have a supporting citation or an explicit label:

- `Assumption: <statement>` identifies an unverified claim.
- `Evidence Gap: <missing evidence>` identifies unavailable material evidence.
- `Open Question: <question>` is reserved for an unresolved decision required from
  the responsible engineer, and MUST state the consequence of deferring it.

Questions answerable through source review, analysis, research, testing, or discovery
MUST be resolved before drafting. Unavailable evidence is an evidence gap, not an
owner question. Record material objections and their dispositions with the selected
direction or the rationale for the decision.

## Validation-observable restrictions

Validation MUST be able to reject missing or invalid readiness values, inconsistent
readiness conditions, incomplete internal or external citation metadata, duplicate
source identities, unsupported material claims, unlabeled evidence gaps, researchable
open questions, unresolved owner choices marked `review-ready`, placeholders, legacy
heading aliases, and generic lifecycle implementation headings.

Validation MUST preserve the boundary between the indexed decision-section files and
`10-implementation.md`. It MUST reject a monolithic `PROPOSAL.md`, missing or misordered
canonical files, mismatched filenames and headings, duplicate section prose, and
unindexed companion files.
It MUST reject commands, task assignments, estimates, owners, and runbook detail in
the implementation overview. These restrictions are contract rules, not optional
authoring advice.
