# Async And Error Boundaries

Would a caller observe this failure, and through which channel? Is this detached work awaited, returned, or deliberately dropped? How do you read a caught value that the checker types as `unknown`? And when a promise settles early or an operation is aborted, what actually stopped?

Promise settlement, rejection, emitted `error` events, and cancellation are language or API behavior whose consequences a caller can observe. How much code to place in a `try` block, and which of several equivalent handlers to use, are conventions whose rationale is attribution or consistency; only the publisher or codebase that states them is bound by them. Everything here stays inside TypeScript source. Node.js and Bun mechanics appear only where they explain how TypeScript source executes or how a caller observes its failure. JavaScript-only work is out of scope, and `allowJs`, `checkJs`, and JSDoc typing of `.js` files are excluded. The examples illustrate a decision shape; they are not mandated house style.

## Make Failure Reach The Caller

An `async` function always returns a promise. MDN states that the promise is resolved with the value the function returns and rejected with an exception uncaught inside it, and that a returned non-promise value is wrapped ([MDN `async function`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)).

```ts
async function loadConfig(path: string): Promise<Config> {
  const text = await readFile(path, "utf8");
  return JSON.parse(text) as Config;
}
```

The call site observes settlement, not a return value. `loadConfig` rejects when `readFile` rejects, and an error thrown inside its body becomes that rejection rather than a synchronous throw. A function that returns a promise without being declared `async` does not get that conversion, so a throw before it returns the promise reaches the caller synchronously. Both forms can satisfy a `Promise<Config>` signature while failing at different moments.

Observation is preserved only when the caller waits for the promise or returns it:

```ts
async function start(): Promise<void> {
  const config = await loadConfig("config.json");
  use(config);
}

function scheduleLoad(): Promise<Config> {
  return loadConfig("config.json");
}
```

`await` raises the rejection reason at that point inside `start`, which rejects `start`'s own promise. `return` hands the same promise to the caller. Dropping the promise does neither:

```ts
async function handle(event: AuditEvent): Promise<void> {
  void saveAudit(event); // settlement discarded
}

async function handleAndWait(event: AuditEvent): Promise<void> {
  await saveAudit(event); // rejection becomes handleAndWait's rejection
}
```

`void` evaluates the call and discards the promise it returns, so `handle` neither waits for the audit write nor observes its failure ([MDN `void` operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/void)). `await saveAudit(event)` gives `handleAndWait` the settlement instead. That difference is behavior, not spelling.

Detached work is the same question in another form. A failure in work whose result is not returned to the caller is not reported through the caller's return path. Node documents that using an `async` function as an event handler "can lead to an unhandled rejection in case of a thrown exception", because `emit` does not observe the promise the handler returns; the `captureRejections` option installs a rejection handler ([Node.js Events](https://nodejs.org/api/events.html)). Rejections that reach no handler are reported through the process-level `'unhandledRejection'` event, which is distinct from the synchronous `'uncaughtException'` path ([Node.js Process](https://nodejs.org/api/process.html)). These mechanisms are Node-specific; the inspected sources do not establish that Bun reports detached failures the same way.

Choose by who must observe the failure:

- `await` or `return` when the caller must decide, or when the caller's own promise should carry the failure.
- Handle inside the callee when the failure has a local recovery or a documented fallback.
- Drop the promise only when no caller needs the outcome and the process-level report is acceptable.
- For an async event handler, catch inside the handler; `emit` does not provide propagation. Enabling `captureRejections` is a project configuration decision, not a property of the handler.

## Read The Error Channel From The API Contract

Node documents that synchronous APIs generally report errors by `throw`, while asynchronous failures are reported "in multiple ways": some methods return a promise that may reject, many callback methods pass an `Error` as the first callback argument, and an `EventEmitter` can route errors to its `'error'` event. It also notes that a few typically asynchronous methods may still throw and that no comprehensive list exists, so each method's own documentation governs ([Node.js Errors](https://nodejs.org/api/errors.html)).

```ts
const text = await readFile(path, "utf8"); // promise rejection

readFile(path, (error, buffer) => { // error as first argument
  if (error) return report(error);
  consume(buffer);
});

const stream = createReadStream(path);
stream.on("error", report); // emitted 'error' event
```

