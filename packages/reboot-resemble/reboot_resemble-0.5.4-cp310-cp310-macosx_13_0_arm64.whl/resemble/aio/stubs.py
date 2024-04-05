import dataclasses
import grpc_status._async as rpc_status
import uuid
from contextlib import asynccontextmanager
from google.protobuf.message import Message
from grpc.aio import AioRpcError
from resemble.aio.aborted import Aborted
from resemble.aio.contexts import Context, Participants
from resemble.aio.headers import IDEMPOTENCY_KEY_HEADER, Headers
from resemble.aio.idempotency import IdempotencyManager
from resemble.aio.internals.channel_manager import _ChannelManager
from resemble.aio.internals.contextvars import get_application_id
from resemble.aio.types import (
    ActorId,
    ApplicationId,
    GrpcMetadata,
    ServiceName,
)
from typing import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Optional,
    TypeVar,
)

CallT = TypeVar('CallT')
ResponseT = TypeVar('ResponseT', bound=Message)


class Stub:
    """Common base class for generated resemble stubs.
    """
    # TODO: Do we add injection for channels and/or interceptors for M1?
    _channel_manager: _ChannelManager
    _headers: Headers

    _idempotency_manager: IdempotencyManager

    # Context that was used to create this stub.
    _context: Optional[Context]

    def __init__(
        self,
        *,
        channel_manager: _ChannelManager,
        idempotency_manager: IdempotencyManager,
        service_name: ServiceName,
        actor_id: ActorId,
        context: Optional[Context],
        bearer_token: Optional[str],
    ):
        self._channel_manager = channel_manager
        self._idempotency_manager = idempotency_manager
        self._context = context

        application_id: Optional[ApplicationId] = None

        transaction_id: Optional[uuid.UUID] = None
        transaction_coordinator_service: Optional[str] = None
        transaction_coordinator_actor_id: Optional[str] = None

        if context is not None:
            application_id = context.application_id

            transaction_id = context.transaction_id
            transaction_coordinator_service = context.transaction_coordinator_service
            transaction_coordinator_actor_id = context.transaction_coordinator_actor_id
        else:
            # When we're creating a `Stub` without a `Context`, e.g.,
            # via a `Workflow`, we use the application ID from the asyncio
            # context variable, if present.
            application_id = get_application_id()

        # NOTE: when running tests via `resemble.aio.tests.Resemble`
        # we won't always know our application ID.

        self._headers = Headers(
            application_id=application_id,
            service_name=service_name,
            actor_id=actor_id,
            transaction_id=transaction_id,
            transaction_coordinator_service=transaction_coordinator_service,
            transaction_coordinator_actor_id=transaction_coordinator_actor_id,
            bearer_token=bearer_token,
        )

    @asynccontextmanager
    async def _call(
        self,
        method: str,
        stub_method: Callable[...,
                              Awaitable[ResponseT] | AsyncIterable[ResponseT]],
        request_or_requests: Message | AsyncIterator[Message],
        *,
        unary: bool,
        reader: bool,
        response_type: type[ResponseT],
        aborted_type: type[Aborted],
        metadata: Optional[GrpcMetadata] = None,
        idempotency_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
    ) -> AsyncIterator[Awaitable[ResponseT] | AsyncIterable[ResponseT]]:
        """Helper for making an RPC, handling any user-defined errors, and
        doing so correctly depending on whether or not we are reactive
        or in a transaction.
        """
        if metadata is None:
            metadata = ()

        # TODO(benh): maybe just overwrite the idempotency key instead
        # of checking for its existence?
        if any(t[0] == IDEMPOTENCY_KEY_HEADER for t in metadata):
            raise ValueError(
                f"Do not set '{IDEMPOTENCY_KEY_HEADER}' metadata yourself"
            )

        if idempotency_key is not None:
            metadata += ((IDEMPOTENCY_KEY_HEADER, idempotency_key),)

        headers = self._headers

        if bearer_token is not None:
            headers = dataclasses.replace(
                headers,
                bearer_token=bearer_token,
            )

        metadata += headers.to_grpc_metadata()

        call: Awaitable[ResponseT] | AsyncIterable[ResponseT]
        try:
            # Check if we should execute this call reactively.
            #
            # Reactive calls are only supported for unary readers, i.e.,
            # we only have a single request, no idempotency key, and we
            # won't be in a transaction.
            if (
                self._context is not None and
                self._context.react is not None and unary and reader
            ):
                assert isinstance(request_or_requests, Message)
                assert idempotency_key is None
                assert self._context.transaction_id is None

                call, response = await self._context.react.call(
                    service=self._headers.service_name,
                    actor_id=self._headers.actor_id,
                    method=method,
                    request=request_or_requests,
                    response_type=response_type,
                    metadata=metadata,
                )

                yield response
            elif self._context is not None and self._context.transaction_id is not None:
                async with self._call_transactionally(
                    stub_method,
                    request_or_requests,
                    metadata=metadata,
                ) as call:
                    yield call
            else:
                call = stub_method(request_or_requests, metadata=metadata)
                yield call
        except AioRpcError as error:
            status = (
                await rpc_status.from_call(call)
            ) if call is not None else None

            if status is not None:
                raise aborted_type.from_status(status) from None

            raise aborted_type.from_grpc_aio_rpc_error(error) from None

    @asynccontextmanager
    async def _call_transactionally(
        self,
        stub_method: Callable[..., CallT],
        request_or_requests: Message | AsyncIterator[Message],
        *,
        metadata: GrpcMetadata,
    ) -> AsyncIterator[CallT]:
        """Helper for making an unreactive RPC and properly tracking it if it
        is part of a transaction.
        """
        assert self._context is not None
        assert self._context.transaction_id is not None

        self._context.outstanding_rpcs += 1

        try:
            call = stub_method(request_or_requests, metadata=metadata)
            yield call
            participants = Participants.from_grpc_metadata(
                # TODO: https://github.com/reboot-dev/respect/issues/2420
                await call.trailing_metadata()  # type: ignore[attr-defined]
            )
            self._context.participants.union(participants)
        except BaseException:
            # TODO(benh): considering stringifying the exception to
            # include in the error we raise when doing the prepare
            # stage of two phase commit.
            self._context.transaction_must_abort = True

            raise
        finally:
            self._context.outstanding_rpcs -= 1
