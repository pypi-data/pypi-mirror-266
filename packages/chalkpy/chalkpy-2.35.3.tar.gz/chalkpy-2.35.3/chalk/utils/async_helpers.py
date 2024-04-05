from __future__ import annotations

import asyncio
import contextlib
import queue
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, AsyncIterable, AsyncIterator, Callable, Coroutine, Generic, Iterable, TypeVar

from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


@contextlib.asynccontextmanager
async def async_null_context(obj: T) -> AsyncIterator[T]:
    yield obj


async def async_enumerate(iterable: AsyncIterator[T] | AsyncIterable[T]):
    i = 0
    async for x in iterable:
        yield i, x
        i += 1


_RUNNING_TASKS: set[asyncio.Task[Any]] = set()


def run_coroutine_fn_threadsafe(
    loop: asyncio.AbstractEventLoop, coro_fn: Callable[P, Coroutine[Any, Any, T]], /, *args: P.args, **kwargs: P.kwargs
) -> Future[T]:
    """Similar to asyncio.run_coroutine_threadsafe(), but it constructs the coroutine inside the main event loop thread.
    This helps eliminate errors related to constructing corotuines that will never be awaited if the event loop is closed before
    the coroutine could be executed"""
    ans: Future[T] = Future()

    def _chain_future(asyncio_res: asyncio.Future[T]):
        try:
            ans.set_result(asyncio_res.result())
        except BaseException as exc:
            ans.set_exception(exc)

    def _run_on_event_loop_thread():
        if ans.set_running_or_notify_cancel():
            t = asyncio.create_task(coro_fn(*args, **kwargs))
            _RUNNING_TASKS.add(t)
            t.add_done_callback(_RUNNING_TASKS.remove)
            t.add_done_callback(_chain_future)

    loop.call_soon_threadsafe(_run_on_event_loop_thread)
    return ans


def _put_on_queue(q: queue.Queue[T | ellipsis], finished_event: threading.Event, x: T | ellipsis):
    if finished_event.is_set():
        return
    q.put(x)


def _yield_to_queue(q: queue.Queue[T | ellipsis], finished_event: threading.Event, it: Iterable[T]):
    try:
        for x in it:
            _put_on_queue(q, finished_event, x)
    finally:
        _put_on_queue(q, finished_event, ...)


class to_async_iterable(Generic[T]):
    """Runs a blocking iterator in an executor, and yields batches asynchronously as they become available.

    This function-like class runs the generator in a separate thread, and uses a queue to share results between the background thread
    and the event loop. This approach ensures that the generator context is spun with the correct parent
    """

    def __init__(self, iterable: Iterable[T], executor: ThreadPoolExecutor | None = None):
        super().__init__()
        self._iterable = iterable
        self._executor = executor
        if self._executor is not None:
            if self._executor._max_workers < 2:
                raise ValueError("The executor must have at least two threads; otherwise, it will deadlock")
        self._q: queue.Queue[T | ellipsis] = queue.Queue(maxsize=1)
        self._finished_event = threading.Event()
        self._executor = executor
        self._task = asyncio.get_running_loop().run_in_executor(
            executor, _yield_to_queue, self._q, self._finished_event, iterable
        )

    def __aiter__(self):
        return self

    async def __anext__(self) -> T:
        try:
            item = await asyncio.get_running_loop().run_in_executor(self._executor, self._q.get)
        except asyncio.CancelledError:
            # If the task is cancelled, we still need to add something to the queue so the .get() call above doesn't hang
            # When the worker task finishes, it will either a) be before any code below runs, which is fine
            # because it is idempotent, or b) be after the the finished event is set, in which case we won't attempt to
            # append anything
            self._finished_event.set()
            try:
                self._q.put_nowait(...)
            except queue.Full:
                pass
            raise
        if item is ...:
            await self._task
            raise StopAsyncIteration
        return item

    def __del__(self):
        # If there was an exception, then the queue might still have an element in it
        # We'll first set the finished_event, and then we'll drain the queue. This will allow the
        # _yield_to_queue to successfully put another element in it, if _safe_put is blocked on q.put(...)
        # Because the finished_event is already set, it will not attempt to add yet another element, which would
        # block forever, because we aren't draining the queue any more
        # If there was no exception, then the queue should already be empty, and the task complete
        self._finished_event.set()
        try:
            self._q.get_nowait()
        except queue.Empty:
            pass
