import grpc
from grpc_interceptor.server import AsyncServerInterceptor
from resemble.aio.internals.channel_manager import _ChannelManager
from resemble.aio.internals.contextvars import use_application_id
from resemble.aio.types import ApplicationId
from resemble.aio.workflows import Workflow
from typing import Any, Callable, Iterable, Mapping, Optional


class LegacyGrpcContext(grpc.aio.ServicerContext):
    """A subclass that Resemble will automatically substitute for
    grpc.aio.ServicerContext when forwarding traffic to RPCs in legacy gRPC
    servicers.

    Such servicers can then use this context to get a Workflow instance and send
    requests to other services in the Resemble system.
    """

    def __init__(
        self,
        grpc_context: grpc.aio.ServicerContext,
        channel_manager: _ChannelManager,
    ):
        self._grpc_context = grpc_context
        self._channel_manager = channel_manager

    def workflow(self, name: str) -> Workflow:
        return Workflow(name=name, channel_manager=self._channel_manager)

    # Implement all the grpc.aio.ServicerContext interface methods by passing
    # through to self._grpc_context.
    async def read(self):
        return await self._grpc_context.read()

    async def write(self, message) -> None:
        await self._grpc_context.write(message)

    async def send_initial_metadata(self, initial_metadata) -> None:
        await self._grpc_context.send_initial_metadata(initial_metadata)

    async def abort(
        self,
        code: grpc.StatusCode,
        details: str = "",
        trailing_metadata=tuple(),
    ):
        return await self._grpc_context.abort(code, details, trailing_metadata)

    async def abort_with_status(self, status):
        return await self._grpc_context.abort_with_status(status)

    def set_trailing_metadata(self, trailing_metadata) -> None:
        self._grpc_context.set_trailing_metadata(trailing_metadata)

    def invocation_metadata(self):
        return self._grpc_context.invocation_metadata()

    def set_code(self, code: grpc.StatusCode) -> None:
        self._grpc_context.set_code(code)

    def set_details(self, details: str) -> None:
        self._grpc_context.set_details(details)

    def set_compression(self, compression: grpc.Compression) -> None:
        self._grpc_context.set_compression(compression)

    def disable_next_message_compression(self) -> None:
        self._grpc_context.disable_next_message_compression()

    def peer(self) -> str:
        return self._grpc_context.peer()

    def peer_identities(self) -> Optional[Iterable[bytes]]:
        return self._grpc_context.peer_identities()

    def peer_identity_key(self) -> Optional[str]:
        return self._grpc_context.peer_identity_key()

    def auth_context(self) -> Mapping[str, Iterable[bytes]]:
        return self._grpc_context.auth_context()

    def time_remaining(self) -> float:
        return self._grpc_context.time_remaining()

    def trailing_metadata(self):
        return self._grpc_context.trailing_metadata()

    def code(self):
        return self._grpc_context.code()

    def details(self):
        return self._grpc_context.details()

    def add_done_callback(self, callback) -> None:
        return self._grpc_context.add_done_callback(callback)

    def cancelled(self) -> bool:
        return self._grpc_context.cancelled()

    def done(self) -> bool:
        return self._grpc_context.done()


class ResembleContextInterceptor(AsyncServerInterceptor):

    def __init__(self, channel_manager: _ChannelManager):
        self._channel_manager = channel_manager

    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        grpc_context: grpc.aio.ServicerContext,
        method_name: str,
    ) -> Any:
        resemble_grpc_context = LegacyGrpcContext(
            grpc_context, self._channel_manager
        )

        response_or_iterator = method(
            request_or_iterator, resemble_grpc_context
        )

        if not hasattr(response_or_iterator, "__aiter__"):
            # Unary, just await and return the response.
            return await response_or_iterator

        # Server streaming responses, delegate to an async generator helper.
        return self._yield_responses(response_or_iterator)

    async def _yield_responses(self, responses):
        async for response in responses:
            yield response


class UseApplicationIdInterceptor(AsyncServerInterceptor):
    """
    Interceptor that sets the application ID asyncio context variable
    for every gRPC call.

    TODO(benh): using asyncio context variables is expensive but we do
    it instead of just setting an environment variable because
    environment variables don't work in tests where we have more than
    one `rsm.up(...)` where we pass `in_process=True`; revisit this
    and consider taking different approaches when we know we can just
    rely on environment variables, e.g., when on Kubernetes.
    """

    def __init__(self, application_id: ApplicationId):
        self._application_id = application_id

    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        grpc_context: grpc.aio.ServicerContext,
        method_name: str,
    ) -> Any:
        with use_application_id(self._application_id):
            response_or_iterator = method(request_or_iterator, grpc_context)

            if not hasattr(response_or_iterator, "__aiter__"):
                # Unary, just await and return the response.
                return await response_or_iterator

            # Server streaming responses, delegate to an async generator helper.
            return self._yield_responses(response_or_iterator)

    async def _yield_responses(self, responses):
        with use_application_id(self._application_id):
            async for response in responses:
                yield response
