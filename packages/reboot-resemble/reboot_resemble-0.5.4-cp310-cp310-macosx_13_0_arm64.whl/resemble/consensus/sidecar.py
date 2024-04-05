import asyncio
import grpc
import uuid
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from resemble.aio.contexts import Participants
from resemble.settings import MAX_SIDECAR_GRPC_MESSAGE_LENGTH_BYTES
from resemble.v1alpha1 import sidecar_pb2, sidecar_pb2_grpc, tasks_pb2
# TODO(benh): move this into a top-level 'grpc' module to be shared by
# both 'respect' and 'resemble'.
from respect.grpc.options import make_retry_channel_options
from typing import Optional


class NonexistentTaskId(Exception):
    pass


class SidecarClient:
    """Helper class for interacting with the resemble sidecar."""

    def __init__(self, target: str):
        self._target = target
        self._stub: Optional[sidecar_pb2_grpc.SidecarStub] = None

    async def load_actor_state(
        self,
        service: str,
        actor_id: str,
    ) -> Optional[bytes]:
        """Attempt to load state from sidecar. Return None if state
         has not (yet) been stored.
        """
        stub = await self._get_sidecar_stub()
        response: sidecar_pb2.LoadResponse = await stub.Load(
            sidecar_pb2.LoadRequest(
                actors=[sidecar_pb2.Actor(service=service, actor_id=actor_id)]
            )
        )
        if len(response.actors) > 1:
            raise RuntimeError(
                f'Expected one actor in LoadResponse; got {len(response.actors)}'
            )

        if len(response.actors) == 0:
            return None

        # Invariant: If an actor is filled in a LoadResponse, its state field is
        # also filled (although said state may itself be empty).
        assert response.actors[0].HasField('state')
        return response.actors[0].state

    async def load_task_response(
        self,
        task_id: tasks_pb2.TaskId,
    ) -> Optional[bytes]:
        """Attempt to load task response from sidecar. Return None if task
         has no response stored yet. If the task doesn't exist yet, throw an
         error.
        """
        stub = await self._get_sidecar_stub()
        response: sidecar_pb2.LoadResponse = await stub.Load(
            sidecar_pb2.LoadRequest(task_ids=[task_id])
        )
        if len(response.tasks) == 0:
            raise NonexistentTaskId()

        if len(response.tasks) > 1:
            raise RuntimeError(
                f'Expected one task in LoadResponse; got {len(response.tasks)}'
            )

        if response.tasks[0].status == sidecar_pb2.Task.Status.COMPLETED:
            # Invariant: once a Task's status is COMPLETED, the task response
            # field is filled (although the response itself may be empty).
            assert response.tasks[0].HasField('response')
            return response.tasks[0].response.SerializeToString()
        else:
            return None

    async def store(
        self,
        actor_upserts: list[sidecar_pb2.Actor],
        task_upserts: list[sidecar_pb2.Task],
        transaction: Optional[sidecar_pb2.Transaction] = None,
        idempotent_mutation: Optional[sidecar_pb2.IdempotentMutation] = None,
        file_descriptor_set: Optional[FileDescriptorSet] = None,
    ) -> None:
        """Store actor state and task upserts after method completion."""
        stub = await self._get_sidecar_stub()

        request = sidecar_pb2.StoreRequest(
            actor_upserts=actor_upserts,
            task_upserts=task_upserts,
            transaction=transaction,
            idempotent_mutation=idempotent_mutation,
            file_descriptor_set=file_descriptor_set,
        )

        await stub.Store(request)

    async def transaction_coordinator_prepared(
        self,
        transaction_id: uuid.UUID,
        participants: Participants,
    ) -> None:
        """Called by a transaction coordinator after it has successfully
        prepared a transaction, i.e., completed the first phase of two
        phase commit. After this RPC returns we should always be able
        to tell all the transaction participants that the transaction
        has committed.
        """
        stub = await self._get_sidecar_stub()

        await stub.TransactionCoordinatorPrepared(
            sidecar_pb2.TransactionCoordinatorPreparedRequest(
                transaction_id=transaction_id.bytes,
                participants=participants.to_sidecar(),
            )
        )

    async def transaction_participant_prepare(
        self, service: str, actor_id: str
    ) -> None:
        """Called by a transaction participant when they are
        prepared. Guarantees that the preparedness of this participant
        is persisted when the RPC returns, meaning that until
        'TransactionParticipantCommit()' or '...Abort()' is called,
        any call to 'Recover()' is guaranteed to return this
        transaction's information.
        """
        stub = await self._get_sidecar_stub()

        await stub.TransactionParticipantPrepare(
            sidecar_pb2.TransactionParticipantPrepareRequest(
                service=service, actor_id=actor_id
            )
        )

    async def transaction_participant_commit(
        self, service: str, actor_id: str
    ) -> None:
        """Called by a transaction participant to commit its given
        transaction. The transaction must previously have been
        prepared via 'TransactionParticipantPrepare()'. The
        transaction is guaranteed to be persisted as committed when
        the RPC returns.
        """
        stub = await self._get_sidecar_stub()

        await stub.TransactionParticipantCommit(
            sidecar_pb2.TransactionParticipantCommitRequest(
                service=service, actor_id=actor_id
            )
        )

    async def transaction_participant_abort(
        self, service: str, actor_id: str
    ) -> None:
        """Called by a transaction participant to abort its given
        transaction. The transaction MAY or MAY NOT have been prepared
        via 'TransactionParticipantPrepare()'. The transaction is
        guaranteed to be persisted as aborted when the RPC returns.
        """
        stub = await self._get_sidecar_stub()

        await stub.TransactionParticipantAbort(
            sidecar_pb2.TransactionParticipantAbortRequest(
                service=service, actor_id=actor_id
            )
        )

    async def recover(self) -> sidecar_pb2.RecoverResponse:
        """Attempt to recover server state after a potential restart."""
        stub = await self._get_sidecar_stub()
        return await stub.Recover(sidecar_pb2.RecoverRequest())

    @classmethod
    async def _make_sidecar_channel(cls, target: str) -> grpc.aio.Channel:
        """Create a gRPC channel with options specific for the sidecar."""
        channel = grpc.aio.insecure_channel(
            target,
            options=make_retry_channel_options(
                max_send_message_length=MAX_SIDECAR_GRPC_MESSAGE_LENGTH_BYTES,
                max_receive_message_length=
                MAX_SIDECAR_GRPC_MESSAGE_LENGTH_BYTES,
            )
        )

        # See 'respect/clients/aio/object_store_client.py' for a
        # longer explanation of why we wait for 'channel_ready()'
        # here.
        await asyncio.wait_for(channel.channel_ready(), timeout=45)
        return channel

    async def _get_sidecar_stub(self) -> sidecar_pb2_grpc.SidecarStub:
        if self._stub is None:
            channel = await SidecarClient._make_sidecar_channel(self._target)
            self._stub = sidecar_pb2_grpc.SidecarStub(channel)
        return self._stub
