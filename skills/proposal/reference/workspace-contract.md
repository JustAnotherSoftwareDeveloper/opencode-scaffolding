# Workspace Contract

This contract governs newly created or intentionally revised proposal workspaces.
It is forward-only: it does not rewrite historical workspaces or provide legacy
heading aliases or other compatibility behavior.

## Workspace boundaries

Use this layout for a proposal workspace:

```text
.proposals/<epoch-ms>-<summary-slug>/
  PROPOSAL.md
  implementation.md
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

The workspace contains a decision document and, when implementation detail applies,
one separate implementation overview. It does not contain import commands,
assignments, estimates, or runbook steps.

## Canonical artifacts

`PROPOSAL.md` is the canonical decision artifact. It contains the nine canonical
decision sections—Summary, Problem and rationale, Scope, Criteria, Alternatives and
trade-offs, Selected direction, Design constraints, Open owner choices, and
Acceptance criteria—plus Supporting sources. Link `implementation.md` from the
selected direction when that file exists.

`implementation.md` is the canonical implementation overview. Its substantive body
is limited to concrete artifact or behavior changes, evidence-supported dependencies,
decision gates, and validation criteria. Use an H2 for each affected area and an H3
for each concrete change; name the affected artifact, interface, workflow, or policy.
Do not turn it into a generic lifecycle document or place decision rationale that
belongs in `PROPOSAL.md` there.

## Frontmatter and readiness

Use YAML frontmatter as the only workspace metadata store. `PROPOSAL.md` MUST define
`title`, `slug`, `created`, `created-at`, `status`, `readiness`, `decision-owner`,
and `source-documents`. List every copied source by its workspace-relative path.
`implementation.md` MUST define `title`, `proposal`, `slug`, `created`, and `status`.
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

Every copied source MUST appear exactly once in **Supporting sources**, using a
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

Validation MUST preserve the boundary between `PROPOSAL.md` and `implementation.md`.
It MUST reject commands, task assignments, estimates, owners, and runbook detail in
the implementation overview. These restrictions are contract rules, not optional
authoring advice.
