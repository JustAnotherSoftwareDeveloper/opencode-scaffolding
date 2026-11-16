# Test Design And Measurement

This page answers three questions about a TypeScript test: what does the test prove, what does a test double leave untested, and does the assertion detect a wrong contract result. The subject is TypeScript test files, fixtures, and helpers in existing Node.js or Bun projects. Standalone JavaScript test guidance, mixed-language eligibility, and JSDoc typing of `.js` files are excluded, and a JavaScript-only request is reported as out of scope.

Design and measurement are separate evidence. A coverage percentage is a ratio over a configured source universe, so a percentage that moves after a test move is a collection and denominator question: [Collection, Isolation, And Coverage](collection-isolation-and-coverage.md) owns discovery, isolation, process cases, coverage interpretation, and the canonical coverage-drop diagnosis. This page keeps the design questions — the oracle, the fidelity of a test double, and the strength of an assertion — because each is decided from the contract rather than from a runner report.

The retained sections here are "Behavior Oracles", "Runtime, Runner, And TypeScript Boundaries", and "Evidence And Handoff". The discovery, isolation, CLI and process-case, and coverage sections that an earlier revision of this page carried now exist only on the collection page, together with the moved coverage-drop walkthrough; they are not restated or summarized here, so that procedure keeps exactly one home. "Mocked Collaborators And The Real Boundary" and "Assertion Strength" are the design sections this page adds.

## Behavior Oracles

Derive each expected result from the requested behavior and the established contract, not solely from the current implementation. An oracle copied from the implementation's current output records what the code does today and keeps passing when the contract is wrong; the test becomes a change detector rather than a contract check. State where the expected value comes from — a documented behavior, a published type or schema, an accepted specification, or an authorized description of the requested outcome — so that a reader can tell a contract check from a characterization of existing behavior.

Make the action and the observable assertion easy to identify. Assert promised values or effects for successful behavior; for rejection, assert the documented error or result and any separate side-effect guarantee. Keep the operation expected to fail narrow, so that an unrelated setup failure cannot satisfy the exception assertion, and assert error text only when the wording is itself part of the contract: a documented error class or code is the stable comparison when only the category is promised, and a message assertion belongs only where the message is caller-facing contract.

A rejection assertion is easy to widen by accident, because the setup can fail in the same shape as the operation:

```ts
// Broad: the path does not exist, so any setup failure satisfies the assertion.
await assert.rejects(publishRelease("dist/missing"));

// Narrow: the fixture is created first, and the documented error is named.
const input = await writeFixture("release.json", "{}");
await assert.rejects(publishRelease(input), (error: unknown) =>
  error instanceof ManifestError && error.code === "MISSING_VERSION",
);
```

The first form passes when `publishRelease` rejects for any reason, including a missing directory that the test never intended to test, so it establishes nothing about the validation path it names. The narrow form establishes the fixture before invoking the operation and compares the error class and code the contract promises; if the operation resolved instead of rejecting, or rejected with an unrelated error, the assertion fails. A separate side-effect guarantee — that no artifact was written, for example — needs its own assertion, because rejecting proves only the error outcome.

Test doubles can make a failure deterministic or verify an interaction, but they may diverge from the real dependency. Select fidelity according to the boundary being tested and retain project conventions; no universal prohibition on mocks and no required unit/integration ratio follows. The next section explains what that choice leaves untested.

## Mocked Collaborators And The Real Boundary

A test double substitutes one collaborator at a seam the test controls. It can record the arguments your code passed, return a response the test chose, and count how often the seam was used. What it proves is an interaction inside the process under test: this code called that seam, with those arguments, and it handled the response the double supplied. That is real evidence about the caller — argument construction, control flow, and response handling — and it is deterministic because the test owns the collaborator's answers.

The double cannot prove what the real collaborator does after the call leaves that seam. A mocked transport method proves that a call occurred; it does not prove the request framing at the process boundary — the request line and target, the header set, the body encoding and content length, connection reuse, TLS, or whether the peer's parser accepts the bytes. Nor does it prove the real dependency behaves as the double claims: a double encodes the test author's belief about the dependency's contract, so a wrong belief yields a passing test against the real system. The seam also usually hides module resolution, file-system semantics, clock behavior, and retry or timeout handling that the real path performs.

The deciding question is which boundary the contract names. If the contract is about a caller-visible result and the interaction with an injected interface, a double can be sufficient evidence and the more deterministic choice. If the contract is about what crosses a serialization, wire, module-resolution, file-system, or process boundary, the double is silent on exactly that claim, and the assertion has to observe a real boundary. The two checks are complementary, not interchangeable, and neither is more rigorous by category.

A double for a transport makes the distinction concrete:

