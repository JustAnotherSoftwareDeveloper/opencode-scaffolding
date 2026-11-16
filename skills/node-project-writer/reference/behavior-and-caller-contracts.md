# Behavior And Caller Contracts

Use this reference when an authorized production change may alter what a caller observes: a
returned value or state, a failure channel, a public import path, a declaration's inferred
type, the timing of an effect, or a side effect that survives cancellation. It owns the
caller-contract question for a change. Which package, runtime, manager, compiler, and
consumer surround the change is a different question, answered in
[Change Design And Validation](change-design-and-validation.md); the mechanics behind
cancellation, backpressure, and process lifetime are answered in
`node-project-reference -> reference/concurrency-and-lifecycle.md`.

The subject is production TypeScript source, configuration, declarations, and directly
coupled regression tests in Node.js or Bun projects. Node.js and Bun runtime mechanics
appear only where they explain how TypeScript source executes or what a caller observes.
JavaScript-only work is out of scope, and `allowJs`, `checkJs`, and JSDoc typing of `.js`
files are excluded.

This is reference context; the operation entry point owns authorization, edits, commands,
and completion claims. Two kinds of statement appear below and are never interchangeable.
A **behavior** is documented for a named API, runtime, and version. A **convention** is a
project or publisher choice whose justification is the consequence it protects. A
convention is never presented here as language behavior.

## Ask What Callers Observe

These five prompts locate the contract that decides whether a change is safe. Ask them
about the change at hand; they are not a universal checklist, an acceptance gate, or a
scoring rubric. A change may leave some of them untouched, and answering all five is not
evidence that the change is correct or complete. What each prompt buys is the identity of
one contract, not a completed review.

1. **What result or state does the caller get?** A returned value, a resolved promise
   value, a mutated object, or a state the caller reads later. The call's documented
   result decides; an internal rewrite that produces the same result has not changed this
   surface.
2. **Through which channel does failure arrive?** A synchronous `throw`, a rejected
   promise, an error passed to a callback, or an emitted `'error'` event. The channel is
   part of the contract, not an implementation detail, because it decides which call-site
   code can observe the failure.
3. **Which public runtime and type path reaches the change?** The package entry point and
   its export map, or a file another module imports directly, plus the declaration path a
   typed consumer resolves. Both paths can change independently.
4. **When does the effect happen, and can it be cancelled?** Ordering with respect to the
   caller's next statement or next turn, timer behavior, and what an accepted
   `AbortSignal` actually stops for this API.
5. **Which side effects, cleanup, and defaults accompany it?** Files written, requests
   sent, listeners added or removed, processes started or killed, and the documented
   defaults that apply when the caller omits an option.

The prompts are independent. A green type check answers a different question from a green
runtime test, and a runtime test that awaits the new failure channel says nothing about a
caller that still uses the old one. Treat each answer as evidence about one surface.

## Keep The Type Surface And The Runtime Surface Separate

