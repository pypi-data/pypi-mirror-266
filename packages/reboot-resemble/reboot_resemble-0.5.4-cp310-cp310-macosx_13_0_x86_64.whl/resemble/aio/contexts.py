from __future__ import annotations

import asyncio
import dataclasses
import grpc.aio
import json
import sys
import traceback
import uuid
from abc import ABC
from backoff import Backoff
from collections import defaultdict
from enum import Enum
from google.protobuf.message import Message
from resemble.aio.auth import Auth
from resemble.aio.headers import TRANSACTION_PARTICIPANTS_HEADER, Headers
from resemble.aio.idempotency import IdempotencyManager
from resemble.aio.internals.channel_manager import (
    LegacyGrpcChannel,
    _ChannelManager,
)
from resemble.aio.internals.contextvars import Servicing, _actor_id, _servicing
from resemble.aio.types import (
    ActorId,
    ApplicationId,
    GrpcMetadata,
    ServiceName,
)
from resemble.v1alpha1 import react_pb2, react_pb2_grpc, sidecar_pb2
from typing import Generic, Iterable, Iterator, Optional, Tuple, TypeVar

ContextT = TypeVar('ContextT', bound='Context')
ResponseT = TypeVar('ResponseT', bound=Message)


def is_grpc_retryable_exception(exception: BaseException):
    """Helper that returns if this exception is a gRPC "retryable" error
       (e.g., network disconnect)."""
    # TODO(benh): determine what other codes, if any, are retryable.
    return (
        isinstance(exception, grpc.aio.AioRpcError) and
        exception.code == grpc.StatusCode.UNAVAILABLE
    )


class Participants:
    _participants: defaultdict[ServiceName, set[ActorId]]

    @classmethod
    def from_sidecar(cls, participants: sidecar_pb2.Participants):
        """Constructs an instance from the sidecar protobuf representation."""
        result = cls()
        for (service, actor_ids) in participants.participants.items():
            result.update(service, actor_ids.actor_ids)
        return result

    def to_sidecar(self) -> sidecar_pb2.Participants:
        """Helper to construct the sidecar protobuf representation."""
        return sidecar_pb2.Participants(
            participants={
                service:
                    sidecar_pb2.Participants.ActorIds(
                        actor_ids=list(actor_ids)
                    ) for (service, actor_ids) in self._participants.items()
            },
        )

    def __init__(self):
        self._participants = defaultdict(set)

    def __iter__(self) -> Iterator[Tuple[ServiceName, ActorId]]:
        """Returns an iterator of (service, actor_id) tuples for each
        participant."""
        for service, actor_ids in self._participants.items():
            for actor_id in actor_ids:
                yield (service, actor_id)

    def add(self, service_name: ServiceName, actor_id: ActorId):
        self._participants[service_name].add(actor_id)

    def update(self, service_name: ServiceName, actor_ids: Iterable[ActorId]):
        self._participants[service_name].update(actor_ids)

    def union(self, participants: 'Participants'):
        for (service_name, actor_ids) in participants._participants.items():
            self._participants[service_name].update(actor_ids)

    def to_grpc_metadata(self) -> GrpcMetadata:
        """Helper to encode transaction participants into gRPC metadata.
        """
        return (
            (
                TRANSACTION_PARTICIPANTS_HEADER,
                json.dumps(
                    # Need to convert 'set' into a 'list' for JSON
                    # stringification.
                    {
                        service_name: list(actor_ids)
                        for (service_name,
                             actor_ids) in self._participants.items()
                    }
                )
            ),
        )

    @classmethod
    def from_grpc_metadata(cls, metadata: GrpcMetadata) -> 'Participants':
        """Helper to decode transaction participants from gRPC metadata.
        """
        for (key, value) in metadata:
            if key == TRANSACTION_PARTICIPANTS_HEADER:
                participants = cls()
                for (service_name, actor_ids) in json.loads(value).items():
                    participants.update(service_name, actor_ids)

                return participants

        return cls()


