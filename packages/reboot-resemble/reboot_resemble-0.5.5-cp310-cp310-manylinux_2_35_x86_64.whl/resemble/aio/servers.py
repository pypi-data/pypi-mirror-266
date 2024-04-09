from __future__ import annotations

import grpc
import logging
import os
import respect.logging
from google.protobuf.descriptor import FileDescriptor
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from grpc_health.v1 import health, health_pb2_grpc
from grpc_interceptor.server import AsyncServerInterceptor
from grpc_reflection.v1alpha import reflection
from resemble.aio.auth.token_verifiers import TokenVerifier
from resemble.aio.contexts import EffectValidation
from resemble.aio.interceptors import (
    ResembleContextInterceptor,
    UseApplicationIdInterceptor,
)
from resemble.aio.internals.channel_manager import _ChannelManager
from resemble.aio.internals.contextvars import use_application_id
from resemble.aio.internals.middleware import Middleware
from resemble.aio.internals.tasks_cache import TasksCache
from resemble.aio.internals.tasks_servicer import TasksServicer
from resemble.aio.react import ReactServicer
from resemble.aio.resolvers import ActorResolver, StaticResolver
from resemble.aio.servicers import (
    ConfigServicer,
    ResembleServiceable,
    Routable,
    Serviceable,
    Servicer,
)
from resemble.aio.state_managers import LocalSidecarStateManager, StateManager
from resemble.aio.types import ApplicationId, RoutableAddress, ServiceName
from resemble.aio.workflows import Workflow
from resemble.controller.settings import (
    ENVVAR_RESEMBLE_APPLICATION_ID,
    ENVVAR_RESEMBLE_CONFIG_SERVER_PORT,
    ENVVAR_RESEMBLE_MODE,
    RESEMBLE_MODE_CONFIG,
    RESEMBLE_ROUTABLE_HOSTNAME,
    RESEMBLE_SYSTEM_NAMESPACE,
    USER_CONTAINER_GRPC_PORT,
    USER_CONTAINER_WEBSOCKET_PORT,
)
from resemble.helpers import generate_proto_descriptor_set
from resemble.inspect.servicer import InspectServicer
from resemble.settings import RESEMBLE_STATE_DIRECTORY
from resemble.v1alpha1 import application_config_pb2, react_pb2
from resemble.v1alpha1.inspect import inspect_pb2
from typing import Awaitable, Callable, Optional

logger = respect.logging.get_logger(__name__)
# TODO(rjh): some mechanism where developers can configure the Resemble log
# level per-module or globally. For now, default to `WARNING`: we have warnings
# in this file that we expect users to want to see.
logger.setLevel(logging.WARNING)


