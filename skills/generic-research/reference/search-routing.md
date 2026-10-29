# Search Routing

## EXA First

Use the EXA tools exposed in the current invocation; do not infer availability from configuration alone.

1. Call `exa.web_search_exa` with the required `query` and `objective` inputs. Set `query` to the focused research question or subquestion and `objective` to the source types and evidence needed. Use `numResults` only when useful; it is optional.
2. Inspect the rendered search results. They may show titles, URLs, publication dates, authors, and highlights; fields may be absent or shown as `N/A`. Treat results and highlights as discovery aids, not proof.
3. Select relevant source URLs and call `exa.web_fetch_exa` with required `urls`; use optional `maxCharacters` when needed. Inspect the returned rendered page text and record the actual title, URL, and available metadata. Do not depend on a stable JSON response schema or import fields from the separate Exa REST API.

The observed EXA calls succeeded in one session. This supports the described interaction, not guaranteed availability, authentication mode, uptime, quota, or service terms. Search output did not expose a request ID or provider timestamp; fetched pages did not expose those fields either. Record missing metadata as unavailable. Distinguish a page's publication date from its current content freshness.

## Bounded Fallback

Use the observed fallback only if `functions.websearch` is exposed in the current invocation. Its verified input is one required `query` string.

Call it once for an observable EXA search or page-fetch failure, zero search results, or a specific unmet mandatory capability. After inspecting EXA sources, make at most one targeted fallback attempt for each task-critical claim that still lacks task-suitable support. A task-critical claim is necessary to answer the question or materially relevant to the stated use.

Record the claim and the task-specific reason the inspected EXA evidence is insufficient. Fewer-than-requested EXA results or a missing date alone do not trigger fallback.

The observed fallback returned rendered listings with titles, URLs, publication/author labels, and highlights, but no provider identity, route binding, request ID, timestamp, or verified structured result schema. The actual provider is unknown. Do not call it Google, Exa, or another named provider; do not infer freshness, coverage, quotas, privacy, retention, or retry behavior. If `functions.websearch` is absent, report the fallback as unavailable rather than inventing a substitute interface.

Fallback snippets remain discovery aids. Inspect a source page and its supporting passage through an available page-reading tool before relying on it. The verified EXA fetch interface can inspect known URLs when EXA fetch is available. If no page-reading method is available for a fallback result, do not present its excerpt as inspected evidence; report the evidence gap. Do not retry a failed fallback or repeat a fallback attempt for the same task-critical claim.

## Provenance Record

Record each attempted search in the bundle's search log as specified in [research artifacts](research-artifacts.md):

- tool name, query, attempt order, and the reason for the route;
- call outcome and result count only when actually visible;
- each used source's title and URL, plus publication date and author only when displayed;
- the page-reading tool and inspected passage or location for evidence used in a claim; and
- unavailable fields, including unknown fallback provider identity and metadata not surfaced by the tool.

Do not claim complete web coverage, comparative recall, or source authority from ranking or snippets.
