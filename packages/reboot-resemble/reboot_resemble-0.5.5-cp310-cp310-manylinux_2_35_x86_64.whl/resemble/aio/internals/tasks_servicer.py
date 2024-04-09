import grpc
from google.protobuf import any_pb2
from resemble.aio.internals.tasks_cache import TasksCache
from resemble.aio.state_managers import StateManager
from resemble.consensus.sidecar import NonexistentTaskId
from resemble.v1alpha1 import tasks_pb2, tasks_pb2_grpc
from typing import Optional


class TasksServicer(tasks_pb2_grpc.TasksServicer):

    def __init__(self, state_manager: StateManager, cache: TasksCache):
        self._cache = cache
        self._state_manager = state_manager

    def add_to_server(self, server: grpc.aio.Server) -> None:
        tasks_pb2_grpc.add_TasksServicer_to_server(self, server)

    async def Wait(
        self,
        request: tasks_pb2.WaitRequest,
        grpc_context: grpc.aio.ServicerContext,
    ) -> tasks_pb2.WaitResponse:
        """Implementation of Tasks.Wait()."""
        cached_response = await self._cache.get(request.task_id)

        if cached_response is not None:
            any_response = any_pb2.Any()
            any_response.ParseFromString(cached_response)
            return tasks_pb2.WaitResponse(response=any_response)

        # Task is not cached; try and load it via the state manager.
        try:
            response: Optional[bytes] = (
                await self._state_manager.load_task_response(request.task_id)
            )
        except NonexistentTaskId:
            await grpc_context.abort(code=grpc.StatusCode.NOT_FOUND)
        else:
            # Invariant: 'response' must not be 'None'.
            #
            # Explanation: For an unknown task_id,
            # load_task_response() will raise, so to get here, task_id
            # must belong to a valid, but evicted, task. We only evict
            # tasks from our cache if they have completed, and
            # completed tasks are required to have a response stored
            # (although that response may itself be empty).
            assert response is not None

            # Cache the task response for temporal locality.
            self._cache.put_with_response(request.task_id, response)

            any_response = any_pb2.Any()
            any_response.ParseFromString(response)

            return tasks_pb2.WaitResponse(response=any_response)

    async def ListPendingTasks(
        self, _request: tasks_pb2.ListPendingTasksRequest,
        grpc_context: grpc.aio.ServicerContext
    ) -> tasks_pb2.ListPendingTasksResponse:
        """Implementation of Tasks.ListPendingTasks()."""
        return tasks_pb2.ListPendingTasksResponse(
            task_ids=self._cache.get_pending_tasks()
        )
