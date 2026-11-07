# Reference Index

Choose the module by the question or symptom. If a case crosses domains, use each
canonical home rather than copying its technical guidance.

- [Project context and layout](project-context-and-layout.md) — Is checkout execution masking a broken installed package, and what does declared support mean?
- [Source and API](source-and-api.md) — Is a failure part of the public contract, and can a timed-out request be replayed safely?
- [Static quality](static-quality.md) — Why did formatting leave imports unsorted, or did an excluded file still get checked?
- [Testing and coverage](testing-and-coverage.md) — Why did fixture cleanup not run, or did the coverage denominator change?
- [Environment and dependencies](environment-and-dependencies.md) — Does the lock match metadata, and is a requirement for users or only development?
- [Distribution artifacts](distribution-artifacts.md) — Why does an installed wheel lack a module or resource that exists in the checkout?
- [Secure configuration and data handling](secure-configuration-and-data-handling.md) — Can a masked value still escape through a serializer or diagnostic?
- [Logging and observability](logging-and-observability.md) — Why is one event emitted twice, or why did a custom field disappear?
- [Async and concurrency](async-and-concurrency.md) — Was a coroutine scheduled, is a queue saturated, or did cancellation stop the underlying work?

## Cross-Skill Boundary

General source conventions belong to the separate `python-source-style-guide`. When
that subject is material, explicitly load
`python-source-style-guide -> reference/python-source-style-guide.md`; do not use a
relative hyperlink into a sibling skill. Reading a passive reference does not transfer
workflow, write, validation, or completion authority.