```ts
import assert from "node:assert/strict";

interface TransportRequest {
  readonly method: string;
  readonly path: string;
  readonly body: string;
}

interface TransportResponse {
  readonly status: number;
  readonly body: string;
}

interface Transport {
  send(request: TransportRequest): Promise<TransportResponse>;
}

function recordingTransport(): { transport: Transport; calls: TransportRequest[] } {
  const calls: TransportRequest[] = [];
  return {
    calls,
    transport: {
      async send(request) {
        calls.push(request);
        return { status: 200, body: '{"id":"ord_1"}' };
      },
    },
  };
}

const { transport, calls } = recordingTransport();
const order = await createOrder(transport, { sku: "A-1", quantity: 2 });

assert.equal(calls.length, 1);
assert.equal(calls[0]?.method, "POST");
assert.equal(calls[0]?.path, "/v1/orders");
assert.equal(order.id, "ord_1");
```

This test establishes that `createOrder` called the injected seam once with a `POST` to `/v1/orders` and that the caller received the id carried by the response the double returned. It establishes nothing about the HTTP request a real transport would build from that request object: header names and casing, `content-type`, `content-length`, body serialization, path joining against a base URL, and the server's acceptance of the payload are all outside the double. A framing check needs a real boundary — for example, a local `node:http` server that records the method, target, and headers its request object received while the client under test points at its port, with the server assertion made inside the request handler and the listener closed during teardown. Confirm the exact request property names against the installed Node.js version; whether the recorded framing matches the contract is the assertion.

When a test uses a double, record the boundary it replaced and the checks that were not performed. That record is part of the evidence, because a green suite that names no boundary reads as if the real dependency had been exercised. A question about the packed artifact — an entry point, an export condition, or a declaration a consumer resolves — is not answered by a source-tree double at all; package artifact and consumer questions route to `node-package-distribution`.

Which mocking facilities a runner provides, and how module replacement, timers, and spies behave, is runner- and version-specific. Establish it from the installed runner's own documentation rather than from API resemblance, and do not infer one runner's mocking semantics from another's similarly named API. This page makes no cross-runner mock comparison and sets no mocking style or ratio.

## Assertion Strength

Coverage counts execution of measured items; an assertion compares a computed value with an expected one. These are different observations of the same run, and a run can satisfy the first while failing the second. The diagnostic is direct: an assertion too weak to detect a wrong result passes. The line enters the numerator, the suite is green, and no coverage report distinguishes it from a line whose assertion would fail on a wrong result. A high percentage therefore says the code ran, not that the test would notice a defect.

Weak assertions share one property: they accept a value that violates the contract. Common forms assert only that a result is defined, truthy, or of an expected type; that a collection is non-empty without checking its contents; that a mock was called without checking the arguments the contract fixes; that a branch was reached rather than that it produced the promised result; or that the implementation's current output was copied into the expectation. Each form can execute every measured item on the path while passing for a wrong answer, and the passing test then fails only on a crash.

Strengthening an assertion means comparing the contract's promised value or effect: the exact value, the error identity (class or code, or wording only where the wording is promised), or the externally visible side effect. A covered branch shows the difference:

```ts
export function applyDiscount(subtotal: number, member: boolean): number {
  return member ? Math.round(subtotal * 0.9) : subtotal;
}

// Weak: reaches the member branch but passes for any finite number.
test("computes a member total", () => {
  assert.ok(Number.isFinite(applyDiscount(100, true)));
});

// Contract: the same covered branch is compared with the promised amount.
test("applies the promised ten percent member discount", () => {
  assert.equal(applyDiscount(100, true), 90);
  assert.equal(applyDiscount(100, false), 100);
});
```

Both tests execute the discount branch and both can be counted as covered. The first passes for a rate of five percent, a negative total, or an inverted condition that still returns a finite number; the second fails as soon as the promised amount changes. The example uses the Node.js `node:assert` API in a commonly available form; the assertion library is a project convention, while the decisive part is the comparison with the contract value. Check the installed version's documentation for the exact rejection-validation form used above.

Assertion count is not assertion strength. Several weak assertions can be weaker than one whole-result comparison, and a single deep comparison of a result object can cover several promised fields at once. Judge each test by the contract points it can detect, not by how many assertion calls it contains, and do not introduce an assertion-count target as incidental test work.

Denominator drift and assertion adequacy stay separate questions. A percentage that moved because the measured source set changed is a collection measurement question, diagnosed on the collection page; a green percentage over a line whose assertion accepts a wrong value is a design question answered here. Neither observation substitutes for the other, and a report that states one without the other overstates what the run established.

## Runtime, Runner, And TypeScript Boundaries