class React:
    """Encapsulates machinery necessary for contexts that are "reactive",
    aka, those that are initiated from calls to `React.Query` and who
    then transform subsequent reader calls into `React.Query` calls
    themselves (for full transitive reactivity).
    """

    class Querier(Generic[ResponseT]):
        """Performs the `React.Query` RPCs.

        Maintains an `asyncio.Task` for every unique request that is
        used (uniqueness is determined via serializing the request).

        Expects a call to `cancel_unused()` to cancel the
        `asyncio.Task`s that are no longer necessary.
        """

        # Service, actor, method we are invoking.
        _service: ServiceName
        _actor_id: ActorId
        _method: str

        # Type of the response we are receiving.
        _response_type: type[ResponseT]

        # Event which indicates that new data has been received and we
        # should re-invoke methods.
        _event: asyncio.Event

        _channel_manager: _ChannelManager

        # Tasks that are calling `React.Query`, keyed by the
        # serialized request.
        _tasks: dict[bytes, asyncio.Task]

        # The gRPC call to `React.Query` that each of our
        # `asyncio.Task`s are making.
        _calls: dict[asyncio.Task, grpc.aio.Call]

        # The latest response or error received from calling
        # `React.Query`, set by our `asyncio.Task`s.
        _responses: dict[asyncio.Task, asyncio.Future[ResponseT]]

        # An event indicating that a response has been used and thus
        # the next response can be retrieved.
        _used_response: dict[asyncio.Task, asyncio.Event]

        # The subset of `_tasks` that's been used since the last call
        # to `cancel_*()`.  Any tasks not in this `set` are considered
        # "unused" for the purposes of `cancel_unused()`.
        _used_tasks: set[asyncio.Task]

        def __init__(
            self,
            *,
            service: ServiceName,
            actor_id: ActorId,
            method: str,
            response_type: type[ResponseT],
            event: asyncio.Event,
            channel_manager: _ChannelManager,
        ):
            self._service = service
            self._actor_id = actor_id
            self._method = method
            self._response_type = response_type
            self._event = event
            self._channel_manager = channel_manager
            self._tasks = dict()
            self._calls = dict()
            self._responses = dict()
            self._used_response = dict()
            self._used_tasks = set()

        async def call(
            self,
            request: Message,
            *,
            metadata: GrpcMetadata,
        ) -> tuple[grpc.aio.Call, asyncio.Future[ResponseT]]:
            serialized_request = request.SerializeToString(deterministic=True)

            task: Optional[asyncio.Task] = self._tasks.get(serialized_request)

            if task is not None:
                self._used_tasks.add(task)

                self._used_response[task].set()

                assert task in self._calls
                assert task in self._responses

                return (self._calls[task], self._responses[task])

            # Need to track whether or not we have received
            # the first response because we don't want to
            # cause an unnecessary reaction (i.e.,
            # re-execution of the user's code) for the first
            # response.
            have_first_response = asyncio.Event()

            async def query():
                task: Optional[asyncio.Task] = asyncio.current_task()

                assert task is not None

                # In the event we receive an error from the call we
                # want to try again because it's possible that we'll
                # get a response if some other state changes, but
                # rather than continuously bombarding the server with
                # requests we exponentially backoff before retrying.
                #
                # TODO(benh): introduce a mechanism where we can
                # actually wait until a new response would be
                # produced, e.g., because we track the state
                # version/clock and only retry calls when the state
                # changes.
                backoff = Backoff(max_backoff_seconds=5)

                while True:
                    channel = self._channel_manager.get_channel_from_service_name(
                        self._service, self._actor_id
                    )

                    call = react_pb2_grpc.ReactStub(channel).Query(
                        react_pb2.QueryRequest(
                            method=self._method,
                            request=serialized_request,
                        ),
                        metadata=metadata,
                    )

                    # We need an extra level of indirection to loop
                    # through the gRPC responses because empirically
                    # it appears as though we cannot cancel an
                    # `asyncio.Task` that is "blocked" in the gRPC
                    # `call` generator.
                    #
                    # By using an extra coroutine we can properly get
                    # interrupted on cancellation and then call
                    # `call.cancel()` which will cancel the underlying
                    # gRPC generator.
                    async def loop():
                        assert task is not None

                        async for query_response in call:
                            if not query_response.HasField('response'):
                                continue

                            response = self._response_type()
                            response.ParseFromString(query_response.response)

                            self._used_response[task].clear()

                            self._calls[task] = call

                            self._responses[task] = asyncio.Future()
                            self._responses[task].set_result(response)

                            if not have_first_response.is_set():
                                have_first_response.set()
                            else:
                                self._event.set()

                            await self._used_response[task].wait()

                    try:
                        await loop()
                    except asyncio.CancelledError:
                        call.cancel()
                        raise
                    except BaseException as exception:
                        if is_grpc_retryable_exception(exception):
                            continue

                        self._used_response[task].clear()

                        self._calls[task] = call

                        self._responses[task] = asyncio.Future()
                        self._responses[task].set_exception(exception)

                        if not have_first_response.is_set():
                            have_first_response.set()
                        else:
                            self._event.set()

                        await self._used_response[task].wait()

                        await backoff()

            task = asyncio.create_task(query())

            self._tasks[serialized_request] = task
            self._used_response[task] = asyncio.Event()
            self._used_tasks.add(task)

            await have_first_response.wait()

            return await self.call(request, metadata=metadata)

        async def cancel_all(self):
            # Mark all tasks as unused and then cancel unused, which
            # will be all of them!
            self._used_tasks = set()
            await self.cancel_unused()

        async def cancel_unused(self):
            tasks = dict()

            for (serialized_request, task) in self._tasks.items():
                if task in self._used_tasks:
                    tasks[serialized_request] = task
                else:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    except:
                        print(
                            'Failed to cancel task invoking `React.Query`',
                            file=sys.stderr,
                        )
                        traceback.print_exc()
                        pass

            self._tasks = tasks
            self._used_tasks = set()

    _channel_manager: _ChannelManager
    _queriers: dict[str, Querier]
    _event: asyncio.Event

    def __init__(self, channel_manager: _ChannelManager):
        self._channel_manager = channel_manager
        self._queriers = dict()
        self._event = asyncio.Event()

    @property
    def event(self) -> asyncio.Event:
        return self._event

    async def call(
        self,
        *,
        service: ServiceName,
        actor_id: ActorId,
        method: str,
        request: Message,
        response_type: type[ResponseT],
        metadata: GrpcMetadata,
    ) -> tuple[grpc.aio.Call, asyncio.Future[ResponseT]]:
        """Performs an RPC by calling `React.Query` instead."""
        # Lookup or create a `Querier` for performing this RPC and
        # then delegate the call to it.
        key = f'{service}.{method}/{actor_id}'

        querier: Optional[React.Querier[ResponseT]] = self._queriers.get(key)

        if querier is None:
            querier = React.Querier(
                service=service,
                actor_id=actor_id,
                method=method,
                response_type=response_type,
                event=self._event,
                channel_manager=self._channel_manager,
            )
            self._queriers[key] = querier

        assert querier is not None
        return await querier.call(request, metadata=metadata)

    async def cancel_unused_queries(self):
        for querier in self._queriers.values():
            await querier.cancel_unused()

    async def cancel_all_queries(self):
        for querier in self._queriers.values():
            await querier.cancel_all()


