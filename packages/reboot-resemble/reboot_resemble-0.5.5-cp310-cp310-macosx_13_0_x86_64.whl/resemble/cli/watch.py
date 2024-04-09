import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Iterator, Optional
from watchdog.events import (
    EVENT_TYPE_CLOSED,
    EVENT_TYPE_OPENED,
    FileSystemEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer


@asynccontextmanager
async def watch(
    globs: list[str],
    *,
    root_dir: Optional[str] = None,
) -> AsyncIterator[asyncio.Task[FileSystemEvent]]:
    """Helper for watching the provided globs on the file system. Implemented
    as a context manager to ensure proper cleanup of the watches."""
    loop = asyncio.get_running_loop()

    root_dir = root_dir or os.getcwd()
    globs = [
        prepared_glob for glob in globs
        for prepared_glob in _prepare_glob(root_dir, glob)
    ]

    class EventHandler(FileSystemEventHandler):

        def __init__(self, events: asyncio.Queue[FileSystemEvent]):
            super().__init__()
            self._events = events

        def on_any_event(self, event):
            if event.event_type in (EVENT_TYPE_OPENED, EVENT_TYPE_CLOSED):
                return
            if _matches_any(event.src_path,
                            globs) or _matches_any(event.dest_path, globs):
                loop.call_soon_threadsafe(
                    lambda: self._events.put_nowait(event)
                )

    events: asyncio.Queue[FileSystemEvent] = asyncio.Queue()

    handler = EventHandler(events)

    observer = Observer()
    try:
        # Recursively watch all unique path prefixes to ensure that any newly created
        # files and directories are discovered.
        path_prefixes = {
            _existing_containing_path_for_glob(root_dir, glob)
            for glob in globs
        }
        for path_prefix in path_prefixes:
            observer.schedule(handler, path=path_prefix, recursive=True)

        observer.start()
    except OSError as e:
        # The following condition signals error: 'inotify instance limit
        # reached', which happens when too many files are watched.
        if e.errno == 24:
            print('Too many files watched.')
        raise e

    events_get = asyncio.create_task(events.get())

    try:
        yield events_get
    finally:
        events_get.cancel()
        observer.stop()
        observer.join()


def _matches_any(path_str: str, patterns: list[str]) -> bool:
    path = Path(path_str)
    return any(path.match(p) for p in patterns)


def _prepare_glob(root_dir: str, glob: str) -> Iterator[str]:
    """Expands `**` globs into two candidate globs.

    Unfortunately neither `Path` nor `fnmatch` handle `**` as "zero or more directories"
    (as expected) and instead require one.
    """
    yield glob
    if "**" in glob:
        yield str(Path(*(part for part in Path(glob).parts if part != "**")))


def _existing_containing_path_for_glob(root_dir: str, glob_path: str) -> str:
    """Given a `glob`/`iglob` style glob, return an existing containing directory prefix."""
    parts = []
    for part in Path(glob_path).parts:
        if "*" in part:
            break
        parts.append(part)
    candidate = Path(*parts)

    if candidate.is_absolute():
        root = Path(candidate.root)
        candidate = candidate.relative_to(root)
    else:
        root = Path(root_dir)

    while not (root / candidate).exists():
        if candidate == candidate.parent:
            break
        candidate = candidate.parent
    return str(root / candidate)