class Server:
    """Server is currently an internal only abstraction. Users should use
    `Application` instead.
    """

    def __init__(
        self,
        listen_address: RoutableAddress,
        *,
        interceptors: Optional[list[AsyncServerInterceptor]] = None
    ):
        if type(self) == Server:
            # Invariant is that constructor does not get called
            # directly; otherwise `type(self)` will be a
            # `_ServiceServer` or `_ConfigServer`.
            raise ValueError(
                'Do not construct Server directly; use, e.g., Server.create_on_k8s()'
            )

        grpc_server = grpc.aio.server(interceptors=interceptors or [])

        try:
            host, port = listen_address.split(':')
        except ValueError:
            host = listen_address

        port = grpc_server.add_insecure_port(listen_address)
        # TODO: Resolve the address (if possible) to a routable address.
        # The address 0.0.0.0 means listen on all network interfaces (there
        # could be more/many/ambiguity). It would be nice to resolve it into
        # something we can use in a test (like 127.0.0.1).
        address = f'{host}:{port}'
        self._grpc_server: grpc.aio.server = grpc_server
        self._listen_address: RoutableAddress = address

    @classmethod
    def _needs_initialization(cls, state_directory: str) -> bool:
        # Invariant: the `state_directory` should exist. If it is still empty we
        # assume that initialization is necessary.
        #
        # There are some files/folders that may exist even in a
        # previously-unused state folder, because the operating system places
        # them there. We ignore these files/folders when determining whether or
        # not we need to initialize.
        IGNORE_STATE_CONTENTS = set(
            [
                # AWS EBS volumes may have a 'lost+found' directory when they are
                # first mounted.
                "lost+found"
            ]
        )
        state_contents = set(
            os.listdir(state_directory)
        ) - IGNORE_STATE_CONTENTS
        needs_initialization = len(state_contents) == 0

        logger.info(
            f"There {'is NO' if needs_initialization else 'IS'} state present, so "
            f"the application {'WILL' if needs_initialization else 'will NOT'} be "
            "initialized"
        )
        if not needs_initialization:
            logger.debug(f"State found was: {state_contents}")

        return needs_initialization

    @classmethod
    def create_on_k8s(
        cls,
        *,
        servicers: list[type[Servicer]],
        initialize: Optional[Callable[[Workflow], Awaitable[None]]] = None,
        initialize_bearer_token: Optional[str] = None,
        listen_address: RoutableAddress = '127.0.0.1:0',
        token_verifier: Optional[TokenVerifier] = None,
    ) -> Server:
        """Creates the appropriate type of `Server` for the current "mode"
        (config or serving).

        This function assumes that it executes in a Kubernetes runtime
        environment. Non-Kubernetes environments should construct a
        `_ServiceServer` directly.
        """
        # TODO(benh): assert we are on K8s if that is the invariant!!!
        # Unfortunately the test in
        # `tests/resemble/controller/config_server_test.py` uses this
        # method when _not_ run on Kubernetes so we can't. Let's clean
        # that up.
        serviceables = [
            Serviceable.from_servicer_type(servicer_type)
            for servicer_type in servicers
        ]
        # To prevent typos mixing up `servicers` and `serviceables`, delete
        # `servicers` (so that mypy can catch if we accidentally use it).
        del servicers

        # Depending on which mode we're starting in, serving or config, we
        # either instantiate a _ServiceServer for handling user requests or a
        # _ConfigServer which is used internally to configure out system.
        if os.environ.get(ENVVAR_RESEMBLE_MODE) == RESEMBLE_MODE_CONFIG:
            server_port = os.environ.get(ENVVAR_RESEMBLE_CONFIG_SERVER_PORT)
            if server_port is None:
                raise EnvironmentError(
                    f'{ENVVAR_RESEMBLE_CONFIG_SERVER_PORT} not found. Must be present '
                    f'when {ENVVAR_RESEMBLE_MODE} is `{RESEMBLE_MODE_CONFIG}`.'
                )

            listen_address = f'0.0.0.0:{server_port}'
            return _ConfigServer(
                serviceables=serviceables,
                listen_address=listen_address,
            )

        # We're not in config mode, so we'll be serving as a consensus member.

        # Set for every consensus, see `KubernetesConsensusManager` in
        # 'resemble/controller/consensus_managers.py'.
        application_id: Optional[str] = os.environ.get(
            ENVVAR_RESEMBLE_APPLICATION_ID
        )

        assert application_id is not None

        # Route all traffic to the Resemble routable hostname. We rely on Istio
        # and our EnvoyFilters to route the traffic to the appropriate
        # consensus.
        static_routable_address = (
            f'{RESEMBLE_ROUTABLE_HOSTNAME}.{RESEMBLE_SYSTEM_NAMESPACE}:'
            f'{USER_CONTAINER_GRPC_PORT}'
        )
        logger.debug(
            f'Routing all actor traffic to address: {static_routable_address}'
        )
        actor_resolver = StaticResolver(static_routable_address)

        # Since we're NOT in config mode, this server will produce state. It may
        # need to initialize that state, if this is the first time this server
        # is being started.
        needs_initialization = cls._needs_initialization(
            RESEMBLE_STATE_DIRECTORY
        )

        # TODO(rjh): use SidecarStateManager once launching sidecars as separate
        #            k8s pods instead of in-process?
        state_manager = LocalSidecarStateManager(RESEMBLE_STATE_DIRECTORY)

        # TODO: Consider pulling this file_descriptor_set info out of a
        # corresponding ApplicationConfig rather than regenerating it from
        # serviceables here.
        file_descriptor_set = generate_proto_descriptor_set(
            routables=serviceables
        )

        return _ServiceServer(
            application_id=application_id,
            serviceables=serviceables,
            listen_address=listen_address,
            websocket_port=USER_CONTAINER_WEBSOCKET_PORT,
            state_manager=state_manager,
            actor_resolver=actor_resolver,
            token_verifier=token_verifier,
            file_descriptor_set=file_descriptor_set,
            # Note: effect validation is always disabled when running on K8s.
            effect_validation=EffectValidation.DISABLED,
            initialize=initialize if needs_initialization else None,
            initialize_bearer_token=initialize_bearer_token,
        )

    async def wait(self):
        await self._grpc_server.wait_for_termination()

    def port(self) -> int:
        """Return port of gRPC server."""
        # Note: Formatting of the address string is done through the factory
        # method. There should be no case in which this is undefined or results
        # in an index or type error.
        return int(self._listen_address.split(':')[-1])

    async def start(self):
        """Start server."""
        # Note: In the future we might have pre/post start hooks here for
        # servicers.
        await self._grpc_server.start()

    async def stop(self, gracetime: Optional[float] = None):
        """Stop grpc server."""
        # Note: In the future we might have pre/post stop hooks here for
        # servicers.
        await self._grpc_server.stop(grace=gracetime)

    async def run(self):
        try:
            await self.start()
            await self.wait()
        except BaseException as e:
            logger.error('Failed to start (or wait on) server', exc_info=e)
            # Contract: it is safe to call `stop()` even when `start()` has not
            #           completed successfully and therefore some parts of our
            #           server may not have started yet. Calling `stop()` on a
            #           not-started resource should be treated as a no-op.
            await self.stop()
            raise