class EffectValidation(Enum):
    ENABLED = 1
    SILENT = 2
    DISABLED = 3


class EffectValidationRetry(Exception):
    """An exception type which is raised in order to abort and retry transactions
    for the purposes of effect validation."""


class Context(ABC, IdempotencyManager):
    """Common base class for all contexts.

    Contexts holds information relevant to the current call.

    Construction of a Context object is done by the servicer
    middleware. You should never need to construct a Context yourself.
    """
    _channel_manager: _ChannelManager
    _headers: Headers

    # Participants aggregated from all RPCs rooted at the method for
    # which we initially created this context.
    #
    # We use this when a method is executed within a transaction so
    # that we can pass back to the coordinator the precise set of
    # participants.
    participants: Participants

    # Number of outstanding RPCs rooted at the method for which we
    # initially created this context. Incremented whenever an RPC
    # begins, and decremented when it completes (whether successfully
    # or not).
    #
    # We use this when a method is executed within a transaction to
    # ensure that all RPCs complete so that we know we have aggregated
    # all possible participants - this count must reach 0.
    #
    # TODO(benh): consider using this for not just transactions but
    # all methods, or at least making it the default with an option to
    # opt out.
    outstanding_rpcs: int

    # Whether or not the transaction enclosing this context should
    # abort.
    transaction_must_abort: bool

    # Extra machinery for handling reactive contexts. Set when using
    # the `StateManager.reactively()` helper.
    react: Optional[React]

    # Auth specific information as provided by the `TokenVerifier`, if present.
    auth: Optional[Auth]

    # Whether or not this context is being used for a "constructor",
    # i.e., a writer or transaction of an actor that has not yet been
    # constructed.
    _constructor: bool

    def __init__(
        self,
        *,
        channel_manager: _ChannelManager,
        headers: Headers,
    ):
        # Note: this is intended as a private constructor only to be
        # called by the middleware.
        if _servicing.get() is not Servicing.INITIALIZING:
            raise RuntimeError(
                'Context should only be constructed by middleware'
            )

        # Store the actor ID as an asyncio contextvar for access via
        # APIs where we don't pass a `context` but we know one has
        # been created (or should have been created).
        _actor_id.set(headers.actor_id)

        super().__init__()

        self._channel_manager = channel_manager
        self._headers = headers

        self.participants = Participants()
        self.outstanding_rpcs = 0
        self.transaction_must_abort = False

        self.react = None

        self.auth = None

        self._constructor = False

    @property
    def channel_manager(self) -> _ChannelManager:
        """Return channel manager.
        """
        return self._channel_manager

    @property
    def application_id(self) -> ApplicationId:
        """Return application ID.
        """
        assert self._headers.application_id is not None
        return self._headers.application_id

    @property
    def service_name(self) -> ServiceName:
        """Return service name.
        """
        return self._headers.service_name

    @property
    def actor_id(self) -> ActorId:
        """Return actor id.
        """
        return self._headers.actor_id

    @property
    def transaction_id(self) -> Optional[uuid.UUID]:
        """Return transaction id.
        """
        return self._headers.transaction_id

    @property
    def transaction_coordinator_service(self) -> Optional[str]:
        """Return transaction coordinator service.
        """
        return self._headers.transaction_coordinator_service

    @property
    def transaction_coordinator_actor_id(self) -> Optional[str]:
        """Return transaction coordinator actor id.
        """
        return self._headers.transaction_coordinator_actor_id

    @property
    def idempotency_key(self) -> Optional[uuid.UUID]:
        """Return optional idempotency key.
        """
        return self._headers.idempotency_key

    @property
    def bearer_token(self) -> Optional[str]:
        """Return optional bearer token.
        """
        return self._headers.bearer_token

    @property
    def constructor(self) -> bool:
        """Return whether or not this context is being used for a method that
        is acting as a constructor.
        """
        return self._constructor

    def legacy_grpc_channel(self) -> grpc.aio.Channel:
        """Get a gRPC channel that can connect to any Resemble-hosted legacy
        gRPC service. Simply use this channel to create a Stub and call it, no
        address required."""
        return LegacyGrpcChannel(self._channel_manager)


