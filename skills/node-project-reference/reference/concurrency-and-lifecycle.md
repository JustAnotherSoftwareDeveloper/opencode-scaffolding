# Concurrency And Lifecycle

## Scope

This page answers three questions that sound related and are not: whether this work runs in parallel, whether a cancellation stops the effect, and whether shutdown waits for work. It covers the event loop, the worker pool, worker threads, child processes, stream backpressure, cancellation surfaces, timers, process lifetime, and concurrent modification of one file in TypeScript projects.

The subject is TypeScript source, configuration, declarations, tests, quality diagnostics, and package artifacts in Node.js or Bun projects. Node.js and Bun mechanics appear only where they explain how that TypeScript surface executes, emits, resolves, declares, or reaches a consumer. JavaScript-only work is out of scope, and `allowJs`, `checkJs`, and JSDoc typing of `.js` files are excluded from this reference.

The page states passive mechanics and interpretation. It selects no concurrency design, worker strategy, pool size, or shutdown sequence, and it measures no project. Event-loop, worker, stream flow-control, timer, process, and filesystem-pool claims come from the released Node.js v26.13.0 API and Learn pages named beside them. Cancellation-surface and wait-versus-effect claims come from Node.js v26.13.1 pages, MDN JavaScript and Web API references, the ECMAScript 2027 draft specification, and the WHATWG DOM Living Standard, last updated 14 November 2026. Bun pages are rolling and expose no release baseline. Every statement describes publisher documentation rather than an executed observation, Node findings are not generalized to Bun without separate evidence, and no parity between the runtimes is claimed.

## Three Questions, Three Mechanisms

Keeping the questions apart prevents three common mistakes: reading `async` as parallelism, reading a signal parameter as a rollback, and reading process exit as a completed flush.

- **Does this run in parallel?** Answered by which thread executes the work. JavaScript callbacks run on the event-loop thread, some asynchronous work is delegated to the operating system or a worker pool, and `worker_threads` add JavaScript threads. An `async` function or a Promise says nothing about threads.
- **Does a cancellation stop the effect?** Answered per API. A signal is a request that an accepting operation may observe by cancelling a wait, destroying a stream, killing a process, or stopping internal buffering. It does not reverse an effect that was already produced.
- **Does shutdown wait for work?** Answered by pending handles, listeners, and per-resource lifetime controls in one runtime. A timer that is still referenced, a server socket, an active worker, or an awaited child process can each keep a process alive, and no inspected source states one shutdown contract across Node.js and Bun.

A terminal outcome — the value or rejection the caller finally observes — is the place to check each answer. A settled race value, a rejection carrying an abort reason, and a process that exits are three different observations, and none of them establishes the other two.

## Event Loop And Callback Timing

