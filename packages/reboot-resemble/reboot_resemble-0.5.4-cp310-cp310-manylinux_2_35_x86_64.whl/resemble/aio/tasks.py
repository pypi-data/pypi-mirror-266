from __future__ import annotations

import uuid
from datetime import datetime
from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp
from resemble.aio.types import ActorId, ServiceName
from resemble.v1alpha1 import sidecar_pb2, tasks_pb2
from typing import Optional


class TaskEffect:
    """An effect which represents running an asynchronous task. If this
    effect is successfully persisted then the task will be dispatched.

    NOTE: this is a user-facing interface while sidecar_pb2.Task is
    (currently) only used internally.
    """

    def __init__(
        self,
        *,
        service_name: ServiceName,
        actor_id: ActorId,
        method_name: str,
        request: Message,
        task_uuid: Optional[bytes] = None,
        schedule: Optional[datetime] = None,
    ):
        self.method_name = method_name
        self.request = request
        self.task_id = tasks_pb2.TaskId(
            service=service_name,
            actor_id=actor_id,
            task_uuid=task_uuid or uuid.uuid4().bytes,
        )
        self.schedule = schedule

    @classmethod
    def from_sidecar_task(
        cls, task: sidecar_pb2.Task, request_type: type[Message]
    ) -> TaskEffect:
        request = request_type()
        request.ParseFromString(task.request)
        return cls(
            service_name=task.task_id.service,
            actor_id=task.task_id.actor_id,
            method_name=task.method,
            request=request,
            task_uuid=task.task_id.task_uuid,
            schedule=task.timestamp.ToDatetime()
            if task.HasField('timestamp') else None,
        )

    def to_sidecar_task(self) -> sidecar_pb2.Task:
        timestamp: Optional[Timestamp] = None

        if self.schedule is not None:
            timestamp = Timestamp()
            timestamp.FromDatetime(self.schedule)

        return sidecar_pb2.Task(
            task_id=self.task_id,
            method=self.method_name,
            status=sidecar_pb2.Task.Status.PENDING,
            request=self.request.SerializeToString(),
            timestamp=timestamp,
        )
