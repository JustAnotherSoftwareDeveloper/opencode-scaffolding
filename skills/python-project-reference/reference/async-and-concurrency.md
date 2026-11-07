# Async And Concurrency

## Choose A Model For The Workload

Keep sequential synchronous code when work is ordered or no concurrency need is
established. Consider asyncio for independent waits with native async APIs or an
already-async interface; consider a thread for blocking synchronous I/O that must not
stall an event loop. Consider processes or other models for CPU work only after
accounting for runtime/build, serialization, startup, and lifecycle costs. Python's
concurrency overview describes available models and workload dimensions; it does not
prove a speedup for a particular application. (Dossier C20-C22; [Python 3.15.2
concurrent execution](https://docs.python.org/3.15/library/concurrency.html).)

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
ownership; `TaskGroup` is available from Python 3.11. (C20; [Python 3.15.2 asyncio
tasks](https://docs.python.org/3.15/library/asyncio-task.html).)

For related child work, `TaskGroup` and default `gather()` have different failure
behavior. A failing child in a TaskGroup cancels unfinished siblings, waits for them,
and reports non-cancellation failures as an exception group. Default `gather()` passes
the first exception to its awaiter while other submitted awaitables continue. Choose
based on whether sibling work should continue; neither undoes external effects already
completed. (C31; same asyncio task reference.)

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

## Treat Queue Bounds As A Behavior Choice

An `asyncio.Queue` is unbounded when `maxsize=0`. A positive capacity makes `put()` wait
while the queue is full; `put_nowait()` raises `QueueFull` instead. A bound therefore
changes producer behavior under saturation; it does not choose whether the application
should wait, reject, shed work, or retry, nor does it choose a suitable capacity. (C21;
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

## Cancellation Does Not Mean The Work Stopped

Task cancellation is cooperative and is delivered at an await opportunity. Cleanup can
run in `finally`, after which `CancelledError` should generally propagate. Moving a
blocking call to `asyncio.to_thread()` keeps that call off the event-loop thread, but
cancelling the awaiting coroutine does not forcibly stop an already-running worker
function. Executor cancellation also distinguishes pending work from running work;
shutdown with `cancel_futures=True` cancels pending futures, not running calls. (C31;
[Python 3.15.2 asyncio tasks](https://docs.python.org/3.15/library/asyncio-task.html), [event loop](https://docs.python.org/3.15/library/asyncio-eventloop.html), and [CPython v3.15.2 futures](https://github.com/python/cpython/blob/v3.15.2/Doc/library/concurrent.futures.rst).)

This matters when a worker performs an external side effect: stopping the caller's
wait is not evidence that the side effect was cancelled. The general timeout/deadline
and retry contract belongs to [Source and API](source-and-api.md).

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
