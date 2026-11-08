# Async And Concurrency

## Choose A Model For The Workload

Keep sequential synchronous code when work is ordered or no concurrency need is
established. Consider asyncio for independent waits with native async APIs or an
already-async interface; consider a thread for blocking synchronous I/O that must not
stall an event loop. Consider processes or other models for CPU work only after
accounting for runtime/build, serialization, startup, and lifecycle costs. Python's
concurrency overview describes available models and workload dimensions; it does not
prove a speedup for a particular application. ([Python 3.15.2
concurrent execution](https://docs.python.org/3.15/library/concurrency.html).)

On one event-loop thread, only one task body runs at a time. A blocking file/network
call or long CPU calculation inside a coroutine prevents other tasks and I/O callbacks
from progressing until it yields control. `async def` changes the interface, not the
blocking behavior of calls inside it.

For ordinary GIL-enabled CPython, threads can overlap I/O but generally do not execute
CPU-bound Python bytecode in parallel. Processes can supply parallel execution at the
cost of startup, serialization, memory, and lifecycle management. Extension code that
releases the GIL, other interpreters, and optional free-threaded builds can change that
trade-off; free-threaded CPython support began in 3.13 and is not the default build.
Python 3.14+ also supplies `InterpreterPoolExecutor`, with a separate interpreter per
worker rather than an ordinary shared-object thread pool. Measure the actual runtime
and workload instead of applying the GIL rule to every build or extension. See
[threading](https://docs.python.org/3.15/library/threading.html#gil-and-performance-considerations)
and [executor models](https://github.com/python/cpython/blob/v3.15.2/Doc/library/concurrent.futures.rst).

## Make Coroutine And Task Lifetime Explicit

Calling an `async def` creates a coroutine object; it does not schedule the body. Await
it in the current flow or create a task when concurrent ownership is intended:

```python
import asyncio


async def caller():
    coroutine = load_record("a-17")  # Created, not scheduled by this call.
    task = asyncio.create_task(coroutine)
    return await task
```

Assumption: `load_record` is an async function. The coroutine is created first and
scheduled by `create_task`; its result becomes available when `caller` awaits the task.
If a caller returns or discards the coroutine without awaiting or scheduling it, its
body has not run. Python 3.15.2 documents `create_task()` and `TaskGroup` for scheduled task
ownership; `TaskGroup` is available from Python 3.11. ([Python 3.15.2 asyncio
tasks](https://docs.python.org/3.15/library/asyncio-task.html).)

For related child work, `TaskGroup` and default `gather()` have different failure
behavior. A failing child in a TaskGroup cancels unfinished siblings, waits for them,
and reports non-cancellation failures as an exception group. Default `gather()` passes
the first exception to its awaiter while other submitted awaitables continue. Choose
based on whether sibling work should continue; neither undoes external effects already
completed (see the asyncio task reference above).

```python
import asyncio


async def fetch_pair(client, first_id, second_id):
    async with asyncio.TaskGroup() as group:
        first = group.create_task(client.fetch(first_id))
        second = group.create_task(client.fetch(second_id))
    return first.result(), second.result()
```

Assumption: Python 3.11+ and a client whose `fetch` method is awaitable. If one child
fails, unfinished sibling tasks are cancelled and awaited; a completed remote write is
not rolled back. The code is illustrative and was not run.

Outside a group, background work still needs an owner that retains task references,
observes results/exceptions, and defines shutdown. The event loop holds weak references;
creating a task and discarding it is not durable work supervision. A done callback that
only removes a task from a set does not handle its failure. Decide whether the owner
awaits it, retrieves and reports its exception, or transfers its outcome to another
supervisor. Cancelling a task before it starts can prevent its coroutine body—and
therefore its `finally` block—from running; avoid acquiring an external resource for
that coroutine without a separate acquisition owner. The task-start caveat is documented
in a [historical CPython discussion](https://github.com/python/cpython/issues/98275),
not a promise about scheduler ordering.

## Treat Queue Bounds As A Behavior Choice

An `asyncio.Queue` is unbounded when `maxsize=0`. A positive capacity makes `put()` wait
while the queue is full; `put_nowait()` raises `QueueFull` instead. A bound therefore
changes producer behavior under saturation; it does not choose whether the application
should wait, reject, shed work, or retry, nor does it choose a suitable capacity. (
[Python 3.15.2 asyncio queues](https://docs.python.org/3.15/library/asyncio-queue.html).)

```python
import asyncio


async def enqueue(queue, item):
    await queue.put(item)   # Waits if the configured queue is full.
```

Call `enqueue` with `asyncio.Queue(maxsize=2)` to see the bounded-wait behavior; the
size `2` is only to make the example legible, not a service recommendation. Replacing
`await queue.put(item)` with `queue.put_nowait(item)` raises `QueueFull` when no slot is
available, so producer code must define what happens to that item. Asyncio queues and
synchronization primitives are not thread-safe; use a documented thread bridge when
crossing execution domains.

## Match Synchronization To The Execution Domain

An async lock protects an invariant among cooperating tasks; it does not protect that
state from OS threads. Async events signal state, conditions pair notification with
a predicate, and semaphores limit simultaneous access. Their invariant, capacity, and
ownership must be explicit. For threads, use thread-safe primitives and `queue.Queue`
rather than sharing an `asyncio.Queue` or `asyncio.Lock` directly.

The event loop exposes bridges for crossing the thread boundary. A worker thread can
submit an awaitable to the loop that owns an async queue:

```python
import asyncio


def submit_from_worker(loop, queue, item, wait_seconds):
    future = asyncio.run_coroutine_threadsafe(queue.put(item), loop)
    return future.result(timeout=wait_seconds)
```

Assumptions: this function runs in a different OS thread, `loop` is running, and
`queue` belongs to that loop. `put()` retains bounded-queue waiting semantics. Do not
call the blocking `result()` on the loop's own thread: it would prevent the submitted
coroutine from making progress. If the thread's wait times out, the item may still be
queued later; timeout is not automatic cancellation or a safe reason to submit it twice.
For callbacks rather than coroutines, `loop.call_soon_threadsafe()` is the corresponding
bridge. See [asyncio multithreading](https://docs.python.org/3.15/library/asyncio-dev.html#concurrency-and-multithreading)
and [async synchronization](https://docs.python.org/3.15/library/asyncio-sync.html).

## Cancellation Does Not Mean The Work Stopped

Task cancellation is cooperative and is delivered at an await opportunity. Cleanup can
run in `finally`, after which `CancelledError` should generally propagate. Moving a
blocking call to `asyncio.to_thread()` keeps that call off the event-loop thread, but
cancelling the awaiting coroutine does not forcibly stop an already-running worker
function. Executor cancellation also distinguishes pending work from running work;
shutdown with `cancel_futures=True` cancels pending futures, not running calls. (
[Python 3.15.2 asyncio tasks](https://docs.python.org/3.15/library/asyncio-task.html), [event loop](https://docs.python.org/3.15/library/asyncio-eventloop.html), and [CPython v3.15.2 futures](https://github.com/python/cpython/blob/v3.15.2/Doc/library/concurrent.futures.rst).)

This matters when a worker performs an external side effect: stopping the caller's
wait is not evidence that the side effect was cancelled. The general timeout/deadline
and retry contract belongs to [Source and API](source-and-api.md).

## Retrieve Worker Outcomes And Plan Shutdown

An executor future makes worker failure observable at the result boundary:

```python
from concurrent.futures import ThreadPoolExecutor


def load_in_worker(read_record, key):
    with ThreadPoolExecutor(max_workers=2) as pool:
        future = pool.submit(read_record, key)
        return future.result()
```

Assumption: `read_record` is a synchronous callable suitable for a thread. Its return
value becomes the function's result; its exception is raised by `future.result()`.
The size `2` is illustrative, not a sizing recommendation. A bare `Thread.join()`
instead waits for thread termination without re-raising its failure; uncaught thread
exceptions go through `threading.excepthook()`. Choose an explicit outcome channel.

An executor context normally waits for submitted work at exit. Even
`shutdown(wait=False)` does not make Python exit while executor work remains;
`cancel_futures=True` affects pending calls only. `asyncio.run()` handles shutdown of
its default executor, so stopping the coroutine can still leave process-exit waiting
on blocking worker code. A bounded shutdown requirement needs cooperative worker
timeouts/stopping or another isolation design, not merely an async timeout wrapper.
A pool can also deadlock if a worker waits on a future that needs the same exhausted
pool. See the [tagged futures documentation](https://github.com/python/cpython/blob/v3.15.2/Doc/library/concurrent.futures.rst)
and [event-loop executor shutdown](https://docs.python.org/3.15/library/asyncio-eventloop.html#asyncio.loop.shutdown_default_executor).

Process pools add a different boundary: submitted callables, arguments, and results
must be picklable and workers need an importable `__main__`. Libraries should allow
caller-supplied multiprocessing contexts rather than silently choose a start method;
context-specific locks and queues may not interoperate. Forced termination can skip
`finally`/exit handlers, corrupt IPC queues, or strand locks. It is not graceful task
cancellation. Python 3.14 changed default start methods away from `fork`; check the
actual interpreter/platform rather than assuming inherited state. See
[multiprocessing contexts and guidelines](https://docs.python.org/3.15/library/multiprocessing.html).

## Brownfield Decision

Preserve the existing sync/async API, runtime support, task ownership, worker model,
shutdown expectations, and overload behavior unless the requested outcome and evidence
justify a bounded change. Before a performance claim, identify a representative
bottleneck; a concurrency model alone does not establish throughput or latency benefit.
Do not invent pool size, queue capacity, concurrency limit, or shutdown budget.

The mechanics here are scoped to Python 3.15.2 documentation. `TaskGroup` requires
Python 3.11+, and `asyncio.to_thread()` requires Python 3.9+. Check the actual
implementation/build and project support contract before relying on them. No workload
or target runtime was supplied.