Node.js runs JavaScript callbacks on the event-loop thread. Non-blocking I/O is handled by operating-system facilities where available, and selected operations are delegated to libuv's worker pool ([The Node.js Event Loop](https://nodejs.org/learn/asynchronous-work/event-loop-timers-and-nexttick); [Don't Block the Event Loop](https://nodejs.org/learn/asynchronous-work/dont-block-the-event-loop)). Long-running synchronous callbacks therefore delay every other event-loop task, including I/O callbacks that have already completed.

Asynchronous syntax does not move JavaScript computation to another thread. An `async` function body and the code after an `await` continue on the event-loop thread, and a resolved Promise schedules a continuation rather than starting a parallel computation. The worker pool helps with operations that the runtime implements off-thread, not with the reader's own JavaScript loop.

`process.nextTick()` callbacks run before the loop continues to its next phase, and recursive scheduling can prevent the loop from reaching I/O phases ([The Node.js Event Loop](https://nodejs.org/learn/asynchronous-work/event-loop-timers-and-nexttick)). This is a Node.js description; the same page is rolling and unversioned, and it labels its phase diagram a simplification.

Phase ordering has a version boundary. The Node.js Learn page records that libuv 1.45.0, shipped with Node.js 20, moved timer processing to after the poll phase in each iteration, with one compatibility run before the loop is entered. A phase-by-phase account therefore describes a specific Node.js generation, and platform differences remain.

Bun's inspected pages do not set out a general event-loop and worker-pool model. Bun documents a separate-thread `Worker` API and a blocking `Bun.sleepSync()`, but those passages do not establish Bun's full scheduling model ([Bun Workers](https://bun.com/docs/runtime/workers); [Bun Utils](https://bun.com/docs/runtime/utils)). That absence in the inspected pages is an evidence limit, not evidence that Bun lacks scheduling behavior.

## Work That Leaves The Event Loop

### Worker Threads And Child Processes

Node.js labels `node:worker_threads` stable and documents that workers execute JavaScript in parallel. Its stated fit is CPU-intensive JavaScript: the documentation says workers do not help much with I/O-intensive work compared with Node's built-in asynchronous I/O, and it documents transferring and sharing memory between threads ([Node.js v26.13.0 Worker Threads](https://nodejs.org/download/release/v26.13.0/docs/api/worker_threads.html)).

Child processes are a different mechanism with different consequences. A child process is a separate operating-system process with an inter-process communication boundary, so its memory, failure containment, and termination differ from the worker-thread model. Worker threads share a process; a crashing worker and a crashing child do not leave the same state behind, and terminating one does not terminate the other. Both mechanisms can be correct, and the documentation describes mechanics rather than a selection rule.

Node's `child_process` functions accept a signal per method, with separate version additions: `exec` added `AbortSignal` support in v15.4.0; `execFile` in v15.4.0 and v14.17.0; `spawn` in v15.5.0 and v14.17.0; `fork` in v15.6.0 and v14.17.0; and `killSignal` for an `AbortSignal` reached `spawn` and `fork` in v15.11.0 and v14.18.0 ([Node.js v26.13.1 Child process](https://nodejs.org/api/child_process.html)). Aborting is documented as similar to calling `.kill()` on the child, except that the callback receives an `AbortError`. Using the signal to destroy a long-lived child process is documented as deprecated (DEP0209), while the same page describes it as appropriate for cancellation, an externally propagated abort, or a timeout.

Bun's global `Worker` is a separate-thread API that shares I/O resources with the main thread, and Bun labels it experimental, particularly termination. An active worker keeps the spawning process alive by default, `terminate()` exits as soon as possible, and the worker's `close` event can occur before it has fully exited ([Bun Workers](https://bun.com/docs/runtime/workers)). Bun's Node.js compatibility page separately labels `node:worker_threads` partially implemented and lists specific omissions and ignored options ([Bun Node.js Compatibility](https://bun.com/docs/runtime/nodejs-compat)). Those are two different API surfaces with two different status labels, so neither label establishes a common worker contract, and a green compatibility mark is not evidence of identical lifecycle behavior.

## Stream Backpressure

Node.js documents `Writable.write()` returning `false` as the cue to stop writing until the stream emits `'drain'`. Continuing to write past that cue accumulates buffered chunks and increases memory use. `highWaterMark` is a buffering threshold that triggers that cue; it is not a strict total-memory cap and not a promise about the destination ([Node.js v26.13.0 Stream](https://nodejs.org/download/release/v26.13.0/docs/api/stream.html)). Waiting for `'drain'` is flow control, not completion: the final chunk is acknowledged later by the stream's own finish or close signal.

Bun documents distinct stream classes and additional behavior. For a `ReadableStream` created with `type: "direct"`, `controller.write()` reports bytes or returns a promise when the destination buffer is full; awaiting that promise waits for drain, and a disconnected destination is reported as `0`. Bun's page says ordinary Web `ReadableStream` and async-generator response bodies apply backpressure automatically, that `reader.cancel(reason)` calls the source's `cancel`, and that a consumer leaving a response generator calls the iterator's `return()` rather than `throw()` ([Bun Streams](https://bun.com/docs/runtime/streams)). That page also states that a generator suspended at an unresolved `await` stays there unless the awaited operation itself receives a cancellation signal such as `req.signal`.

Bun's compatibility page calls `node:stream` fully implemented while also noting that several stream helpers understand Node streams but not Web Streams ([Bun Node.js Compatibility](https://bun.com/docs/runtime/nodejs-compat)). A high-level status label qualified by API-specific limitations is not evidence that Node streams, Bun's Node-stream surface, and Bun's Web Streams share one backpressure contract.

## Cancellation Is A Request

### What `abort()` Changes

`AbortController.abort(reason)` stores the reason on the controller's signal and notifies observers that the associated activity is to be aborted; with no argument it stores an `"AbortError"` `DOMException`. The signal exposes `aborted`, `reason`, `throwIfAborted()`, an `onabort` handler and `abort` event, and the static `AbortSignal.abort()`, `AbortSignal.timeout()`, and `AbortSignal.any()` methods ([WHATWG DOM Standard](https://dom.spec.whatwg.org/#interface-abortsignal); [MDN AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal)). MDN describes abort as targeting an asynchronous operation before it has completed ([MDN AbortController.abort()](https://developer.mozilla.org/en-US/docs/Web/API/AbortController/abort)).

The web-platform model is a request with a cooperating API on the other side. The DOM Standard says an API that wishes to support aborting accepts a signal and uses its state to decide how to proceed, encourages such APIs to reject unsettled promises with the abort reason, and states that an API observing the signal can choose to ignore the change, for instance if the operation has already completed. Node describes `AbortController` as a utility for signalling cancelation in selected `Promise`-based APIs ([Node.js v26.13.1 Global objects](https://nodejs.org/api/globals.html)). The word "selected" is the operative bound: cancellation is per API, not a property of promises in general.

Propagation is equally explicit. A signal reaches only an operation that accepts it and chooses to observe it; nothing in the inspected sources establishes implicit global propagation. Reason composition is also specific: `AbortSignal.timeout()` aborts with a `"TimeoutError"` `DOMException`, and `AbortSignal.any()` produces a dependent signal whose reason is the reason of the first source to abort, with no separate "which source fired" property and no method to unsubscribe the composed signal from its inputs.

MDN's pages disagree about telling a timeout apart through `AbortSignal.any()`. The `AbortSignal.any()` page's example distinguishes causes by `e.name === "TimeoutError"`, while the `AbortSignal` page warns that there is no way to tell whether the final abort came from a timeout. The disagreement stays visible here: the composed signal's reason is the first source's reason object, so inspect `signal.reason` or the rejection's `name`, treat a `TimeoutError` name as a strong indication rather than proof in every configuration, and do not assume a separate attribution field.

An un-aborted signal or controller can be shared by several concurrent operations. Once aborted, the signal cannot be reset or re-armed and the controller triggers its abort event only once, so a new cancellable operation needs a fresh controller. Node also recommends checking that the signal is not already aborted before adding an abort listener, and using a once-only listener ([Node.js v26.13.1 Global objects](https://nodejs.org/api/globals.html)).

### Request Versus An Already-Produced Effect

No inspected source promises that abort reverses work that has already happened. The DOM Standard's allowance that an API can ignore a signal once the operation has completed is the clearest statement that abort influences an activity that is not yet finished.

Node's `fs` documentation supplies the concrete case. Cancelling `fsPromises.writeFile()` is documented as "best effort", and "some amount of data is likely still to be written"; aborting an ongoing request does not abort individual operating-system requests but the internal buffering the write performs. `fsPromises.readFile()` rejects an aborted request with an `AbortError` under the same internal-buffering qualification ([Node.js v26.13.1 File system](https://nodejs.org/api/fs.html)). An already-aborted write is different: it rejects with `AbortError` without performing I/O, because no effect had started.

MDN's fetch example marks the same boundary at the response level: if the request is aborted after the `fetch()` call has been fulfilled but before the body has been read, reading the body rejects with an `AbortError`. Data already consumed is not returned, and data already produced elsewhere is not undone.

Teardown and rollback are also distinct at the resource level. `stream.pipeline` with an aborted signal calls `destroy` on the underlying pipeline with an `AbortError`, and `stream.addAbortSignal` behaves like calling `.destroy(new AbortError())` on the stream, or `controller.error(new AbortError())` for web streams ([Node.js v26.13.1 Stream](https://nodejs.org/api/stream.html)). Destruction releases resources; it does not restore bytes already written downstream. Aborting a child process is likewise documented as similar to killing it, and killing stops a process; it does not revert a file or a message the process already produced.

The stopping point is therefore API-specific and is not stated as a numeric guarantee. "Best effort" with likely partial data is the opposite of a rollback promise, and nothing on this page turns it into one.

### Cancelling A Wait Versus Destroying The Work

Node's stream surface separates two operations under the same signal mechanism, and that separation is the clearest counterexample to "this API takes a signal, so aborting stops it".

- `stream.finished(stream[, options], callback)` with `signal` aborts the wait for the stream to finish. The documentation states that the underlying stream is not aborted, that the callback receives an `AbortError`, and that the listeners this function added are removed. The `signal` option was added in Node.js v15.11.0 ([Node.js v26.13.1 Stream](https://nodejs.org/api/stream.html)).
- `stream.pipeline` with `{ signal }` destroys the underlying pipeline, calling `destroy` with an `AbortError`.
- `stream.addAbortSignal(signal, stream)` behaves like `.destroy(new AbortError())` on the stream; it carries a Stability 0 documentation-only deprecation for long-lived stream resources (DEP0209).
- `events.once(emitter, name[, options])` with `signal` cancels waiting for the event and rejects the pending promise with an `AbortError`; the option was added in v15.0.0 ([Node.js v26.13.1 Events](https://nodejs.org/api/events.html)).
- `timers/promises` functions accept `options.signal` to cancel the scheduled timeout and reject with an `AbortError` ([Node.js v26.13.1 Timers](https://nodejs.org/api/timers.html)).

The consequence for diagnosis is that a documented signal parameter answers only "may this operation be asked to stop", not "what will stop". A subscription, a buffered write, a destroyed stream, and a killed process leave different residue behind, and the terminal outcome differs too: a callback error, a rejected promise, a discarded race result, or an emitted `'error'` event.

### Runtime And API Bounds

Node documents signal acceptance on named surfaces, each with its own version note: `fetch`; `events.once` (v15.0.0) and `events.addAbortListener` (stable in v24.0.0 and v22.16.0, changed in v26.11.0); `fs`/`fs/promises`, where `readFile` and `writeFile` gained `signal` in v15.2.0 and v14.17.0, `createReadStream` supported it from v15.5.0, and `filehandle.stat` gained it in v26.1.0; `stream.finished` (v15.11.0) and `stream.pipeline`; `timers/promises`; and the `child_process` methods listed above ([Node.js v26.13.1 Global objects](https://nodejs.org/api/globals.html); [Node.js v26.13.1 File system](https://nodejs.org/api/fs.html); [Node.js v26.13.1 Events](https://nodejs.org/api/events.html); [Node.js v26.13.1 Timers](https://nodejs.org/api/timers.html)). The list is the inspected subset, not an exhaustive inventory.

Bun documents signal acceptance on `fetch` through `RequestInit.signal`, on `Bun.spawn` through a signal that "kills the subprocess when aborted", on `node:http` request options, and on `ReadableStream.pipeThrough`, where a signal cancels the source and aborts the destination unless `preventCancel` or `preventAbort` is set ([Bun RequestInit.signal](https://bun.com/reference/globals/RequestInit/signal); [Bun spawn signal](https://bun.com/reference/globals/bun/Spawn/BaseOptions/signal); [Bun node:http RequestOptions.signal](https://bun.com/reference/node/http/RequestOptions/signal); [Bun ReadableStream.pipeThrough](https://bun.com/reference/globals/ReadableStream/pipeThrough)).

Bun's spawn behavior has two stages. An already-aborted signal throws an `AbortError` synchronously before any process is created, so the caller never receives a process handle and nothing is spawned. A later abort kills the running process with the signal named by `killSignal`, which defaults to `SIGTERM` ([Bun spawn signal](https://bun.com/reference/globals/bun/Spawn/BaseOptions/signal)). Both stages are Bun-specific and API-specific: Node's `child_process` documents its own bounds, the analogous Bun behavior is documented on `Bun.spawn`, and neither page is evidence about the other runtime. Node's `events.addAbortListener` and `stream.addAbortSignal` helpers appear in Node documentation; the inspected Bun reference pages do not document them, which is a documentation-scope observation and not a claim that Bun implements or omits them.

### Promise Coordination Does Not Cancel

`Promise.race()` accepts an iterable of promises and returns a promise that settles with the eventual state of the first input to settle: it fulfils if the first settlement fulfils and rejects if the first settlement rejects. It is always asynchronous, and an empty iterable leaves the returned promise pending forever ([MDN Promise.race()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/race); [ECMAScript 2027 draft, `PerformPromiseRace`](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#sec-promise.race)).

Settling does not cancel the losing operations, and it does not unsubscribe the handlers attached to their promises. The losing result is discarded rather than delivered, and handlers on a long-lived pending promise can accumulate across repeated races. The normative algorithm supports the same reading: `PerformPromiseRace` invokes `then` on each input with the result capability's resolve and reject functions and contains no cancel or unsubscribe step, and the promise machinery has no first-class cancellation protocol.

Stopping losing work is therefore a separate action performed through whatever mechanism the underlying operation supports: a `clearTimeout` or cancellation token, an explicit `destroy`, `kill`, or `cancel` call, an `AbortSignal`, or another API-specific route. `AbortSignal` is not the exclusive route and no operation is claimed to have to accept one.

Two bounds keep the statement honest. First, it describes promise machinery, not a universal claim that every underlying operation keeps running in every runtime; whether a socket, timer, or subprocess continues is answered by that API. Second, MDN's statement that losing rejections do not trigger `unhandledrejection` is bounded to inputs the combinator successfully iterated and attached a `then` handler to; a throwing iterator or a throwing `then` invocation surfaces by rejecting the combinator's own promise, and unrelated chains are unaffected ([MDN Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)).

A bounded example shows the cleanup the race does not perform. It is scoped to Node.js v26.13.1 `timers/promises` signal behavior:

```ts
import { setTimeout as delay } from "node:timers/promises";

async function firstOfTwoWaits(): Promise<string> {
  const controller = new AbortController();
  const slow = delay(10_000, "slow", { signal: controller.signal });
  const fast = delay(100, "fast");

  try {
    return await Promise.race([slow, fast]);
  } finally {
    // The race returns "fast"; the 10 s timer is still scheduled.
    // Aborting the signal cancels that timer through its own signal option.
    controller.abort();
  }
}
```

`fast` settles first, so the race fulfils with `"fast"` and `slow`'s result is ignored. Without the `controller.abort()` call, the losing timer would remain scheduled: `Promise.race` supplies no stop mechanism, and the abort rejects `slow` with an `AbortError` that the already-settled race ignores. Replace the losing timer with a socket, a subprocess, or a stream, and the corresponding stop mechanism is the one that API documents.

## Timers And Process Lifetime

### Timer Thresholds And Referencing

Node documents a timer delay as a threshold, not an exact deadline: callbacks are not guaranteed to run at a precise time or in a guaranteed order, and event-loop work can delay them ([Node.js v26.13.0 Timers](https://nodejs.org/download/release/v26.13.0/docs/api/timers.html)). A stated delay therefore supports a lower-bound expectation, not a measurement of when the callback ran.

`Timeout` and `Immediate` objects are referenced by default, which means they keep the event loop alive. `unref()` removes that effect, so the object alone no longer needs to keep the process running, and a later `ref()` restores it. The distinction matters at shutdown: an outstanding referenced timer is one reason a process that "finished its work" stays alive.

Timer phase ordering carries the Node.js 20 and libuv 1.45.0 change described above, so an ordering claim should name the runtime generation it describes. Bun's inspected pages list `setTimeout`, `setInterval`, and their clear functions, and document `Bun.sleep()` as asynchronous and `Bun.sleepSync()` as blocking ([Bun Web APIs](https://bun.com/docs/runtime/web-apis); [Bun Utils](https://bun.com/docs/runtime/utils)). They do not establish precision or reference semantics for Bun's global timers; Worker `ref()`/`unref()` and subprocess `unref()` are resource-specific controls, not a global timer contract ([Bun Workers](https://bun.com/docs/runtime/workers); [Bun Child Process](https://bun.com/docs/runtime/child-process)).

### Shutdown And Uncaught Errors

Node emits `beforeExit` when the event loop empties. A handler may schedule asynchronous work and thereby keep the process running; `exit` listeners are synchronous-only, and queued asynchronous work is abandoned once exit begins. `process.exit()` forces the process to exit as quickly as possible even when asynchronous operations are still pending ([Node.js v26.13.0 Process](https://nodejs.org/download/release/v26.13.0/docs/api/process.html)).

`uncaughtException` is documented as a last-resort path for synchronous cleanup before termination, not as ordinary recovery. It is not a graceful shutdown hook: a handler that schedules asynchronous work cannot rely on that work completing, because the process is already on its way out.

Signal behavior is platform-sensitive. Installing a `SIGINT` or `SIGTERM` listener removes the default termination behavior on non-Windows systems, which transfers the decision to the application, and the documentation records Windows-specific differences. Signal events are unavailable on Node Worker threads ([Node.js v26.13.0 Process](https://nodejs.org/download/release/v26.13.0/docs/api/process.html)).

Bun documents `beforeExit` and `exit` and states that neither fires when the process is killed by a signal it has no listener for; its guide shows a signal listener that calls `process.exit()` ([Bun Listen To OS Signals](https://bun.com/guides/process/os-signals.md)). Bun also documents that an active worker keeps the spawning process alive, that `terminate()` exits as soon as possible, that a worker's `close` event can precede full exit, and that a parent waits for child processes by default with `unref()` available ([Bun Workers](https://bun.com/docs/runtime/workers); [Bun Child Process](https://bun.com/docs/runtime/child-process)).

No inspected source states one shutdown contract across the runtimes. Whether shutdown waits depends on pending handles and referenced timers, on whether a listener replaced a default signal behavior, on workers and children, and on per-resource lifetime controls; none of those is a portable sequence.

### Concurrent Modification Of One File

Node documents that filesystem promise operations use the thread pool and are not synchronized for concurrent modification of the same file, and it warns that data corruption can occur ([Node.js v26.13.0 File system](https://nodejs.org/download/release/v26.13.0/docs/api/fs.html#threadpool-usage)). Thread-pool execution explains why two awaits can interleave without any JavaScript parallelism: the operations run off-thread and their results return to the loop in completion order.

The statement is scoped to Node's `fs` promise operations on one file. It names no locking mechanism, no ordering guarantee between separate writes, and no equivalent claim about Bun's file APIs. Coordinating writers is an application decision, and it is not supplied by `await`.

## Mechanism Versus Convention

Two kinds of statement appear in this material and should not be read as interchangeable.

- **Mechanisms** are documented behavior: `write()` returns `false` at the threshold, a referenced timer keeps the loop alive, `stream.finished` cancels only the wait, `PerformPromiseRace` attaches handlers without cancelling, and `Bun.spawn` throws synchronously for an already-aborted signal. Each is bounded by the runtime, version, and API named with it.
- **Conventions** are project choices: which `highWaterMark` value to set, whether to thread one signal through helper parameters, whether to compare `error.name` against `AbortError` or read `signal.reason`, whether to use a worker or a child process, and whether to stop a process with a signal or an explicit `kill()`. These choices have no runtime guarantee behind them.

The rationale for a convention is reader clarity, consistency across a codebase, and the observable consequences the chosen mechanism actually documents. Passing a signal parameter through every helper, for example, does not make the helper cancellable; only an API that observes the signal can react. Threading a single controller through unrelated operations does not give them a shared stop order either, because each API decides what the abort means for it. Presenting such a choice as language behavior would misstate both the mechanism and the evidence.

## Worked Contrasts

### `await` Does Not Make JavaScript Parallel

Two timed waits overlap; two computations do not. The difference is waiting versus running, not threads.

```ts
import { setTimeout as delay } from "node:timers/promises";

async function measureWaits(): Promise<{ sequential: number; concurrent: number }> {
  const sequentialStart = performance.now();
  await delay(50);
  await delay(50);
  const sequential = performance.now() - sequentialStart;

  const concurrentStart = performance.now();
  await Promise.all([delay(50), delay(50)]);
  const concurrent = performance.now() - concurrentStart;

  return { sequential, concurrent };
}
```

The sequential pair takes roughly twice as long as the concurrent pair, because the first wait must finish before the second starts while the two waits inside `Promise.all` are both outstanding at once. No JavaScript runs in parallel in either case: the continuations still execute on the event-loop thread. Replace the delays with a synchronous loop and the totals add up in both forms; `Promise.all` overlaps waiting, not computation. Timer delays are thresholds, so the measured values are approximate ([Node.js v26.13.0 Timers](https://nodejs.org/download/release/v26.13.0/docs/api/timers.html)).

### A Signal Only Where The API Documents It

A signal is useful only when the called API documents that it observes one. `fsPromises.readFile` does, and the same code path shows the cancellation-versus-effect boundary.

```ts
import { readFile } from "node:fs/promises";

async function readConfig(path: string): Promise<string | undefined> {
  try {
    return await readFile(path, {
      encoding: "utf8",
      signal: AbortSignal.timeout(2_000),
    });
  } catch (error) {
    const name = error instanceof Error ? error.name : "";
    if (name === "AbortError" || name === "TimeoutError") return undefined;
    throw error;
  }
}
```

`readFile` accepts `signal` from Node.js v15.2.0 and v14.17.0, and an aborted read rejects with an `AbortError` ([Node.js v26.13.1 File system](https://nodejs.org/api/fs.html)). `AbortSignal.timeout()` documents a `"TimeoutError"` reason, so the check accepts either name rather than assuming one reason across APIs ([MDN AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal)). The example is scoped to these pages and their versions.

The contrast is a helper that takes a `signal` parameter and never passes it to an operation that observes it. Nothing happens on abort: the parameter is data, and only an accepting API turns it into an effect. A fresh controller is also required per cancellable operation, because an aborted signal cannot be re-armed.

### Waiting For `drain` In A Write Loop

Ignoring `write()`'s return value is how a producer outruns its destination. The loop below waits at the documented cue and observes completion separately.

```ts
import { once } from "node:events";
import { createWriteStream } from "node:fs";

async function writeChunks(path: string, chunks: Iterable<string>): Promise<void> {
  const out = createWriteStream(path);

  for (const chunk of chunks) {
    if (!out.write(chunk)) {
      await once(out, "drain");
    }
  }

  out.end();
  await once(out, "finish");
}
```

`write()` returns `false` once the buffer reaches `highWaterMark`, and `'drain'` marks the point where writing may resume; ignoring that cue keeps buffering chunks and increases memory use ([Node.js v26.13.0 Stream](https://nodejs.org/download/release/v26.13.0/docs/api/stream.html)). Waiting is flow control rather than completion, so the loop ends with `end()` and observes the terminal outcome through `'finish'`. `events.once` rejects if the emitter emits `'error'` while waiting, which is why the same helper reports a failed write instead of hanging silently ([Node.js v26.13.1 Events](https://nodejs.org/api/events.html)). The threshold is not a total-memory limit, and a destination may still apply its own buffering.

## Diagnose A Partial Effect After Cancellation

A cancelled request can have already written part of its effect, so the caller observes both a cancellation and a partial result. Diagnose the two separately.

1. Record the API, the runtime and version, and what that API documents the signal as doing: cancelling a wait, destroying a stream, killing a process, or stopping internal buffering. A signal parameter alone does not identify the response.
2. Record which terminal outcome the caller actually observed: a rejected promise or callback error, an emitted `'error'` event, a discarded result after a settled race, or a value returned before the abort took effect. A race result says nothing about the loser.
3. Check what had already been produced before the abort arrived: a partially written file under the documented "best effort" behavior, bytes already flushed downstream by a destroyed pipeline, side effects of a killed child process, or a partially consumed response body. Already-aborted operations that never started are a different finding, because Node documents those as rejecting without I/O.
4. Check whether the operation's own stop mechanism was invoked at all. A timer that remains referenced, a signal never passed to an observing API, and a losing promise in a settled race all continue without any error, and the first two can also keep the process alive.
5. If the expected stop behavior cannot be established from the API's documentation, say so. No inspected source promises an exact stopping point, and an observed partial result does not prove that more work was attempted than the API allows.

The observable consequence is not a rollback: the cancellation and the partial effect are both real, and the fix belongs to whatever coordination or idempotency the operation's contract supports.

## Limits And Version Boundaries

- Node.js claims are bounded to the released pages named above: v26.13.0 for the event-loop, worker, stream flow-control, timer, process, and filesystem-pool material, and v26.13.1 for cancellation surfaces and the wait-versus-effect boundaries. Node Learn pages are rolling and unversioned.
- Timer phase ordering carries the libuv 1.45.0 and Node.js 20 change, so a phase-level account describes that generation and later; platform differences remain.
- Bun documentation is rolling and names no release baseline on the inspected pages. Bun's stream, timer, and lifecycle behavior is documented separately from Node's, and no cross-runtime shutdown contract or behavioral parity is claimed. A missing statement on an inspected Bun page is an evidence limit, not proof of absence.
- Cancellation is API-specific. The signal-accepting surfaces listed here are the inspected subset, not an exhaustive inventory, and no operation is claimed to have to accept a signal.
- `Promise.race()` supplies no cancellation. The settlement and losing-work statements describe promise machinery under current MDN wording and the ECMAScript 2027 draft; the draft's clause numbering varies between drafts, and MDN is rolling.
- The WHATWG DOM Living Standard was last updated on 14 November 2026 and may change. Its text states a request model for abort, not a rollback guarantee.
- MDN's disagreement about identifying a timeout through `AbortSignal.any()` remains visible: the reason object is preserved, source attribution has no separate field, and a `TimeoutError` name is an indication rather than proof in every configuration.
- No inspected source promises reversal of an already-produced effect, a numeric partial-effect bound, delivery or flush completion, or a universal ordering between concurrent operations. Statements describe publisher documentation, not measurements of a specific project.
- The scope is TypeScript-only: no JavaScript or mixed-language eligibility, no `allowJs` or `checkJs` guidance, and no JSDoc typing of `.js` files. Nothing here selects, prescribes, or assumes Vite; an incidental dependency edge is neither evidence of direct selection nor proof of its absence. Nothing on this page forms an implicit pipeline, and no compatibility promise follows for another runtime, package, or version.
- The repository's deterministic utilities under `scripts/node/` have their own Bun and repository conventions. Those conventions are not ordinary project defaults.

## Ownership And Routing

This page is passive interpretation. Behavior or cancellation changes that alter production behavior go to the production owner, `node-project-writer -> reference/change-design-and-validation.md`. How asynchronous code is written and how caller-visible async failures are shaped belong to the style page `node-source-style-guide -> reference/async-and-error-boundaries.md`, and the caller-observable contract of a change belongs to `node-project-writer -> reference/behavior-and-caller-contracts.md`. Dependency, lockfile, and environment changes go to `node-project-dependencies -> reference/evaluation-and-environment-changes.md`.

Configuration sources, parsing, validation, and exposure controls are covered in [Configuration Loading And Validation](configuration-loading-and-validation.md). Diagnostic output, runtime reports, and telemetry export are covered in [Diagnostics And Telemetry](diagnostics-and-telemetry.md). Runtime execution, module resolution, and the mixed manager-and-runtime reading are covered in [Runtime And Project Structure](runtime-and-project-structure.md). Manager, lockfile, workspace, and invocation evidence is covered in [Manager, Workspace, And Invocation Evidence](manager-workspaces-and-invocation.md). No approval, behavior change, configuration change, or completion evidence follows from this page.