Treat test discovery, transformation, type checking, runtime execution, module loading, and coverage as separate configured behaviors. Establish the target runtime and test runner from project evidence. Installing with Bun does not show that tests execute in Bun. A runner's Jest-like API does not establish complete API compatibility or equal isolation semantics.

- Node's built-in `node:test` behavior is Node-version-specific. Node v26.13.0 documents TypeScript test-file discovery under its native type-stripping conditions ([Node.js v26.13.0 test runner](https://nodejs.org/download/release/v26.13.0/docs/api/test.html)). Stripping erasable syntax is not type checking, ignores `tsconfig.json`, and does not support syntax that requires code generation or `.tsx` in the documented path ([Node.js v26.13.0 TypeScript modules](https://nodejs.org/download/release/v26.13.0/docs/api/typescript.html)). Do not project those details to other Node versions or Bun.
- Bun's `bun test` runs in Bun, supports TypeScript transforms, and documents checking test files and their imports through its `--check` option ([Bun test runner](https://bun.com/docs/test)). Its default shared process, global object, and module registry are Bun-specific; Jest compatibility is explicitly incomplete. Bun's test pages are rolling documentation that surfaced no release version, so these statements describe the accessed pages rather than a contract for a specific release.
- Jest uses its own discovery, transforms, configuration, and runtime requirements. Its TypeScript transformation depends on configuration; Babel's TypeScript transform does not itself type-check ([Jest code transformation](https://jestjs.io/docs/code-transformation)). Jest's current configuration page identifies itself as version 30.5, while release v30.5.2 supplies its own type-stripping note for files no transformer claims — a version-specific behavior, not a claim that Jest checks types. Bun as an install command does not establish a supported Jest runtime.

The transform-versus-check distinction has a concrete shape when a runner accepts TypeScript test files:

```sh
# Executes the TypeScript test file through the runner's transform; no type check.
bun test cart.test.ts

# Checks the test file and its imports, then runs the tests.
bun test --check cart.test.ts
```

The first command accepting and running a `.ts` test file shows that the runner transformed it and that its assertions passed; it does not show that the file type-checks. The second asks for a check of test files and their imports before the tests run, which is narrower than "the project type-checks": files outside that import graph are not in the check, and the check's result is still separate from whether the wider program compiles. Node's native path presents the same two questions differently, because `node --test` on v26.13.0 strips erasable syntax without checking and ignores `tsconfig.json`, so a separate `tsc --noEmit` invocation is what answers the type question. Which program a check covers is a quality-scope decision that belongs to `node-quality-workflow`.

These are representative version-qualified documentation findings, not a recommendation or an interoperability test. For a concrete project, check the exact installed versions, configuration, invocation, test-file patterns, module setup, transform or check scope, and execution runtime. A tool's TypeScript support can mean transformation without type checking; identify the actual checker command separately.

## Evidence And Handoff

A passing run establishes only that the collected tests passed under that command, configuration, and runtime. Report collection and execution separately when their evidence differs, and report the design evidence with them: which expected values came from the contract, which boundary a test double replaced, and which assertions compare the promised result rather than merely reaching the line. Report unavailable version or compatibility details explicitly rather than inferring them from package-manager use, syntax support, or publisher goals.

If a contract-consistent test exposes a production defect, preserve the assertion and observed mismatch, stop changes that depend on repairing production behavior, and hand off the production change with the contract, reproduction, and relevant test. Test-only ownership does not authorize the production edit.

## Limits And Routes

Runner behavior in this page is version- and configuration-specific. Bun's `--check` checks test files and their imports only, so it does not establish a whole-project check; Node's native TypeScript path strips without checking; and a Jest transform does not verify types by itself. The inspected runner documents also disagree on two measurement points — the Node API statement that matching test files are excluded from coverage by default against a Node Learn example that includes one, and Bun's coverage page against its test-configuration page on when threshold checks run. The inspected pages do not explain either difference, so both sides stay visible and neither is resolved into a default; the measurement reading of both belongs to the collection page. No universal runner, cross-runner mock equivalence, unit/integration ratio, assertion count, coverage target, or compatibility promise follows from anything here. No step in this page selects or relies on Vite, and no command sequence here forms an implicit pipeline.

This is test-only work. A detected production defect is reported to `node-project-writer` and not repaired here. Discovery, isolation, process cases, and coverage interpretation, including the canonical coverage-drop diagnosis, are on [Collection, Isolation, And Coverage](collection-isolation-and-coverage.md); the cross-runtime runner and coverage view is `node-project-reference -> reference/test-execution-and-measurement.md`. Package tarball and installed-archive consumer questions route to `node-package-distribution`, and tests for this repository's `scripts/node/` utilities stay on their repository route, `skill-script-node-test-writer`.