class ReaderContext(Context):
    """Call context for a reader call."""


class WriterContext(Context):
    """Call context for a writer call."""


class TransactionContext(Context):
    """Call context for a transaction call."""

    def __init__(
        self,
        *,
        channel_manager: _ChannelManager,
        headers: Headers,
    ):
        # NOTE: we don't (yet) support nested transactions.
        self._nested = False

        assert headers.transaction_id is None
        assert headers.transaction_coordinator_service is None
        assert headers.transaction_coordinator_actor_id is None

        headers = dataclasses.replace(
            headers,
            transaction_id=uuid.uuid4(),
            # The actor servicing the request to executing a method of
            # kind transaction acts as the transaction coordinator.
            transaction_coordinator_service=headers.service_name,
            transaction_coordinator_actor_id=headers.actor_id,
        )

        super().__init__(
            channel_manager=channel_manager,
            headers=headers,
        )

    @property
    def transaction_id(self) -> uuid.UUID:
        """Return transaction id.
        """
        assert self._headers.transaction_id is not None
        return self._headers.transaction_id

    @property
    def transaction_coordinator_service(self) -> str:
        """Return transaction coordinator service.
        """
        assert self._headers.transaction_coordinator_service is not None
        return self._headers.transaction_coordinator_service

    @property
    def transaction_coordinator_actor_id(self) -> str:
        """Return transaction coordinator actor id.
        """
        assert self._headers.transaction_coordinator_actor_id is not None
        return self._headers.transaction_coordinator_actor_id

    @property
    def nested(self) -> bool:
        """Return whether or not this transaction is nested.
        """
        return self._nested
