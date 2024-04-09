import threading
from typing import Callable


class Once:
    """Takes a function and ensures 'call once' semantics.
    e.g. print_me_once = Once(lambda: print('print me'))
         print_me_once() # Prints 'print me'.
         print_me_once() # Does nothing.
    """

    def __init__(self, f: Callable[[], None]):
        self._f = f
        self._lock = threading.Lock()
        self._called = False

    def __call__(self) -> None:
        """Execute, exactly once, the function passed to the constructor."""
        # More than one caller might have a handle to an instance of Once at
        # the same time. Acquire a lock so that only one runs to completion.
        with self._lock:
            if not self._called:
                try:
                    self._f()
                finally:
                    self._called = True


# The version of Once that allows calling async functions (AsyncOnce) was
# unused and removed in https://github.com/reboot-dev/respect/pull/2160.
# To reinstate the async implementation, please take a look at that commit.
