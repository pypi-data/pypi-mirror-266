import asyncio
from collections import OrderedDict
from resemble.v1alpha1 import tasks_pb2
from typing import Iterable, Optional

# Target capacity of the tasks responses cache. This is just a target
# because we want to keep all entries for tasks that are still pending
# so that any requests to wait on those tasks will not raise. While
# this means that we may have more entries in the cache than the
# target, the total number of pending tasks will never exceed
# 'tasks_dispatcher.DISPATCHED_TASKS_LIMIT', thus providing an upper
# bound on the size of the cache.
TASKS_RESPONSES_CACHE_TARGET_CAPACITY = 256


class TasksCache:

    def __init__(self):
        # Cache from task UUIDs to a future on the serialized bytes of
        # the response.
        self._cache: OrderedDict[bytes, asyncio.Future[bytes]] = OrderedDict()

        # We may return to a caller _after_ a transaction has been
        # prepared by the coordinator (i.e., the coordinator has
        # persisted that all participants have prepared) but _before_
        # the transaction has committed. Because of this we might not
        # yet have dispatched the tasks, i.e., called
        # `put_pending_task(...)`, and thus we will think a task is
        # not in the cache.
        #
        # We solve this by also holding on to any tasks that have been
        # prepared in a transaction.
        self._transaction_prepared_tasks: dict[
            bytes,
            asyncio.Future[None],
        ] = {}

        # Map of pending task UUIDs to TaskId protos, for testing and
        # observability. We store as a map since TaskIds are not themselves
        # hashable.
        self._pending_task_ids: dict[bytes, tasks_pb2.TaskId] = {}

    def transaction_prepared_task(
        self,
        task_id: tasks_pb2.TaskId,
    ) -> None:
        """Adds task as transaction prepared."""
        uuid = task_id.task_uuid
        self._transaction_prepared_tasks[uuid] = asyncio.Future()

    def transaction_aborted_task(
        self,
        task_id: tasks_pb2.TaskId,
    ) -> None:
        """Removes task as transaction prepared, or does nothing if it had not
        previously been added as transaction prepared.
        """
        uuid = task_id.task_uuid
        if uuid in self._transaction_prepared_tasks:
            self._transaction_prepared_tasks[uuid].set_exception(
                RuntimeError("Transaction aborted")
            )
            del self._transaction_prepared_tasks[uuid]

    def put_pending_task(
        self,
        task_id: tasks_pb2.TaskId,
    ) -> asyncio.Future[bytes]:
        """Adds a cache entry for the pending task so that any subsequent
        requests to wait on the task do not raise due to the task not
        having completed yet.

        Returns a future that the caller can set with the response
        bytes to indicate the completion of the task.
        """
        uuid = task_id.task_uuid

        self._pending_task_ids[uuid] = task_id

        future: asyncio.Future[bytes] = asyncio.Future()
        self._cache[uuid] = future

        future.add_done_callback(lambda _: self._pending_task_ids.pop(uuid))

        self._cache.move_to_end(uuid)
        self._trim_cache()

        # Check if the task had been added as part of a transaction,
        # and if so, notify any waiters that the transaction has
        # committed and they can start waiting for the task.
        #
        # NOTE: there is an invariant here that after calling
        # `set_result()` on the future the task will be in the cache
        # and thus we do this after adding it to the cache above.
        if uuid in self._transaction_prepared_tasks:
            self._transaction_prepared_tasks[uuid].set_result(None)
            del self._transaction_prepared_tasks[uuid]

        return future

    def get_pending_tasks(self) -> Iterable[tasks_pb2.TaskId]:
        """Get the TaskIds of all pending tasks in the cache."""
        return self._pending_task_ids.values()

    async def get(self, task_id: tasks_pb2.TaskId) -> Optional[bytes]:
        """Get the cached response for a particular task, awaiting if necessary.
        Returns None if the given task is not cached."""
        uuid = task_id.task_uuid

        # Check if the task has been prepared as part of a transaction
        # and we are still waiting on the dispatch. If this is the
        # case, the transaction must have committed because that's the
        # only way we'd expose the task ID, we're just racing with the
        # task getting dispatched.
        if uuid in self._transaction_prepared_tasks:
            await self._transaction_prepared_tasks[uuid]

        if uuid not in self._cache:
            return None

        response_future: asyncio.Future[bytes] = self._cache[uuid]
        self._cache.move_to_end(uuid)
        self._trim_cache()
        return await response_future

    def put_with_response(
        self, task_id: tasks_pb2.TaskId, response: bytes
    ) -> None:
        """Cache the specified response for the task."""
        uuid = task_id.task_uuid
        if uuid not in self._cache:
            # NOTE: we always try and add to the cache, even if we're
            # at capacity, because when we call '_trim_cache()' it's
            # possible that there is a lesser recently used entry that
            # will get evicted instead of us. It's also possible that
            # the cache is full of pending entries, in which case we
            # will evict this entry, but for now we'll just let
            # '_trim_cache()' do its thing rather than optimize that
            # case here.
            future: asyncio.Future[bytes] = asyncio.Future()
            future.set_result(response)
            self._cache[uuid] = future

        self._cache.move_to_end(uuid)
        self._trim_cache()

    def _trim_cache(self):
        """Try to remove entries in the cache in excess of the capacity by
        removing those that are no longer pending.

        We want to keep pending entries in the cache so that any
        requests to wait will not raise.
        """
        uuids_to_remove: list[bytes] = []

        # Default iteration order of a OrderedDict is from the least
        # to most recently inserted (used).
        for uuid, future in self._cache.items():
            entries = len(self._cache) - len(uuids_to_remove)
            if entries <= TASKS_RESPONSES_CACHE_TARGET_CAPACITY:
                break
            if future.done():
                uuids_to_remove.append(uuid)

        for uuid in uuids_to_remove:
            _ = self._cache.pop(uuid)