TypeScript erases type-only imports and exports from emitted JavaScript, so an
`export type { Config } from "./config.js"` produces no runtime binding, so a consumer's
value import of that name fails even though its type import succeeds ([TypeScript Modules
Reference](https://www.typescriptlang.org/docs/handbook/modules/reference.html)). A package
can therefore satisfy a typed consumer and fail a runtime consumer of the same name, or
the reverse.

The runtime path is decided by the package's own metadata. Node.js documents that `exports`
defines the public entry points when present, takes precedence over `main` for
package-name resolution, and makes subpaths it does not expose unavailable through
ordinary package-name resolution; conditional keys are matched in object key order, so the
active condition depends on order as well as on the runtime ([Node.js
packages](https://nodejs.org/api/packages.html)). A declared subpath that no key exposes
fails at resolution, whatever the declarations say.

The type path is decided by a separate resolver. TypeScript's `node16` and `nodenext`
resolutions follow `exports` conditions, `bundler` also follows `exports` without requiring
Node's runtime rules, and extension substitution can locate a declaration after an export
target is chosen. Neither direction proves the other: a declaration that type-checks does
not establish that the runtime target exists and loads, and a runtime import that succeeds
does not establish that a typed consumer resolves declarations for that subpath.

Two change shapes show the separation. In the first, the runtime entry point stops
re-exporting a public name while the published declaration still lists it:

```ts
// src/index.ts — before the change
export { createServer } from "./server.js";

// after the change: the re-export is gone from the built entry point,
// while the published index.d.ts still declares it.
// import { createServer } from "widget";  — link fails before the
// module body runs, on a consumer whose type check passed.
```

That consumer's checker accepts the import against the stale declaration, and the
runtime's module linking then rejects the missing export before any of the module's code
executes. The failure is a reachability fact about the built entry point, not a typing
error.

In the second shape, only the declaration changes. The runtime function is untouched:

```ts
// index.d.ts — before
export declare function parseConfig(text: string): Config;

// index.d.ts — after: the declaration admits a missing configuration
export declare function parseConfig(text: string): Config | undefined;
```

No emitted JavaScript changed, so every existing runtime call behaves as before. A
consumer compiled with `strictNullChecks` must now handle `undefined`: reading a property
of the result raises TS18048 ("possibly `undefined`"), and passing it where a `Config` is
required raises an assignability error. That is a real caller-visible change carried
entirely by inference.

Types describe a static interface; they do not validate runtime values. A type assertion
is erased and performs no runtime check, so `JSON.parse(text) as Config` can hand a caller
an object that does not match `Config` while the checker reports no error ([TypeScript type
assertions](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions)).
When a change depends on the shape of external input, the runtime check is a separate
piece of behavior to identify, not something the declaration supplies.

## Read The Failure Channel From The API Contract

Node.js documents several distinct failure paths: a synchronous `throw`, a rejected
promise, an error passed as the callback's first argument, and an `'error'` event on an
`EventEmitter`. Which path applies is determined by the called method's documentation,
which the documentation directs readers to consult because a handful of asynchronous APIs
can still throw ([Node.js errors](https://nodejs.org/api/errors.html)).

The difference is observable at the call site. A rejection settles a promise the caller can
await or return; a synchronous throw happens before any promise exists; a callback argument
is only seen by the callback; an emitted `'error'` event is delivered to listeners in a
later turn. An `'error'` event emitted after the call stack has returned cannot be
intercepted by the `try` block that contains the call, and with no listener attached Node.js
throws it as an uncaught exception. The `try` has already exited, so its `catch` is not a
boundary for that failure.

The two shapes below are different APIs, not two styles of the same call:

```ts
import { readFile } from "node:fs/promises";

type Settings = { port: number };

async function loadSettings(path: string): Promise<Settings> {
  const text = await readFile(path, "utf8");
  return JSON.parse(text) as Settings; // a rejection settles the returned promise
}

function parsePort(raw: string): number {
  const port = Number(raw);
  if (!Number.isInteger(port)) throw new RangeError(`not an integer: ${raw}`);
  return port; // a synchronous throw, before any promise exists
}
```

`await loadSettings(path)` inside a `try` observes the rejection; `loadSettings(path)`
called without awaiting discards it; `parsePort(raw)` needs no `await` for its throw to be
observed. A change that converts one channel to another — a callback error argument to a
rejection, or a rejection to an emitted event — changes what existing callers can catch.
That is a caller-visible contract change even when the error value itself is identical.

For Node-originated errors, `error.code` is documented as more stable than `error.message`:
codes change only between major versions, while messages may change between any versions
([Node.js errors](https://nodejs.org/api/errors.html)). Matching on `code` is a convention
whose rationale is that stability statement, and the rationale is the reason it is worth
following — the identifier survives patch releases that reword a message. The claim does
not extend to third-party error objects, whose codes and messages follow their own
publishers.

## Treat Cancellation As A Request, Not Rollback

The web-platform model, which Node.js and Bun both expose through global
`AbortController` and `AbortSignal`, is a request with a cooperating API on the other side.
An API that supports aborting accepts a signal and uses its state to decide how to
proceed; the DOM Standard says an observing API can choose to ignore the signal when the
operation has already completed ([WHATWG DOM
Standard](https://dom.spec.whatwg.org/#interface-abortsignal)). Node.js describes
`AbortController` as a utility for signalling cancelation in selected `Promise`-based APIs,
and the word "selected" is the operative bound ([Node.js
globals](https://nodejs.org/api/globals.html)).

No inspected source promises that abort reverses an effect already produced. The concrete
case is Node's `fsPromises.writeFile`: cancelation is documented as "best effort", "some
amount of data is likely still to be written", and an aborted request does not abort
individual operating-system requests but the internal buffering the write performs
([Node.js file system](https://nodejs.org/api/fs.html)). An already-aborted write is a
different case: it rejects with `AbortError` without performing I/O, because no effect had
started. The caller of a cancelled write can therefore observe both the cancellation and a
partial file, and the partial bytes are not removed by the abort.

What a signal stops is per API, and two Node stream functions demonstrate the split. For
`stream.finished(stream, { signal }, callback)` the signal cancels the wait for the stream
to finish: the documentation states that the underlying stream is not aborted, the callback
receives an `AbortError`, and the listeners the function added are removed; the `signal`
option was added in Node.js v15.11.0. For `stream.pipeline(..., { signal })` the signal
destroys the underlying pipeline, calling `destroy` with an `AbortError`, and
`stream.addAbortSignal(signal, stream)` behaves like `.destroy(new AbortError())` on the
stream ([Node.js stream](https://nodejs.org/api/stream.html)). A wait, a teardown, and a
completed write leave different residue.

Pre-aborted and after-start cancellation also differ by API. Bun's `spawn` documents two
stages: an already-aborted signal throws an `AbortError` synchronously before a process is
created, so the caller never receives a handle and nothing is spawned; a later abort kills
the running process with the signal named by `killSignal`, which defaults to `SIGTERM`
([Bun spawn signal](https://bun.com/reference/globals/bun/Spawn/BaseOptions/signal)). Node's
`child_process` documents aborting as similar to calling `.kill()` on the child, with the
callback receiving an `AbortError`, and adds `signal` per method: `exec` in v15.4.0,
`spawn` in v15.5.0 and v14.17.0, and `killSignal` support for `spawn` and `fork` in v15.11.0
and v14.18.0 ([Node.js child
process](https://nodejs.org/api/child_process.html)). The Bun statements are Bun
documentation for `Bun.spawn`; they are not evidence about Node's `child_process`, and the
reverse also holds.

A signal is single-use in one direction. Once aborted, a signal cannot be reset or
re-armed, and the controller fires its abort event once, so a new cancellable operation
needs a fresh controller. An un-aborted controller can be shared by several concurrent
operations, which makes the signal a fan-out request rather than a shared stop order:
threading one controller through unrelated calls does not give them a common ordering or a
guarantee that each one observes it.

Promise completion is not cancellation. `Promise.race()` settles with the eventual state of
the first input that settles, and the losing inputs and their attached handlers are neither
cancelled nor unsubscribed; the losing result is discarded ([MDN
`Promise.race()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/race)).
The bound matters in both directions: this is promise machinery, not a claim that every
underlying operation keeps running forever. Whether a timer, socket, or subprocess continues
is that API's own answer, and stopping it may be `clearTimeout`, an explicit
`destroy`/`kill`/`cancel`, an `AbortSignal`, or another API-specific route. `AbortSignal` is
not the exclusive route, and no operation is claimed to have to accept one.

The example below scopes the rule to an API that documents signal support:

```ts
import { writeFile } from "node:fs/promises";

async function saveReport(path: string, report: string): Promise<"written" | "cancelled"> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 500);

  try {
    await writeFile(path, report, { signal: controller.signal });
    return "written";
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      return "cancelled"; // a prefix of `report` may already be on disk
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
```

`writeFile` observes the signal from Node.js v15.2.0 and v14.17.0, and its cancelation is
the "best effort" buffering behavior above, so `"cancelled"` does not mean the file is
absent or intact. The contrast is a helper that accepts a `signal` parameter and never
forwards it to an operation that observes one:

```ts
import { appendFile } from "node:fs/promises";

async function appendNote(path: string, note: string, _signal: AbortSignal): Promise<void> {
  await appendFile(path, note); // no signal option passed: abort has no effect here
}
```

Nothing happens on abort in the second form. The parameter is data; only an accepting API
turns it into a stopping action. Reading a signature is therefore not evidence of
cancellability, and a comment or test that asserts cancellation against the second form
would encode a false contract.

## Preserve Behavioral And Public Boundaries

Before editing, identify the observable behavior, the callers that depend on it, the public
imports and package entry points, the module interpretation, the declared and effective
runtime versions, and the error paths involved. Respect the existing module and package
layout unless changing it is part of the authorized behavior request. A change to package
`type`, `exports`, conditions, or subpath visibility can alter consumer resolution, and
adding exports can block a previously reachable path. Treat declaration shape and runtime
behavior as related but separate surfaces; neither one establishes the other.

Trace asynchronous effects only as far as they bear on the change. Timers are thresholds,
not exact deadlines. For Node streams, a writable returning `false` signals that the
producer should wait for `'drain'`, and `highWaterMark` is a threshold rather than a strict
process memory cap. Do not generalize one Node API's behavior or stability label to another
release, Bun, or a third-party library.

Handle errors according to the affected API's documented contract, as the failure-channel
section above sets out, and preserve useful error context without leaking secrets or
sensitive data into logs and reports. Do not infer a universal security, logging,
observability, or reliability policy. Runtime diagnostic reports can include environment or
network information, so review their contents and exposure only when the requested change
touches them. Logging output, diagnostic channels, process reports, and telemetry bridges
are distinct interfaces. Source-level examples from style guides are contextual conventions,
not universal Node.js or Bun rules; follow the target repository's established conventions
where available.

## Diagnose A Consumer Mismatch

The characteristic failure for this page is a change that passes `tsc` and passes a runtime
test while a consumer observes a different failure channel. An adapter rewrite shows the
shape: the old function called `callback(error, value)`, the new one returns a promise that
rejects, and the adapter's own test awaits the call and asserts the rejection. The test is
green because it was written against the new channel. An existing caller still passes a
callback, so it never receives the rejection, never enters its error branch, and waits for a
value that will not arrive. Nothing about the implementation is broken; the channel changed
and the caller's observation of it did not.

Read the mismatch in order instead of assigning a cause:

1. Establish which contract each green check covered. A type check covers the checker's
   program and options; a runtime test covers its own imports and its own runtime, which is
   often source rather than packed or built output.
2. Establish the consumer's actual path: the exact specifier, the active condition, the
   module format, the runtime and its version, and the declaration resolution mode.
3. Compare the observed outcomes. A synchronous throw, a rejection, an error argument, an
   emitted event, and a link-time missing export are five different observations, and each
   points at a different surface.
4. Assign the question to its owner. A mismatch inside a packed artifact, an export map, or
   a declaration's wiring is the package owner's diagnosis; a channel or shape decision in
   the authorized source belongs to this change.

The consequence to report is the caller-visible observation, not the internal rewrite. "The
function now returns a promise that rejects" is a contract statement; "the caller was
updated" is a claim about one caller, and it needs its own evidence.

## Separate Mechanism From Convention

The distinction is easier to apply with the two lists side by side.

- **Mechanisms** are documented behavior for a named API, runtime, and version:
  `stream.finished` cancels only the wait; `stream.pipeline` destroys its stages;
  `Promise.race` attaches handlers without cancelling an input; an `'error'` event emitted
  after the call stack cannot be caught by the enclosing `try`; `Bun.spawn` throws
  synchronously for an already-aborted signal.
- **Conventions** are choices: whether to branch on `error.code`, `error.name`, or
  `signal.reason`; whether to translate an API error into a domain error type; whether to
  expose a declared name as a type-only export or as a runtime value; whether to wrap a
  callback API in a promise; whether to forward a signal parameter through helper layers.

Each convention has a deciding rationale that is not a language rule. Matching on `code`
protects against message rewording between patch releases, which Node documents. Wrapping a
callback API changes which call-site code can observe failure, which is an observable
consequence, not a correctness rule. Exposing a type without a runtime value fails a
consumer that imports it at runtime, which the runtime path documents. Forwarding a signal
through helpers changes nothing unless an accepting API receives it. Stating such a choice
as Node.js behavior would misattribute both the evidence and the consequence.

## Limits And Version Boundaries

- Error and cancellation behavior is API-specific in the pinned documentation. Signal
  acceptance is recorded per method and version, and the inspected set is not an exhaustive
  inventory; no operation is claimed to have to accept a signal, and no single catch
  boundary covers all asynchronous calls.
- Node's `code`-over-`message` stability statement is scoped to Node-originated errors and
  does not extend to third-party error objects.
- Bun's behavior is documented separately, in rolling reference pages that name no release
  baseline on the inspected pages. No Node.js and Bun parity is claimed, and a missing
  statement on one runtime's page is an evidence limit rather than proof of absence.
- The Node.js error page and API pages used here are v26-series documentation snapshots
  (the error page identified v26.7.0 and the API pages v26.13.1). They are not a claim that
  the pages describe one tested release, and recheck any version-sensitive statement
  against the target project's versions.
- No universal semantic-versioning policy is claimed. Nothing here decides which changes
  require a major version; that is the project's or publisher's decision. No compatibility
  proof follows without the supported versions and the named consumers.
- The examples are documentation illustrations, not executed project evidence. A passing
  type check establishes only the program and options it covered.
- The scope is TypeScript-only: no JavaScript or mixed-language eligibility, no `allowJs` or
  `checkJs` guidance, and no JSDoc typing of `.js` files. Nothing here selects, prescribes,
  or relies on Vite; an incidental dependency edge is neither evidence of direct selection
  nor proof of its absence. Nothing on this page forms an implicit pipeline, and no
  compatibility promise follows for another runtime, package, or version.

## Ownership And Routing

This page owns production behavior: what an authorized change must preserve for callers,
and which caller-visible results, failures, timing, and side effects it alters.

- Project context, module-to-runtime alignment, regression scope, and evidence reporting:
  [Change Design And Validation](change-design-and-validation.md).
- How asynchronous source is written and how a caller-visible async failure is shaped:
  `node-source-style-guide -> reference/async-and-error-boundaries.md`.
- Cancellation, backpressure, and process-lifetime mechanics:
  `node-project-reference -> reference/concurrency-and-lifecycle.md`.
- Public source and API conventions, including the resolution summary for a failing
  subpath: `node-project-reference -> reference/source-and-api-conventions.md`.
- Consumer validation of packaged output, export-map branches, and declaration wiring:
  `node-package-distribution -> reference/consumer-resolution-and-declarations.md`. Archive
  validation belongs to that owner; this page does not duplicate its layered diagnosis.
- Test-only work belongs to `node-project-test-writer`, dependency and environment changes
  to `node-project-dependencies`, and standalone quality configuration or reporting to
  `node-quality-workflow`. This repository's `scripts/node/` utilities have their own
  Bun and repository conventions, which are not ordinary project defaults. Executable
  source-based plans remain with `plan-writer`.

A caller-contract finding is a reason to inspect, bound, or report a change. It is not
authorization to edit, and it is not completion evidence.