The channel belongs to the API, and the channels are not interchangeable. A callback API's return value is not a promise, so there is nothing to `await` or attach a rejection handler to. An emitted `'error'` is not a rejection, so a surrounding `try` does not see it. The same operation may exist in more than one form, as reading a file does here, and each form documents its own channel.

The event channel has its own failure mode. Node's events page states that emitting `'error'` with no listener throws and crashes the process, so an `'error'` listener is part of using such an API rather than a defensive extra. The `errorMonitor` event observes errors for instrumentation, but it does not replace the listener: the page states the missing-listener throw still occurs ([Node.js Events](https://nodejs.org/api/events.html)).

Read the method's page before choosing a handler, and do not expect one channel's handling to cover another. The hub's public-contract review list names all four channels in one sentence; this page states what each one does, and `node-project-reference -> reference/source-and-api-conventions.md` owns the wider public-surface reading.

## Narrow A Caught Value Typed `unknown`

Historically a catch-clause variable was `any`. TypeScript 4.0 allowed an explicit `: unknown` or `: any` annotation on it, and TypeScript 4.4 added `useUnknownInCatchVariables`, which changes the default to `unknown` under the `strict` family ([TypeScript 4.4 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-4.html)). The option defaults to `true` when `strict` is enabled and `false` otherwise and was released in 4.4; `strict` itself defaults to `true` in the current configuration reference and in TypeScript 6.0 and later ([TSConfig `useUnknownInCatchVariables`](https://www.typescriptlang.org/tsconfig/useUnknownInCatchVariables.html), [TSConfig Reference](https://www.typescriptlang.org/tsconfig/strict.html), [TypeScript 6.0 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html)).

```ts
async function readJson(path: string): Promise<Config> {
  try {
    const text = await readFile(path, "utf8");
    return JSON.parse(text) as Config;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`cannot read ${path}: ${error.message}`);
    }
    throw error;
  }
}
```

Reading `error.message` without the guard is a compiler error under these defaults: the variable is `unknown`, and TypeScript 6.0.3 reports TS18046, `'error' is of type 'unknown'`. `instanceof Error` is a runtime check that also narrows the type, so the property becomes available after it. The rethrow keeps a thrown string or plain object from being swallowed or mistaken for an `Error`.

The bound is version-sensitive. With `strict` enabled in 4.4 or later, and without any explicit `strict` entry in 6.0 or later, the default is `unknown`. In 4.4 through 5.x without `strict`, the default is `any`, and the same property read compiles without a guard. State the compiler major or the effective `strict` value beside this advice.

The guard is a real check on the runtime value, unlike an annotation that erases; [Types, Validation, And Generics](types-validation-and-generics.md) owns assertion versus guard. Narrowing also does not make a thrown non-`Error` safe to format: a thrown string has no `message`, which is why the `else` branch is a decision about the value rather than a formality.

## Treat Cancellation As A Request, Not A Rollback

Node documents `AbortController` as "a utility class used to signal cancelation in selected `Promise`-based APIs", based on the Web API ([Node.js Globals](https://nodejs.org/api/globals.html)). The qualifier matters twice: only selected APIs accept a signal, and an accepting API decides how to react. The DOM Standard states that an observing API "can choose to ignore" the signal, for instance if the operation has already completed, and MDN describes `abort()` as aborting an asynchronous operation before it has completed ([DOM Standard](https://dom.spec.whatwg.org/#interface-abortsignal), [MDN `AbortController.abort()`](https://developer.mozilla.org/en-US/docs/Web/API/AbortController/abort)).

An aborted operation therefore stops at a point its own contract defines, and it does not undo what it already produced. Node's `fs` documentation gives the concrete case: cancellation of `fsPromises.writeFile` is "best effort", "and some amount of data is likely still to be written", and aborting "does not abort individual operating system requests but rather the internal buffering" the write performs; an already-aborted write rejects with an `AbortError` without performing I/O ([Node.js File system](https://nodejs.org/api/fs.html)). Code that treats abort as a rollback is wrong about both outcomes: the caller can observe a rejection and a partially written file.

Signal acceptance and effect can differ inside one module. `stream.finished(stream, { signal })` documents that the signal "allows aborting the wait for the stream finish" while "the underlying stream will not be aborted", and that the callback receives an `AbortError` while the listeners it added are removed. `stream.pipeline` documents that aborting the signal calls `destroy` on the underlying pipeline with an `AbortError`, and `stream.addAbortSignal` behaves like calling `.destroy(new AbortError())` on the stream ([Node.js Stream](https://nodejs.org/api/stream.html)).

```ts
import { finished, pipeline } from "node:stream/promises";

await finished(stream, { signal: controller.signal }); // cancels the wait only
await pipeline(source, destination, { signal: controller.signal }); // destroys
```

Both calls type-check and both accept the same signal; what the signal stops is different. Read the API page for which behavior it documents before relying on a cancellation to release a resource. `node-project-reference -> reference/concurrency-and-lifecycle.md` owns the exact surfaces, their per-runtime bounds, and shutdown behavior.

What follows for source style: pass a signal only to an API that documents accepting one; state in the caller's contract what a cancelled call may already have done; put cleanup or idempotency in the operation's own contract rather than assuming the signal supplies it; and do not describe `abort()` as reverting a completed write, send, or state change.

## Read A Settled Race As Settlement Only

`Promise.race()` returns a promise that settles with the eventual state of the first input that settles: it fulfils if that input fulfils and rejects if it rejects. Unlike the other combinators it is always asynchronous, and an empty iterable leaves the returned promise pending forever ([MDN `Promise.race()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/race); [ECMAScript 2027 draft, `PerformPromiseRace`](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#sec-promise.race)).

Settlement is not cancellation. MDN states that settling the returned promise "does not cancel the losing operations or unsubscribe the handlers attached to their promises", that the losing result is discarded, and that repeatedly racing a long-lived promise accumulates handlers on it. The normative algorithm supports the same reading: `PerformPromiseRace` invokes `then` on each input with the result capability's functions and contains no step that cancels or unsubscribes an input, and the promise machinery has no first-class cancellation protocol ([MDN `Promise`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)).

Two bounds keep the statement precise. Whether an underlying socket, timer, or subprocess keeps running is a separate, API-specific question that a race result does not answer. MDN's statement that later rejections do not trigger `unhandledrejection` applies to inputs the combinator successfully iterated and attached a `then` handler to; a throwing iterator or a throwing `then` invocation rejects the combinator's own promise instead.

Stopping losing work is a separate action through whatever the operation supports: a `clearTimeout` or cancellation token, an explicit `destroy`, `kill`, or `cancel`, an `AbortSignal`, or another API-specific route. `AbortSignal` is not the exclusive route, and no operation is claimed to have to accept one.

A bounded example, using the `signal` option that Node.js v26.13.1 documents for `timers/promises`, shows the cleanup the race does not perform:

```ts
import { setTimeout as delay } from "node:timers/promises";

async function withDeadline<T>(operation: Promise<T>, ms: number): Promise<T> {
  const controller = new AbortController();
  const timer = delay(ms, undefined, { signal: controller.signal });
  const deadline = timer.then(() => {
    throw new Error(`operation exceeded ${ms} ms`);
  });

  try {
    return await Promise.race([operation, deadline]);
  } finally {
    // If the operation settled first, abort clears the still-scheduled timer.
    // The operation itself is unaffected: the race does not stop it.
    controller.abort();
  }
}
```

When `operation` settles first, the race returns and the `finally` block clears the timer through the timer's own signal option. Without that call the timer would remain scheduled, because `Promise.race` supplies no stop mechanism. When the deadline wins, `operation` continues: if it holds a request, a stream, or a child process, stop it through the mechanism that API documents. If the losing input is such a resource instead of a timer, the same reasoning applies: read that API's page for its stop mechanism. The timer behavior is Node-specific and bounded to the inspected v26.13.1 documentation; the race semantics are language behavior, and this example was not executed for this page.

## Read Conventions As Conventions

The sections above state behavior. The choices below are conventions, and each keeps its rationale.

- **A focused `try` block.** Google's TypeScript style guide states a preference for a focused `try` block around the code that can throw ([Google TypeScript style guide](https://google.github.io/styleguide/tsguide.html#control-structures)). The language does not require it: a `try` observes failures raised or awaited inside its range, so widening the block changes which failures the handler receives, not whether `try` works. The preference's rationale is that the handler's attribution stays narrow and an unrelated failure is not reported as if it came from the guarded call. Adopting it is a project decision; a wide block with a specific catch is still correct TypeScript.
- **`await` or `return` after a call.** Where only settlement matters, both preserve observation, and the choice is consistency. Inside a `try`, `return await` keeps the rejection in that `try`, while a bare `return` moves it to the caller's `await`; when a handler is intended to see the failure, that difference is behavior.
- **An explicit return type on an exported async function.** Google's guide recommends explicit return types as its own convention for public contracts ([Google TypeScript style guide](https://google.github.io/styleguide/tsguide.html)). The annotation has a type consequence: the returned value is checked against the declared type instead of an inferred one. The preference itself is attributed rather than universal, and [Types, Validation, And Generics](types-validation-and-generics.md) owns annotation versus inference.
- **`.catch()` or `try`/`await`.** Where both observe the same promise, the choice is readability and local consistency. They are not equivalent in scope: a `.catch` handles one promise, while a `try` handles what is awaited within its range.

None of these conventions changes when a rejection occurs, which channel an API uses, or what a signal can stop.

## What Fails, And Where

- An `async` event handler that throws produces an unhandled rejection, because `emit` does not observe the returned promise; a `try` around the `emit` call does not catch it.
- Emitting `'error'` with no listener throws and crashes the process; an `errorMonitor` listener does not prevent that throw.
- Reading `error.message` on a catch variable typed `unknown` is a compiler error under `strict`; TypeScript 6.0.3 reports TS18046, while 4.4 through 5.x without `strict` type the variable as `any` and accept the read.
- A discarded promise reports no failure to its caller: `void saveAudit(event)` continues, and a rejection surfaces only through the process-level unhandled-rejection report, or not at all.
- Aborting `fsPromises.writeFile` can reject the promise while leaving part of the data written, because the abort does not reverse the write.
- `stream.finished` with an aborted signal reports an `AbortError` for the wait while the stream keeps running.
- A losing input to `Promise.race` keeps running and keeps its handlers; the race neither cancels it nor stops a timer, socket, or subprocess behind it.
- `Promise.race([])` never settles, because there is no input whose settlement could be delivered.

## Limits And Ownership

- The error-channel taxonomy is Node-specific documentation for the Node API surface, from the v26.13.1 pages cited above. The inspected sources do not establish that Bun reports failures through the same channels, and no cross-runtime parity is claimed.
- `useUnknownInCatchVariables` dates from TypeScript 4.4 and defaults to `true` under `strict`; `strict` defaults to `true` in the current reference and from TypeScript 6.0. An unconfigured 4.4 through 5.x project may therefore still type a catch variable as `any`, so state the major or the effective `strict` value with the advice.
- `Promise.race` settlement and losing-work wording is current MDN text plus the ECMAScript 2027 draft; MDN is rolling, and draft clause numbering varies between drafts. The deadline example is bounded to the `timers/promises` signal behavior documented for Node.js v26.13.1.
- Cancellation is API-specific. The surfaces named here are the inspected subset, not an inventory, and no inspected source promises an exact stopping point or a reversal of an already-produced effect.
- The DOM Standard was last updated 14 November 2026 and may change; its abort text states a request model, not a rollback guarantee.
- All examples are non-normative illustrations. They were not compiled or executed for this page, and a passing type check would not establish the runtime behavior described.
- This page provides style guidance only. A change to callback behavior, return shapes, or error handling that alters production behavior goes to the production owner (`node-project-writer -> reference/change-design-and-validation.md`); the caller-observable contract of a change belongs to `node-project-writer -> reference/behavior-and-caller-contracts.md`.
- Cancellation, lifecycle, event-loop, and shutdown mechanics belong to `node-project-reference -> reference/concurrency-and-lifecycle.md`; the public source and API surface is covered by `node-project-reference -> reference/source-and-api-conventions.md`.
- Type-level guarantees, assertion versus guard, and which TypeScript syntax runs without a transform are owned by [Types, Validation, And Generics](types-validation-and-generics.md). Callback argument lists and receivers belong to [Functions, Callbacks, Receivers, And State](functions-callbacks-receivers-and-state.md), and value and absence semantics belong to [Values, Defaults, Objects, And Iteration](values-defaults-objects-and-iteration.md).
- The repository's deterministic utilities under `scripts/node/` keep their own Bun and repository conventions; they are not ordinary project defaults. Nothing here selects or presupposes Vite, forms an implicit pipeline, or promises compatibility for another runtime, package, or version.
- The method for weighing these sources, and the routing across the style pages, stays with the hub, [Contextual Source-Style Guidance](source-style-guidance.md).
