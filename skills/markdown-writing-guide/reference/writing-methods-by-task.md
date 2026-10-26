# Writing Methods By Task

The [canonical writing-quality reference](./writing-quality.md) governs cross-cutting choices about reader fit, evidence, and format. These optional methods and examples address particular tasks; use only what helps the reader, not as a checklist. Publisher guidance linked below describes those publishers' practices, not proven effects or universal rules. Examples marked hypothetical are illustrative, not factual claims.

## Procedures

At the point of action, include the context and detail needed for a reader to take the step and recognize what follows. Depending on the task, that may mean a goal, command or placeholder explanation, expected result, rationale, or a clear indication that a step is optional. Split an unwieldy step or link to a repeated procedure rather than making every step carry every detail. Google's [developer-procedure guidance](https://developers.google.com/style/procedures) describes these as choices for its technical documentation, not general Markdown requirements.

**Hypothetical contrast:**

- **Too thin:** “Export the report.”
- **At the point of action:** “To save a CSV copy, run `tool export --format csv`. The command writes `report.csv` in the current directory. This step is optional if you only need the on-screen report.”

The second version supplies a goal, action, expected location, and optionality because those details help the imagined reader complete and verify this task. A real procedure should use its actual command and behavior; do not infer output or prerequisites from the example.

## Recommendations

Make the force of a statement clear in its own context: is it a binding requirement, advice, or one available option? When recommending action, give enough support to connect the evidence to an actor and feasible next action. Do not adopt a universal modal-word policy or a fixed recommendation template. Google's distinctions among requirements, recommendations, and options reflect its [prescriptive developer-documentation guidance](https://developers.google.com/style/prescriptive-documentation); SMART criteria and audit-specific wording belong to their respective evaluation and audit settings.

**Hypothetical contrast:**

- **Vague:** “The team should improve onboarding.”
- **Recommendation:** “In this hypothetical pilot review, five support cases involved the same setup step. We recommend that the onboarding team add an example at that step before the next pilot; estimate implementation effort before committing to a release date.”

The example labels its invented evidence and action as a recommendation, not a requirement. A stronger commitment would need support from the relevant policy, evidence, authority, and implementation constraints.

## Analysis And Comparison

For analytical prose, distinguish observed results from interpretation when that difference matters, and explain method, uncertainty, or scope limits when they affect what readers may conclude. A comparison can contextualize a result when a suitable baseline exists, but do not force one or imply causality the evidence cannot establish. Government analysis and report-writing guidance offers examples for data and report settings ([Government Analysis Function](https://analysisfunction.civilservice.gov.uk/policy-store/writing-about-data/), [Department for Education](https://assets.publishing.service.gov.uk/media/67489b9d5ba46550018cebd8/Research_reports_guidance.pdf), and [GOV.UK evaluation guidance](https://www.gov.uk/guidance/use-your-results-evaluating-digital-health-products)); it does not prescribe one report structure for all prose. These baseline comparisons differ from the option-choice example below.

**Hypothetical before-and-after example:**

- **Overclaim:** “The release made the service more reliable.”
- **Evidence-calibrated:** “In this hypothetical sample, recorded failures fell from 12 of 100 requests before the release to 8 of 100 afterward. That is a four-percentage-point decline in the observed samples; without a suitable comparison or other causal evidence, these figures alone do not show that the release caused it.”

The second version names the comparison, states the observation, and limits the inference. In another task, a relevant comparison might be a prior period, another group, or a target—or no comparison may be suitable. Keep findings, interpretations, and recommendations distinct when blending them would hide the reasoning.

### Comparing Options

When a reader must choose among alternatives, identify the decision and the criteria that matter to it. Compare options on a common basis only where the evidence permits; make material trade-offs visible and state uncertainty or missing evidence that could change the choice. This is an optional editorial method, not a publisher-prescribed framework; the sources cited above address contextualizing results against baselines, not a universal method for ranking alternatives. No matrix, single score, or winner is required.

**Hypothetical option comparison:** Suppose a team is choosing between two proposed approaches. Approach A would take less effort to set up but allow fewer local adjustments; approach B would allow more adjustments but require more ongoing maintenance. Compare those trade-offs against the team's actual priorities. If its maintenance capacity is uncertain, state whether that uncertainty could change the choice; recommend an approach only if the priorities and available evidence support doing so.

## Reference Entries

For lookup-oriented reference, answer likely questions about the specific element's behavior and boundaries rather than restating its name or type. Defaults, conditions, return behavior, prerequisites, errors, and exceptions are useful only where they apply. Microsoft's [reference-documentation guidance](https://learn.microsoft.com/en-us/style-guide/developer-content/reference-documentation) and Google's [API-reference guidance](https://developers.google.com/style/api-reference-comments) concern software/API material; their fields are not a template for unrelated prose.

**Hypothetical API-entry contrast:**

- **Thin:** `retryLimit`: integer.
- **More useful lookup detail:** `retryLimit` is an integer from 0 to 5; the default is 0, which disables retries. A positive value allows that many retries after a timeout. Permission errors are not retried.

The added detail makes the fictional field's default, range, behavior, and exception findable. Include only behavior verified for the actual API; link to a tutorial for broader conceptual or procedural explanation when that better serves the reader.

## Layered Detail And Document Forms

When one surface cannot serve distinct reader needs without hiding the main point or omitting needed depth, consider a concise summary with technical detail in the body or an appendix, a link to deeper material, or separate outputs for genuinely different audiences. Keep essential meaning on the main path and make optional depth findable. Public-sector report guidance describes such options in its own settings ([Department for Education](https://assets.publishing.service.gov.uk/media/67489b9d5ba46550018cebd8/Research_reports_guidance.pdf) and [ATSDR](https://www.atsdr.cdc.gov/pha-guidance/putting_it_all_together/tips-for-preparing-written-documents.html)); it does not mean every document needs an appendix or multiple versions.

**Hypothetical choice:** A public summary might state the principal finding and its material limitation, while a linked technical appendix explains sampling and calculations needed by specialist readers. If the added layer would not answer a distinct reader need—or would make a key qualification harder to find—keep the explanation together instead.
