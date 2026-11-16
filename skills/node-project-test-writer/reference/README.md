# Reference Index

This index routes from a question to the reference page that answers it for test-only
work in existing TypeScript Node.js and Bun projects. It is an index only: it carries no
procedure, permission, delegation, sequence, edit, approval, or completion claim, and it
selects no runner, runtime, coverage target, or assertion count.

## Route By Question

- [Test Design And Measurement](test-design-and-measurement.md) — what does the test
  prove, what does a test double leave untested, and does the assertion detect a wrong
  contract result? The discriminating clues are a doubtful expected value or oracle, a
  mocked seam whose real boundary is unnamed, and an assertion that would pass for a
  wrong result.
- [Collection, Isolation, And Coverage](collection-isolation-and-coverage.md) — why was
  this test omitted from the run, does this process case leak state, and why did coverage
  change after a test move? The discriminating clues are a discovery pattern, root, or
  filter, shared process or working-directory state, a CLI exit status or output stream,
  and a coverage percentage or denominator.

## Limits And Boundaries

Runner behavior on both pages is version- and configuration-specific: test-file
patterns, isolation defaults, process boundaries, mocking facilities, and coverage
reporting depend on the installed runner and runtime and on the project's own
configuration. Verify those details against the target project; a page's documented
behavior is not evidence for another version, runtime, or project.

The scope is TypeScript test files, fixtures, helpers, and suite layout in existing
Node.js and Bun projects; JavaScript-only or mixed-language test work is excluded and
reported out of scope. Collection, isolation, process cases, and coverage interpretation,
including the canonical coverage-drop diagnosis, stay on
[Collection, Isolation, And Coverage](collection-isolation-and-coverage.md); oracles,
double fidelity, and assertion strength stay on
[Test Design And Measurement](test-design-and-measurement.md). A test that exposes a
production defect is reported to `node-project-writer` with its failing assertion and is
not repaired under test-only work; repository `scripts/node/` tests and packed artifact or
installed-consumer questions stay on their own routes. Nothing here selects or relies on
Vite, and no command sequence here forms an implicit pipeline.
