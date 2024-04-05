import asyncio
import logging
import respect.logging  # type: ignore[import]
import traceback
from backoff import Backoff
from datetime import datetime
from google.protobuf import any_pb2
from google.protobuf.message import Message
from resemble.aio.internals.tasks_cache import TasksCache
from resemble.aio.tasks import TaskEffect
from typing import Awaitable, Protocol
from uuid import UUID

logger = respect.logging.get_logger(__name__)
# Set logging to `WARNING` becaues we have warnings in this module
# that we expect users to want to see.
logger.setLevel(logging.WARNING)

# Limit on the total number of tasks that can be dispatched to avoid a
# denial of service attack.
#
# TODO(benh): make this configurable per service and/or actor
DISPATCHED_TASKS_LIMIT = 1024


class DispatchCallable(Protocol):
    """Helper class for capturing the type of our dispatch
    callable. Necessary because of our keyword arguments which can not
    be captured with just Callable.
    """

    def __call__(
        self,
        task: TaskEffect,
        *,
        only_validate: bool = False,
    ) -> Awaitable[Message]:
        pass


class TasksDispatcher:
    """Encapsulates dispatching and retrying tasks as well as informing
    the TasksCache about said tasks and their status.
    """

    def __init__(
        self,
        dispatch: DispatchCallable,
        tasks_cache: TasksCache,
    ):
        self._dispatch = dispatch
        self._tasks_cache = tasks_cache

        # Signal that stop has been requested.
        self._stop_requested = asyncio.Event()

        # We need to hold a reference to each asyncio.Task we create
        # for running our tasks otherwise the Python interpreter might
        # try and garbage collect them even if they haven't finished.
        self._dispatched_tasks: dict[bytes, asyncio.Task] = {}

    async def validate(self, tasks: list[TaskEffect]) -> None:
        """Validate that the specified tasks can be dispatched.

        There is an invariant that no other tasks will get validated
        until after 'tasks' are either stored and dispatched or an
        error is raised, otherwise we can't ensure that we'll stay
        below the limit.

        For this reason we don't validate when we're dispatching
        because we _must_ dispatch tasks that have been stored.

        It also means our limit is really more of a "soft" limit in
        that future validations will fail, but we may go above the
        limit for some time until enough tasks complete.
        """
        # Ensure that we aren't exceeding the tasks limit (to avoid a
        # possible denial of service exploit).
        if len(self._dispatched_tasks) + len(tasks) > DISPATCHED_TASKS_LIMIT:
            raise RuntimeError('Too many tasks')

        # Now call dispatch for each task but to only validate.
        await asyncio.gather(
            *[self._dispatch(task, only_validate=True) for task in tasks]
        )

    def transaction_prepare_dispatch(self, tasks: list[TaskEffect]) -> None:
        """Marks the task as prepared in a transaction and pending dispatch if
        the transaction commits."""
        for task in tasks:
            self._tasks_cache.transaction_prepared_task(task.task_id)

    def transaction_abort_dispatch(self, tasks: list[TaskEffect]) -> None:
        """Marks the task as aborted in a transaction and thus no pending
        dispatch should be expected."""
        for task in tasks:
            self._tasks_cache.transaction_aborted_task(task.task_id)

    def dispatch(self, tasks: list[TaskEffect]) -> None:
        """Creates an async dispatch and retry loop for each of the specified
        tasks."""

        # If stop has been requested we should not dispatch any new tasks.
        if self._stop_requested.is_set():
            raise ValueError('Stop requested')

        async def dispatch_retry_loop(
            task: TaskEffect,
            response_future: asyncio.Future[bytes],
        ):
            try:
                # Sleep until this task is scheduled!
                #
                # TODO(benh): improve the scheduling so that all tasks are
                # not concurrently sleeping to keep resources low.
                if task.schedule is not None:
                    seconds = (task.schedule - datetime.now()).total_seconds()
                    if seconds > 0:
                        await asyncio.sleep(seconds)

                # TODO(benh): let tasks configure their retry/backoff values.
                backoff = Backoff()

                # NOTE: The convergence criteria here is that the task either
                # successfully completes or is cancelled. A cancelled task must
                # propagate the `asyncio.exceptions.CancelledError` as is
                # standard python practice. A task that fails to complete or
                # cancel will continue to retry.
                while True:
                    try:
                        response = await self._dispatch(task)
                        any_response = any_pb2.Any()
                        any_response.Pack(response)
                        response_future.set_result(
                            any_response.SerializeToString()
                        )
                        break
                    except asyncio.exceptions.CancelledError:
                        # Allow task cancellation to be propagated. Exception
                        # handling is done on the outer scope.
                        raise
                    except BaseException as exception:
                        logger.warning(
                            f'task with UUID {str(UUID(bytes=task.task_id.task_uuid))} failed\n'
                            + ''.join(traceback.format_exception(exception))
                        )

                        await backoff()

            except asyncio.exceptions.CancelledError:
                # Re-raise to allow any upstream code to clean up.
                raise

        for task in tasks:
            # To provide idempotence, in the event that this task has
            # already been dispatched we simply ignore it.
            if task.task_id.task_uuid in self._dispatched_tasks:
                continue

            # Add task to the TasksCache _before_ we return to the
            # caller so that if they try and wait on it it will be
            # known about.
            response_future: asyncio.Future[
                bytes] = self._tasks_cache.put_pending_task(task.task_id)

            asyncio_task = asyncio.create_task(
                dispatch_retry_loop(task, response_future)
            )

            self._dispatched_tasks[task.task_id.task_uuid] = asyncio_task

            # It's possible that the task will never even start
            # because we'll call `cancel()` on it immediately. In that
            # case, it won't be able to remove itself from
            # `self._dispatched_tasks` so we need to do it via
            # `add_done_callback()`.
            def done(_):
                del self._dispatched_tasks[task.task_id.task_uuid]

            asyncio_task.add_done_callback(done)

    async def stop(self) -> None:
        """Stop dispatching Resemble tasks, and cancel any outstanding
        `asyncio.Task`s that represent an attempt to execute those Resemble
        Tasks, so those may be safely re-dispatched again elsewhere later.
        """

        # Signal that stop has been requested to avoid dispatching new tasks.
        self._stop_requested.set()

        # Cancel existing `asyncio.Tasks`.
        # NOTE: we make a copy of the values to dodge errors arising from the
        # dictionary changing size during iteration. Python does not like when
        # that happens.
        for task in list(self._dispatched_tasks.values()):
            task.cancel()

        while len(self._dispatched_tasks) > 0:
            # Wait for all dispatched tasks to finish. If the tasks are taking
            # too long, we will log a warning to the user.

            # NOTE: In contrast to `asyncio.wait_for`, `asyncio.wait` does not
            # raise `TimeoutError` if the timeout is reached and does not
            # `cancel` the `asyncio.Tasks` (again) on timeout.
            await asyncio.wait(
                self._dispatched_tasks.values(),
                timeout=5,
            )

            # As tasks complete, they should be removed from
            # `_dispatched_tasks`.
            if len(self._dispatched_tasks) == 0:
                break

            # If there are still tasks left, log a warning to the user.
            logger.warning(
                'We are still waiting for cancelled tasks to finish, are you '
                'possibly catching and forgetting to propagate a CancelledError?'
            )

            for (uuid, task) in self._dispatched_tasks.items():
                logger.warning(
                    f'Waiting for task with UUID {str(UUID(bytes=uuid))}'
                )
