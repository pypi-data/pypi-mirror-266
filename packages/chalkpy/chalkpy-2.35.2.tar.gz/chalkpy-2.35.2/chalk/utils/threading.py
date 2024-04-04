from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor

from typing_extensions import Final

DEFAULT_IO_EXECUTOR = ThreadPoolExecutor(
    max_workers=32,
    thread_name_prefix="chalk-io-",
)


class MultiSemaphore:
    """Semaphore-like class that takes a value for both acquire and release"""

    def __init__(self, value: int = 1, /) -> None:
        super().__init__()
        self._value = value
        self.initial_value: Final = value
        self._cond = threading.Condition()

    def acquire(self, val: int = 1, /, *, block: bool = True, timeout: float | None = None):
        if val <= 0:
            raise ValueError(f"Value ({val}) is not positive")
        if val > self.initial_value:
            raise ValueError(f"Value ({val}) is greater than the initial value ({self.initial_value})")
        if timeout is not None and timeout < 0:
            raise ValueError(f"Timeout ({timeout}) is negative, which is not supported")
        if not block:
            if timeout:
                raise ValueError("If `block` is False, then the timeout must not be specified (or be 0)")
            timeout = 0
        with self._cond:
            self._cond.wait_for(lambda: self._value - val >= 0, timeout)
            if self._value - val >= 0:
                self._value -= val
                return True
            return False

    def release(self, val: int):
        if val <= 0:
            raise ValueError(f"Value ({val}) is not positive")
        with self._cond:
            if self._value + val > self.initial_value:
                raise ValueError(f"Value ({val}) would put the semaphore above the initial value.")
            self._value += val
            self._cond.notify()
