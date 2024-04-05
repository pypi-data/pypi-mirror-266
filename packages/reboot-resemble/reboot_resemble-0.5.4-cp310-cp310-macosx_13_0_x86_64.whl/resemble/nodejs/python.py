import asyncio
import base64
import gzip
import importlib
import os
import sys
import tempfile
import threading
from resemble.cli.directories import chdir


class EventLoopThread:
    """Helper class for creating and running an event loop on a thread and
    performing callbacks on said event loop from C++ via caling
    `run_callback_on_event_loop()`.
    """

    def __init__(self):
        # Need to keep multiprocessing initialization from failing
        # because there is more than one thread running.
        #
        # If this ends up being an issue we can try and revisit how to
        # initialize multiprocessing before creating any threads, but
        # that poses some serious challenges given that in order to
        # embed the Python interpreter we need to create a thread that
        # is different than the nodejs thread to begin with.
        #
        # See 'resemble/aio/tests.py'.
        os.environ['RESEMBLE_NODEJS_EVENT_LOOP_THREAD'] = 'true'

        self._loop = asyncio.new_event_loop()

        def run_forever():
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()

        self._thread = threading.Thread(target=run_forever)
        self._thread.start()

    def run_callback_on_event_loop(self, callback):
        self._loop.call_soon_threadsafe(callback)


def import_py(module: str, base64_gzip_py: str):
    """Helper for importing Python source files from encoded base64 strings."""
    # If we've already loaded this module, return. This may be
    # possible if nodejs tries to load a '.js' file more than once
    # itself, which we haven't seen but have read is possible, so we
    # are being defensive here.
    if module in sys.modules:
        return

    # Write the source file out to disk in order to load it back in.
    #
    # We tried using `importlib.util` to create our own spec and
    # loader, and while we could successfully load some code, we
    # couldn't properly reference that loaded code in other files.
    with tempfile.TemporaryDirectory() as directory:
        with chdir(directory):
            path = f"{module.replace('.', os.path.sep)}.py"
            os.makedirs(os.path.dirname(path))
            with open(path, "w") as file:
                file.write(
                    gzip.decompress(
                        base64.b64decode(base64_gzip_py.encode('utf-8'))
                    ).decode('utf-8')
                )
                file.close()

            # This does the actual loading.
            importlib.import_module(module)

            # As suggested in the docs for
            # `importlib.import_module()`, this may be necessary, so
            # we're just doing it defensively.
            importlib.invalidate_caches()
