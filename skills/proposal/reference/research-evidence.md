# Bounded Research Evidence

Use this local method before proposal drafting when a recommendation materially
depends on external, comparative, or prior-art evidence that the supplied sources do
not already cover. The method makes the basis and limits of a decision reviewable; it
does not define an industry standard.

## Trigger And Handoff

Treat research as material when relevant findings could reasonably change the
recommendation, the options considered, decision confidence, or the scope or conditions
of the choice. Judge this against the particular decision, not a fixed source count,
score, source hierarchy, or sufficiency threshold.

- Research is not needed when the supplied sources already support the decision, or
  when additional background would not affect the decision or its explanation. Do not
  create an empty packet.
- Examples of potentially material evidence include current compatibility or support
  facts that could change a technology choice, or prior-art evidence that could change
  whether a proposed approach is novel or appropriate.
- Examples that are not material include additional background that does not alter the
  decision boundary, or rechecking a point already adequately covered by supplied
  sources when no plausible finding would change the choice.

The proposal command accepts research only as a caller-supplied, persisted packet with
explicit paths to all four files below. Proposal authoring does not perform, delegate,
or substitute for research. If material research is absent or its packet is incomplete,
stop before creating a proposal workspace or drafting; report what is missing and ask
the caller to complete and persist the research separately, then resume with explicit
packet paths. Do not treat search snippets or an unpersisted conversational summary as
completed evidence. A complete packet may report unavailable or unresolved evidence;
carry that result forward as an `Evidence Gap:` and do not imply it supports a
conclusive recommendation. A material gap that prevents decision readiness remains
blocking under the [workspace contract](./workspace-contract.md).

## Frame The Question

Before searching, record:

- The decision question and the packet's intended use.
- The decision boundary: relevant options, topic, population or system, jurisdiction,
  and exclusions where applicable.
- An as-of or time boundary, including which source versions or dates matter.
- Focused subquestions that resolve the decision question.
- What evidence could change the recommendation, confidence, scope, or conditions.

Keep the inquiry proportionate to this decision. State the boundary and important
omissions so a reader can see what the findings do and do not address. Do not turn a
bounded inquiry into a claim of exhaustive coverage.

## Inspect And Appraise Sources

Use searches to discover candidate sources, not as evidence by themselves. Inspect the
source itself and record the passage, section, page, or other location supporting each
material claim. Prefer authoritative primary sources when they are suitable for the
question, but assess authority in relation to the particular claim; do not treat any
source type as a universal rank order.

For each used source, record its stable source ID, title, URL, discovery method, page-
reading method, inspected location, and author or publication date only when surfaced.
Record unavailable metadata as unavailable rather than inferring it. For each source,
assess:

- **Fit:** How directly the source addresses this question, decision, setting, and
  time boundary.
- **Authority:** Why this source can support the particular claim, including whose
  policy, practice, or scope it represents.
- **Currency:** Whether its publication/update date and mutable status suit the claim.
- **Limitations:** Missing context, access limits, narrow scope, self-reported
  information, mutable content, or other reasons not to generalize it.

Record contrary and qualifying evidence where found. Distinguish a source that is
silent from one that contradicts a claim. A search log shows where and how discovery
was attempted; it does not establish evidence quality or prove that an unlocated fact
does not exist.

## Trace Material Claims

Give each decision-driving claim a stable ID and concise wording. Identify its type:

- **Source-reported fact:** A statement directly reported by an inspected source.
- **Source-reported synthesis:** A pattern or comparison supported across identified
  sources.
- **Interpretation:** A conclusion drawn from the evidence rather than stated by one
  source.
- **Local recommendation:** A proposed choice for this decision, not an external
  convention.

For each claim, link supporting source IDs to inspected locations, record material
contrary or qualifying evidence, and state task-specific fit and limitations. Use the
answer and claim record consistently: IDs must resolve, and neither should imply more
certainty or scope than the source register supports. Label unavailable, unresolved,
or unsupported claims explicitly. Do not turn absence of found evidence into proof of
absence, or present a local choice as an external requirement. Qualify conclusions to
the actual source scope, sample, and time boundary.

## Stop And Report Gaps

Stop when each decision-driving claim has inspected support or an explicit evidence
gap, material contrary evidence and source limitations are recorded, and further
reasonably scoped research is unlikely to change the recommendation, confidence, scope,
or conditions. State why the completed scope is adequate for this decision. This is a
qualitative local stopping rule, not a numeric threshold or a claim of exhaustiveness.

If a source is unavailable or the evidence remains unsupported, record what could not
be established and why. Do not conceal the gap, inflate the claim, or keep searching
without a decision-relevant question. A packet can be structurally complete while its
findings disclose a gap; the proposal must carry material gaps forward and must not
mark itself decision-ready when a blocking gap remains.

## Persisted Packet

Persist one packet at repository-root
`.research/<unique-run-id>-<task-slug>/`, with these four Markdown files:

- `README.md` records `Question`, `Intended use`, `Scope and time boundary`, `Created
  at` using an observed timestamp or `unavailable`, `Bundle status`, and links to the
  other three records. Mark the bundle `complete` only after its files and internal
  references have been verified.
- `answer.md` records `Question`, `Scope`, `Answer or findings`, `Interpretation`,
  `Uncertainty and limitations`, and the claim IDs supporting material statements.
- `sources.md` contains the search-attempt log and source register. For every attempt,
  record its ID and order, tool, query, route reason, outcome, and visible result count
  when supplied. For each used source, record its ID, title, URL, discovery tool,
  surfaced publication date and author, page-reading tool, and inspected passage or
  location. Mark unavailable fields explicitly; do not invent tool identity, results,
  metadata, or timestamps.
- `claims.md` records each material claim's ID and wording, claim type, supporting
  source IDs and inspected locations, contrary or qualifying evidence when present,
  and task-specific fit and limitations.

Keep source and claim IDs stable across the packet. Ensure every referenced source ID
resolves in `sources.md` and the answer's claim IDs agree with `claims.md`. Verify all
four files are readable, required fields and links are present, and the answer and
claim support are persisted before marking the packet complete.

Use the active generic-research writer's safe path, unique-run, collision, and
no-overwrite rules for this bundle. The earlier proposal design described a
date/topic-slug directory; this handoff reconciles that name to the active writer's
`.research/<unique-run-id>-<task-slug>/` contract. This is a path-name update only:
retain the approved four files and their decision-relevant contents. When the packet is
used by a proposal, supply each file as an explicit source path and copy it unchanged
under its declared source category. External URLs in `sources.md` are references, not
copied-source manifest entries. The packet precedes the proposal; it is not a second
proposal or an authored companion in the proposal workspace.