class _ServiceServer(Server):

    class ReactRoutable(Routable):
        """Helper "routable" that can be provided to for routing to the
        `ReactServicer` system service that we run manually."""

        def service_name(self) -> ServiceName:
            # TODO(benh): get from react_pb2.DESCRIPTOR.
            return 'resemble.v1alpha1.React'

        def file_descriptor(self) -> FileDescriptor:
            return react_pb2.DESCRIPTOR.services_by_name['React'].file

    class InspectRoutable(Routable):
        """Helper "routable" that can be provided to for routing to the
        `InspectServicer` system service that we run manually."""

        def service_name(self) -> ServiceName:
            # TODO(benh): get from inspect_pb2.DESCRIPTOR.
            return 'resemble.v1alpha1.inspect.Inspect'

        def file_descriptor(self) -> FileDescriptor:
            return inspect_pb2.DESCRIPTOR.services_by_name['Inspect'].file

    ROUTABLES: list[Routable] = [
        ReactRoutable(),
        InspectRoutable(),
    ]

    SYSTEM_SERVICE_NAMES = [r.service_name() for r in ROUTABLES]

    _websocket_port: Optional[int]

    def __init__(
        self,
        *,
        application_id: ApplicationId,
        serviceables: list[Serviceable],
        listen_address: RoutableAddress,
        websocket_port: Optional[int] = None,
        token_verifier: Optional[TokenVerifier],
        state_manager: StateManager,
        actor_resolver: ActorResolver,
        file_descriptor_set: FileDescriptorSet,
        effect_validation: EffectValidation,
        initialize: Optional[Callable[[Workflow], Awaitable[None]]],
        initialize_bearer_token: Optional[str] = None,
    ):
        # Construct our _ChannelManager first so that we can use it to construct
        # an Interceptor to pass to our superclass.
        self._channel_manager = _ChannelManager(
            actor_resolver,
            # Communication between actors does not use a secure channel,
            # since it doesn't go through the gateway, which is where SSL
            # termination happens. In production infrastructure it is assumed
            # that this intra-Resemble traffic is secured otherwise, e.g. via Istio
            # sidecars providing mTLS.
            secure=False,
        )

        self._application_id = application_id

        super().__init__(
            listen_address,
            interceptors=[
                ResembleContextInterceptor(self._channel_manager),
                UseApplicationIdInterceptor(self._application_id),
            ],
        )

        self._websocket_port = websocket_port

        self._state_manager = state_manager
        self._file_descriptor_set = file_descriptor_set

        # Keep track of our middleware so that we can use it to manually
        # dispatch recovered tasks.
        self._middleware_by_service_name: dict[ServiceName, Middleware] = {}

        # Construct shared tasks cache.
        tasks_cache = TasksCache()

        # Now start serving the serviceables.
        for serviceable in serviceables:
            if isinstance(serviceable, ResembleServiceable):
                # Resemble servicers get middleware. Requests are passed to the
                # middleware, which will pass them on to the user code.
                servicer, _ = serviceable.instantiate()
                # TODO: https://github.com/reboot-dev/respect/issues/2421
                middleware = servicer.create_middleware(  # type: ignore[attr-defined]
                    application_id=self._application_id,
                    state_manager=self._state_manager,
                    channel_manager=self._channel_manager,
                    tasks_cache=tasks_cache,
                    token_verifier=token_verifier,
                    effect_validation=effect_validation,
                )
                middleware.add_to_server(self._grpc_server)
                self._middleware_by_service_name[servicer.__service_name__
                                                ] = middleware
            else:
                # Legacy gRPC servicers don't get middleware. Requests are
                # passed to the user code directly.
                legacy_grpc_servicer, add_to_server = serviceable.instantiate()
                assert add_to_server is not None
                add_to_server(legacy_grpc_servicer, self._grpc_server)

        # Construct 'Inspect' system service for the Resemble servicers.
        #
        # Invariant: `self._middleware_by_service_name` has been fully
        # constructed at this point.
        self._inspect_servicer = InspectServicer(
            self._state_manager,
            self._middleware_by_service_name,
        )
        self._inspect_servicer.add_to_server(self._grpc_server)

        # Construct and add 'React' system service for the Resemble servicers.
        #
        # Invariant: `self._middleware_by_service_name` has been fully
        # constructed at this point.
        self._react_servicer = ReactServicer(
            self._application_id,
            self._middleware_by_service_name,
        )
        self._react_servicer.add_to_server(self._grpc_server)

        # Add the standard gRPC health checking servicer to every server. See:
        # https://grpc.io/docs/guides/health-checking/
        self._health_servicer = health.aio.HealthServicer()
        health_pb2_grpc.add_HealthServicer_to_server(
            self._health_servicer,
            self._grpc_server,
        )

        # Construct and add 'Tasks' system service.
        self._tasks_servicer = TasksServicer(self._state_manager, tasks_cache)
        self._tasks_servicer.add_to_server(self._grpc_server)

        # Add StateManager system services (i.e., to serve transaction
        # coordinators and participants).
        state_manager.add_to_server(self._grpc_server)

        # We use the reflection service to make this server more debugable. See:
        # https://github.com/grpc/grpc/blob/master/doc/python/server_reflection.md
        service_names = tuple([s.service_name() for s in serviceables])
        reflection.enable_server_reflection(service_names, self._grpc_server)

        # The initialize callback (if any) will be called after the server has
        # started.
        self._initialize = initialize
        self._initialize_bearer_token = initialize_bearer_token

    async def start(self):
        # Recover past state (if any).
        await self._state_manager.recover(
            application_id=self._application_id,
            channel_manager=self._channel_manager,
            middleware_by_service_name=self._middleware_by_service_name,
            file_descriptor_set=self._file_descriptor_set,
        )

        # Once recovery is complete, we can start serving traffic.
        await super().start()

        # And also start serving React traffic.
        self._websocket_port = await self._react_servicer.start(
            self._websocket_port
        )

        # Now that traffic has been observed to flow, we can invoke the user's
        # initialize callback.
        if self._initialize is not None:

            workflow = Workflow(
                name="initialize",
                # TODO(rjh): by passing `self._listen_address` instead
                # of `self._channel_manager` we guarantee that traffic
                # can immediately be served (the user's `initialize()`
                # does not need retries to deal with connectivity
                # issues), but as a tradeoff the user's `Workflow`
                # can't be used to contact services outside this
                # consensus. That's very surprising and unfortunate
                # for our users, and is acceptable only because the
                # planned replacement of initializers (singletons) has
                # the same semantics in a much better API that is NOT
                # so surprising.
                gateway=self._listen_address,
                # Not using a secure channel, since our `gateway` is in fact the
                # (non-SSL) port of the actual service.
                secure_channel=False,
                bearer_token=self._initialize_bearer_token,
            )

            # Need to set the application ID asyncio context
            # variable so `initialize` can make calls to other
            # servicers.
            with use_application_id(self._application_id):
                await self._initialize(workflow)

    async def stop(self, gracetime: Optional[float] = None):
        # Stop any background tasks running in the middleware.
        for middleware in self._middleware_by_service_name.values():
            await middleware.stop()

        # Stop serving React traffic.
        await self._react_servicer.stop()

        # Stop serving traffic.
        await super().stop(gracetime=gracetime)

    def websocket_port(self) -> int:
        """Return port of React websocket server."""
        if self._websocket_port is None:
            raise RuntimeError(
                'Must call `start()` before trying to get websocket port'
            )

        return self._websocket_port


class _ConfigServer(Server):

    def __init__(
        self,
        serviceables: list[Serviceable],
        listen_address: RoutableAddress,
    ):
        super().__init__(listen_address, interceptors=[])
        routables = serviceables + _ServiceServer.ROUTABLES

        proto_descriptor_set = generate_proto_descriptor_set(
            routables=routables
        )
        service_names = [r.service_name() for r in routables]
        application_config = application_config_pb2.ApplicationConfig(
            spec=application_config_pb2.ApplicationConfig.Spec(
                file_descriptor_set=proto_descriptor_set.SerializeToString(),
                service_names=service_names,
            )
        )

        ConfigServicer.add_to_server(self._grpc_server, application_config)
