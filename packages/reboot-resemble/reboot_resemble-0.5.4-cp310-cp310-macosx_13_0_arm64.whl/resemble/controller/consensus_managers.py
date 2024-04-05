import asyncio
import kubernetes_asyncio
import multiprocessing
import os
import signal
import sys
import tempfile
import threading
import traceback
from dataclasses import dataclass
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from kubernetes_utils.kubernetes_client import EnhancedKubernetesClient
from kubernetes_utils.resources.deployments import (
    DynamicVolumeMount,
    UpdateStrategy,
)
from kubernetes_utils.resources.persistent_volume_claims import AccessMode
from kubernetes_utils.resources.services import Port
from resemble.aio.auth.token_verifiers import TokenVerifier
from resemble.aio.contexts import EffectValidation
from resemble.aio.resolvers import DirectResolver
from resemble.aio.servers import _ServiceServer
from resemble.aio.servicers import Serviceable
from resemble.aio.signals import raised_signal
from resemble.aio.state_managers import LocalSidecarStateManager
from resemble.aio.types import (
    ApplicationId,
    ConsensusId,
    RoutableAddress,
    ServiceName,
)
from resemble.cli import terminal
from resemble.consensus.local_envoy import LocalEnvoy
from resemble.controller.consensuses import Consensus
from resemble.controller.envoy_filter import EnvoyFilter
from resemble.controller.envoy_filter_generator import (
    generate_transcoding_filter,
)
from resemble.controller.exceptions import InputError
from resemble.controller.settings import (
    ENVVAR_RESEMBLE_APPLICATION_ID,
    IS_RESEMBLE_CONSENSUS_LABEL_NAME,
    IS_RESEMBLE_CONSENSUS_LABEL_VALUE,
    RESEMBLE_CONSENSUS_ID_LABEL_NAME,
    RESEMBLE_STORAGE_CLASS_NAME,
    USER_CONTAINER_GRPC_PORT,
    USER_CONTAINER_WEBSOCKET_PORT,
)
from resemble.naming import get_service_account_name_for_application
from resemble.run_environments import on_kubernetes
from resemble.settings import (
    ENVVAR_RSM_DEV_EFFECT_VALIDATION,
    EVERY_LOCAL_NETWORK_ADDRESS,
    RESEMBLE_STATE_DIRECTORY,
    SIDECAR_SUFFIX,
)
from resemble.v1alpha1 import placement_planner_pb2
from typing import Awaitable, Callable, Iterable, Optional, Union


def get_deployment_name(consensus_id: ConsensusId) -> str:
    return f'{consensus_id}'


def get_service_name(consensus_id: ConsensusId) -> str:
    return f'{consensus_id}'


class ConsensusManager:

    def __init__(self):
        # We expect our callbacks to be async functions with no params.
        self.locations_change_callbacks: list[Callable[[],
                                                       Awaitable[None]]] = []
        # Dict mapping consensus name to Consensus info.
        self.current_consensuses: dict[ConsensusId, Consensus] = {}

    async def _set_consensus(
        self,
        consensus: Consensus,
    ) -> placement_planner_pb2.ConsensusAddresses:
        """Make a consensus and return a list of its addresses. If a consensus
        with the same name already exists, overwrite it with the new config (if
        the config hasn't changed, this can and should be a no-op.)"""
        raise NotImplementedError()

    async def _delete_consensus(
        self,
        consensus: Consensus,
    ) -> None:
        """Delete the given consensus from the system."""
        raise NotImplementedError()

    def on_locations_change(
        self, callback: Callable[[], Awaitable[None]]
    ) -> None:
        """Set a new callback function for any consensus location changes we
        hear about from Kubernetes."""
        self.locations_change_callbacks.append(callback)

    async def set_consensuses(
        self, consensuses: Iterable[Consensus]
    ) -> list[placement_planner_pb2.ConsensusAddresses]:
        """Take in a list of Consensuses, and return a list
        of matching ConsensusAddresses."""
        new_consensus_locations: list[placement_planner_pb2.ConsensusAddresses
                                     ] = []
        new_consensus_dict = {}
        for consensus in consensuses:
            # Add a new consensus, or update the existing consensus (if any).
            consensus_addresses = await self._set_consensus(consensus)
            new_consensus_locations.append(consensus_addresses)
            new_consensus_dict[consensus.id] = consensus

        # Go through and delete consensuses that are no longer part of the plan.
        for consensus_id, consensus in self.current_consensuses.items():
            if consensus_id not in new_consensus_dict:
                await self._delete_consensus(consensus)

        self.current_consensuses = new_consensus_dict
        return new_consensus_locations


class KubernetesConsensusManager(ConsensusManager):

    def __init__(self, k8s_client: Optional[EnhancedKubernetesClient] = None):
        super().__init__()
        self._k8s_client = k8s_client

    async def _set_consensus(
        self,
        consensus: Consensus,
    ) -> placement_planner_pb2.ConsensusAddresses:
        if self._k8s_client is None:
            # We know we're inside a cluster.
            self._k8s_client = (
                await EnhancedKubernetesClient.create_incluster_client()
            )

        assert consensus.file_descriptor_set is not None
        assert consensus.namespace is not None
        assert consensus.container_image_name is not None

        deployment_name = get_deployment_name(consensus.id)

        # Create a storage claim for the consensus. TODO: set ownership to the
        # original ApplicationDeployment object associated with this consensus.
        # (The owner object must be in the same namespace as the objects being
        # created, or the new resources won't come up.)
        # ISSUE(https://github.com/reboot-dev/respect/issues/1430): Fix
        # ownership. Owner should be the ApplicationDeployment.
        await self._k8s_client.persistent_volume_claims.create_or_update(
            namespace=consensus.namespace,
            name=deployment_name,
            storage_class_name=RESEMBLE_STORAGE_CLASS_NAME,
            # TODO(rjh): make this configurable via the ApplicationDeployment.
            storage_request="1Gi",
            # TODO(rjh): once widely supported, switch to READ_WRITE_ONCE_POD
            #            for additional assurance that we don't have multiple
            #            pods reading the same volume. As of November 2023, our
            #            version of k3d is lacking support.
            access_modes=[AccessMode.READ_WRITE_ONCE],
        )

        # TODO: set ownership to the original ApplicationDeployment object
        # associated with this consensus, NOT the controller Pod. (The owner
        # object must be in the same namespace as the objects being created, or
        # the new resources won't come up.)
        # ISSUE(https://github.com/reboot-dev/respect/issues/1430): Fix
        # ownership. Owner should be the ApplicationDeployment.
        pod_labels = {
            # Mark each pod as being part of a Resemble consensus.
            # That'll be used to target the pod for e.g. EnvoyFilter
            # distribution.
            IS_RESEMBLE_CONSENSUS_LABEL_NAME:
                IS_RESEMBLE_CONSENSUS_LABEL_VALUE,
            # Further mark it with its specific consensus name, for even
            # narrower EnvoyFilter targeting.
            RESEMBLE_CONSENSUS_ID_LABEL_NAME:
                consensus.id,
        }
        await self._k8s_client.deployments.create_or_update(
            namespace=consensus.namespace,
            deployment_name=deployment_name,
            container_image_name=consensus.container_image_name,
            replicas=1,
            exposed_ports=[
                USER_CONTAINER_GRPC_PORT,
                USER_CONTAINER_WEBSOCKET_PORT,
            ],
            pod_labels=pod_labels,
            service_account_name=get_service_account_name_for_application(
                consensus.application_id
            ),
            # Currently, Resemble applications can't be replaced in a graceful
            # rolling restart. They must be brought down first, before a
            # replacement can be brought back up. This will cause some downtime,
            # particularly since the old application doesn't terminate
            # instantly.
            update_strategy=UpdateStrategy.RECREATE,
            env=[
                # Expected when run on Kubernetes, see
                # 'resemble/aio/servers.py'.
                kubernetes_asyncio.client.V1EnvVar(
                    name=ENVVAR_RESEMBLE_APPLICATION_ID,
                    value=consensus.application_id,
                ),
                # Ensure that any Python process always produces their output
                # immediately. This is helpful for debugging purposes.
                kubernetes_asyncio.client.V1EnvVar(
                    name="PYTHONUNBUFFERED",
                    value="1",
                ),
            ],
            volumes=[
                DynamicVolumeMount(
                    persistent_volume_claim_name=deployment_name,
                    mount_path=RESEMBLE_STATE_DIRECTORY,
                )
            ]
        )

        # Instruct the consensus to transcode incoming HTTP traffic to gRPC.
        # We do this by setting up an EnvoyFilter for this specific consensus.
        assert consensus.file_descriptor_set is not None
        transcoding_filter_name = f'{deployment_name}-transcoding-filter'
        transcoding_filter: EnvoyFilter = generate_transcoding_filter(
            namespace=consensus.namespace,
            name=transcoding_filter_name,
            target_labels=pod_labels,
            services=[s for s in consensus.service_names],
            file_descriptor_set=consensus.file_descriptor_set,
        )
        await self._k8s_client.custom_objects.create_or_update(
            transcoding_filter
        )

        # TODO: set ownership to the original ApplicationDeployment object
        # associated with this consensus, NOT the controller Pod. (The owner
        # object must be in the same namespace as the objects being created, or
        # the new resources won't come up.)
        # ISSUE(https://github.com/reboot-dev/respect/issues/1430): Fix
        # ownership. Owner should be the ApplicationDeployment.
        service_name = get_service_name(consensus.id)
        await self._k8s_client.services.create_or_update(
            namespace=consensus.namespace,
            name=service_name,
            deployment_label=deployment_name,
            ports=[
                # To let this port serve gRPC traffic when there's an
                # intermediate Envoy proxy in gateway mode, this port
                # MUST be called "grpc".
                Port(port=USER_CONTAINER_GRPC_PORT, name="grpc"),
                # Port for WebSockets for browsers.
                Port(port=USER_CONTAINER_WEBSOCKET_PORT, name="websocket"),
            ],
        )

        service_address = placement_planner_pb2.ConsensusAddress(
            host=f'{service_name}.{consensus.namespace}.svc.cluster.local',
            port=USER_CONTAINER_GRPC_PORT
        )

        return placement_planner_pb2.ConsensusAddresses(
            consensus_id=consensus.id,
            namespace=consensus.namespace,
            addresses=[service_address]
        )

    async def _delete_consensus(
        self,
        consensus: Consensus,
    ) -> None:
        if self._k8s_client is None:
            # We know we're inside a cluster.
            self._k8s_client = (
                await EnhancedKubernetesClient.create_incluster_client()
            )

        assert consensus.namespace is not None

        await self._k8s_client.services.delete(
            namespace=consensus.namespace,
            name=get_service_name(consensus.id),
        )
        deployment_name = get_deployment_name(consensus.id)
        await self._k8s_client.deployments.delete(
            namespace=consensus.namespace, name=deployment_name
        )
        await self._k8s_client.persistent_volume_claims.delete(
            namespace=consensus.namespace, name=deployment_name
        )


def _run_consensus_process(
    application_id: ApplicationId,
    directory: str,
    address: str,
    requested_serviceables: list[Serviceable],
    placement_planner_address: RoutableAddress,
    token_verifier: Optional[TokenVerifier],
    # This multiprocessing.Queue can't be typed, but it's of type:
    #   Queue[Union[int, str]]
    queue: multiprocessing.Queue,
    file_descriptor_set: FileDescriptorSet,
    effect_validation: EffectValidation,
):
    """Helper that runs an instance of a server in its own process.
    """

    async def run() -> None:
        resolver: Optional[DirectResolver] = None
        state_manager: Optional[LocalSidecarStateManager] = None
        server: Optional[_ServiceServer] = None

        try:
            resolver = DirectResolver(placement_planner_address)

            await resolver.start()

            state_manager = LocalSidecarStateManager(directory)

            # Pass a port of 0 to allow the Server to pick its own
            # (unused) port.
            server = _ServiceServer(
                application_id=application_id,
                serviceables=requested_serviceables,
                listen_address=address,
                token_verifier=token_verifier,
                state_manager=state_manager,
                actor_resolver=resolver,
                file_descriptor_set=file_descriptor_set,
                effect_validation=effect_validation,
                # For local consensuses, initialization is done at a higher
                # level.
                initialize=None,
            )

            await server.start()

            # Communicate the ports back to the caller.
            queue.put(server.port())
            queue.put(server.websocket_port())
        except Exception as e:
            # We failed to communicate a port to the caller, so
            # instead we'll communicate the error back to the caller.
            #
            # NOTE: passing exceptions across a process will lose the
            # trace information so instead we stringify the error here
            # to print out later.
            queue.put(''.join(traceback.format_exception(e)))

            # NOTE: we don't re-raise the error here as it adds a lot
            # of cruft to the output and may get interleaved with
            # other output making it hard to parse.
        else:
            # TODO(benh): catch other errors and propagate them back
            # to the error as well.
            await server.wait()
        finally:
            if server is not None:
                await server.stop()
                await server.wait()

            if state_manager is not None:
                await state_manager.shutdown_and_wait()

            if resolver is not None:
                await resolver.stop()

    asyncio.run(run())


@dataclass(
    frozen=True,
    kw_only=True,
)
class RegisteredServiceable:
    """Helper class encapsulating properties for a serviceable."""
    serviceable: Serviceable
    in_process: bool
    local_envoy: bool
    local_envoy_port: int
    token_verifier: Optional[TokenVerifier]
    directory: Optional[str]
    effect_validation: Optional[EffectValidation]


@dataclass(
    frozen=True,
    kw_only=True,
)
class LaunchedConsensus:
    """Helper class for a launched consensus."""
    consensus: Consensus
    serviceables: list[Serviceable]
    addresses: placement_planner_pb2.ConsensusAddresses

    local_envoy: Optional[LocalEnvoy] = None

    @dataclass(
        frozen=True,
        kw_only=True,
    )
    class InProcess:
        """Encapsulates everything created for an "in process" consensus."""
        server: _ServiceServer
        resolver: DirectResolver
        state_manager: LocalSidecarStateManager

    @dataclass(
        frozen=True,
        kw_only=True,
    )
    class Subprocess:
        """Encapsulates everything created for a "subprocess" consensus."""
        process: multiprocessing.Process
        # `threading.Event` is an alias for `multiprocessing.Event`, so even
        # though we're using a `multiprocessing.Process` we must use
        # `threading.Event`, since we can't use type aliases in type hints.
        terminated: threading.Event

    # Only one of 'in_process' or 'subprocess' will be set.
    in_process: Optional[InProcess] = None
    subprocess: Optional[Subprocess] = None


class LocalConsensusManager(ConsensusManager):

    def __init__(self):
        super().__init__()
        # Map of fully qualified service name to a tuple of Python
        # serviceable class and whether or not to run the server for this
        # serviceable in the same process or a separate process.
        self._serviceables_by_name: dict[ServiceName,
                                         RegisteredServiceable] = {}

        # Map of launched consensuses, indexed by consensus name.
        self._launched_consensuses: dict[ConsensusId, LaunchedConsensus] = {}

        # We create a single temporary directory that we put each of
        # the state managers subdirectories within to make it easier
        # to clean up all of them. Note that we explicitly _do not_
        # want to clean up each state manager's directory after
        # deleting its corresponding consensus because it is possible
        # that the same consensus (i.e., a consensus with the same
        # name) will be (re)created in the future and it needs its
        # directory!
        self._directory = tempfile.TemporaryDirectory()

        # Placement planner address must be set later because there is
        # a cycle where PlacementPlanner depends on ConsensusManager,
        # so we won't know the address to give to the
        # LocalConsensusManager until after the PlacementPlanner has
        # been created.
        self._placement_planner_address: Optional[RoutableAddress] = None

    def __del__(self):
        """Custom destructor in order to avoid the temporary directory being
        deleted _before_ the state managers have been shutdown.
        """

        async def shutdown_and_wait():
            for launched_consensus in self._launched_consensuses.values():
                if launched_consensus.in_process is not None:
                    await launched_consensus.in_process.state_manager.shutdown_and_wait(
                    )

        # This destructor cannot be async, but the `launched_consensus` code is
        # all async, so we need to go through this little hoop to run its
        # shutdown procedure.
        try:
            current_event_loop = asyncio.get_running_loop()
            # If the above doesn't raise, then this synchronous method is being
            # called from an async context.
            # Since we have a running event loop, we must call the async
            # function on that loop rather than via asyncio.run().
            _ = current_event_loop.create_task(shutdown_and_wait())
        except RuntimeError:
            # We're in a fully synchronous context. Call the async function via
            # asyncio.run().
            asyncio.run(shutdown_and_wait())

    def get_local_envoy_for_serviceable(
        self, serviceable: Serviceable
    ) -> Optional[LocalEnvoy]:
        for launched_consensus in self._launched_consensuses.values():
            if launched_consensus.local_envoy is None:
                continue

            if serviceable in launched_consensus.serviceables:
                return launched_consensus.local_envoy

        return None

    def register_placement_planner_address(
        self, placement_planner_address: RoutableAddress
    ):
        """Register the placement planner address so that we can bring up new
        servers that can create resolvers that get actor routes from
        the placement planner.

        NOTE: this must be called _before_ a consensus can be created.
        Unfortunately we can't pass the address into the constructor because
        there is a cycle where PlacementPlanner depends on ConsensusManager,
        so we won't know the address to give to the LocalConsensusManager until
        after the PlacementPlanner has been created.
        """
        self._placement_planner_address = placement_planner_address

    def register_serviceables(
        self,
        *,
        serviceables: list[Serviceable],
        token_verifier: Optional[TokenVerifier] = None,
        in_process: bool,
        local_envoy: bool,
        local_envoy_port: int,
        directory: Optional[str],
        effect_validation: Optional[EffectValidation],
    ):
        """Save the given serviceable definitions so that we can bring up
        corresponding objects if and when a Consensus requires them."""
        for serviceable in serviceables:
            # TODO: I think we ought to check that the name is not already in
            # the dict.
            self._serviceables_by_name[serviceable.service_name()
                                      ] = RegisteredServiceable(
                                          serviceable=serviceable,
                                          in_process=in_process,
                                          local_envoy=local_envoy,
                                          local_envoy_port=local_envoy_port,
                                          token_verifier=token_verifier,
                                          directory=directory,
                                          effect_validation=effect_validation,
                                      )

    async def _delete_consensus(
        self,
        consensus: Consensus,
    ) -> None:
        """Stop the process or server corresponding to the given Consensus and delete it
        from our internal records.
        If there is no such process or server, do nothing."""
        launched_consensus = self._launched_consensuses.pop(consensus.id, None)

        if launched_consensus is None:
            return

        if launched_consensus.local_envoy is not None:
            await launched_consensus.local_envoy.stop()

        if launched_consensus.subprocess is not None:
            launched_consensus.subprocess.terminated.set()
            # Perform a graceful termination by first doing 'terminate'
            # followed after a grace period by 'kill'.
            launched_consensus.subprocess.process.terminate()
            # Wait no more than 3 seconds.
            launched_consensus.subprocess.process.join(timeout=3)
            if launched_consensus.subprocess.process.is_alive():
                launched_consensus.subprocess.process.kill()
                # Waiting forever is safe because kill can not be trapped!
                launched_consensus.subprocess.process.join()
        else:
            assert launched_consensus.in_process is not None

            await launched_consensus.in_process.server.stop()
            await launched_consensus.in_process.server.wait()

            await launched_consensus.in_process.resolver.stop()

            # NOTE: need to explicitly shutdown+wait the state manager so that
            # another state manager can be brought up immediately for the same
            # consensus (e.g., as part of a consensus restart) without conflict.
            await launched_consensus.in_process.state_manager.shutdown_and_wait(
            )

    async def _set_consensus(
        self,
        consensus: Consensus,
    ) -> placement_planner_pb2.ConsensusAddresses:
        """Start a gRPC server, in the same process or a separate process,
        serving all the services in the given Consensus, and return
        its address.
        """
        # If this is an "update" to an existing consensus, don't do
        # anything (assuming there is not anything to be done, which
        # locally should always be the case).
        launched_consensus = self._launched_consensuses.get(consensus.id)

        if launched_consensus is not None:
            assert launched_consensus.consensus == consensus
            return launched_consensus.addresses

        # Ok, this isn't an update, we want to create a consensus!
        assert self._placement_planner_address is not None

        # Gather all the serviceables used in the given consensus.
        in_process_serviceables: list[Serviceable] = []
        subprocess_serviceables: list[Serviceable] = []
        envoy_serviceables: list[Serviceable] = []
        envoy_port: int = 0
        directory: Optional[str] = None
        token_verifier: Optional[TokenVerifier] = None
        maybe_effect_validation: Optional[EffectValidation] = None
        for service_name in consensus.service_names:
            registered_serviceable = self._serviceables_by_name[service_name]
            if registered_serviceable.in_process:
                in_process_serviceables.append(
                    registered_serviceable.serviceable
                )
            else:
                subprocess_serviceables.append(
                    registered_serviceable.serviceable
                )

            if registered_serviceable.local_envoy:
                envoy_serviceables.append(registered_serviceable.serviceable)
                if envoy_port == 0:
                    envoy_port = registered_serviceable.local_envoy_port
                else:
                    assert envoy_port == registered_serviceable.local_envoy_port

            if registered_serviceable.token_verifier is not None:
                if token_verifier is None:
                    token_verifier = registered_serviceable.token_verifier
                else:
                    assert token_verifier == registered_serviceable.token_verifier

            if registered_serviceable.directory is not None:
                if directory is None:
                    directory = registered_serviceable.directory
                else:
                    assert directory == registered_serviceable.directory

            if maybe_effect_validation is None:
                maybe_effect_validation = registered_serviceable.effect_validation
            else:
                assert maybe_effect_validation == registered_serviceable.effect_validation

        effect_validation = maybe_effect_validation or EffectValidation[
            os.getenv(ENVVAR_RSM_DEV_EFFECT_VALIDATION, "ENABLED").upper()]

        launch_local_envoy = len(envoy_serviceables) > 0

        # Ensure we have a directory for the sidecar for this consensus.
        directory = os.path.join(
            directory or self._directory.name,
            f'{consensus.id}{SIDECAR_SUFFIX}',
        )

        try:
            os.mkdir(directory)
        except FileExistsError:
            # The directory might already exist when we're bringing
            # back up a consensus after an induced failure as well as
            # when using 'rsm' locally for development.
            pass

        async def launch():
            assert directory is not None

            host = EVERY_LOCAL_NETWORK_ADDRESS

            # Invariant here is that all the services are either in
            # subprocesses or in-process, but not a mix, as enforced,
            # e.g., by 'resemble.aio.tests.Resemble'
            if len(subprocess_serviceables) != 0:
                assert len(in_process_serviceables) == 0
                assert not launch_local_envoy or subprocess_serviceables == envoy_serviceables
                return await self._launch_subprocess_consensus(
                    directory,
                    host,
                    consensus,
                    subprocess_serviceables,
                    token_verifier,
                    launch_local_envoy,
                    envoy_port,
                    effect_validation,
                )
            elif len(in_process_serviceables) != 0:
                assert len(subprocess_serviceables) == 0
                assert not launch_local_envoy or in_process_serviceables == envoy_serviceables
                return await self._launch_in_process_consensus(
                    directory,
                    host,
                    consensus,
                    in_process_serviceables,
                    token_verifier,
                    launch_local_envoy,
                    envoy_port,
                    effect_validation,
                )

        launched_consensus = await launch()

        self._launched_consensuses[consensus.id] = launched_consensus

        return launched_consensus.addresses

    async def _launch_in_process_consensus(
        self,
        directory: str,
        host: str,
        consensus: Consensus,
        serviceables: list[Serviceable],
        token_verifier: Optional[TokenVerifier],
        launch_local_envoy: bool,
        envoy_port: int,
        effect_validation: EffectValidation,
    ) -> LaunchedConsensus:
        assert self._placement_planner_address is not None
        resolver = DirectResolver(self._placement_planner_address)
        await resolver.start()

        state_manager = LocalSidecarStateManager(directory)

        server = _ServiceServer(
            application_id=consensus.application_id,
            serviceables=serviceables,
            listen_address=f'{host}:0',
            token_verifier=token_verifier,
            state_manager=state_manager,
            actor_resolver=resolver,
            file_descriptor_set=consensus.file_descriptor_set,
            effect_validation=effect_validation,
            # For local consensuses, initialization is done at a higher level.
            # This discrepancy is a little awkward, but any work we'd do to
            # address that awkwardness will be made moot when we remove all of
            # this code in favor of the new singletons approach.
            initialize=None,
        )

        await server.start()

        port = server.port()
        websocket_port = server.websocket_port()

        # The consensus should now be reachable at the address of the
        # server we started in the subprocess.
        addresses = placement_planner_pb2.ConsensusAddresses(
            consensus_id=consensus.id,
            addresses=[
                placement_planner_pb2.ConsensusAddress(host=host, port=port)
            ]
        )

        return LaunchedConsensus(
            consensus=consensus,
            serviceables=serviceables,
            addresses=addresses,
            local_envoy=await self._launch_local_envoy(
                host,
                port,
                websocket_port,
                consensus.application_id,
                serviceables,
                envoy_port,
            ) if launch_local_envoy else None,
            in_process=LaunchedConsensus.InProcess(
                server=server,
                resolver=resolver,
                state_manager=state_manager,
            ),
        )

    async def _launch_subprocess_consensus(
        self,
        directory: str,
        host: str,
        consensus: Consensus,
        serviceables: list[Serviceable],
        token_verifier: Optional[TokenVerifier],
        launch_local_envoy: bool,
        envoy_port: int,
        effect_validation: EffectValidation,
    ) -> LaunchedConsensus:
        # Create and start a process to run a server for the servicers.
        #
        # We use a queue to report back the port on which the process
        # is running. Even though we only need a single value, a queue
        # provides an "eventing" mechanism while
        # 'multiprocessing.Value' does not.
        port_or_stringified_error_queue: multiprocessing.Queue[Union[
            int, str]] = multiprocessing.Queue()

        loop = asyncio.get_running_loop()

        process = multiprocessing.Process(
            target=_run_consensus_process,
            args=(
                consensus.application_id,
                directory,
                f'{host}:0',
                serviceables,
                self._placement_planner_address,
                token_verifier,
                port_or_stringified_error_queue,
                consensus.file_descriptor_set,
                effect_validation,
            ),
            # NOTE: we set 'daemon' to True so that this process will
            # attempt to terminate our subprocess when it exits.
            #
            # TODO(benh): ensure that this always happens by using
            # something like a pipe.
            daemon=True,
        )
        process.start()

        # Watch the process to see if it exits prematurely so that we
        # can try and provide some better debugging for end users. We
        # use a 'terminated' event to differentiate when we initiated
        # the termination vs when the process exits on its own.
        terminated = threading.Event()

        # The consensus will communicate ports (or its failure to produce
        # ports) on a sync queue. However, we're in an async context here, so we
        # can't just block on the sync queue. Instead, we'll execute the get in
        # the default pool executor. This gives us a coroutine for the call that
        # we can safely await.
        async def get_port() -> int:
            port_or_stringified_error: Union[int, str] = (
                await loop.run_in_executor(
                    None,
                    port_or_stringified_error_queue.get,
                )
            )

            if isinstance(port_or_stringified_error, str):
                # The process failed to start, so it communicated a
                # stringified error. Raise an exception back up to
                # (eventually) the user.
                stringified_error: str = port_or_stringified_error

                # Emulate `traceback.print_exc()` by printing the
                # error to `sys.stderr`.
                print(stringified_error, file=sys.stderr)

                # While there may be many different errors, there are some in
                # the case of running `rsm dev run` that we'd like to help the user
                # make sense of with additional warnings.
                #
                # Also, we only bother checking for these errors here and not
                # when we launch an in-process consensus because we only care
                # about the `rsm dev run` case which always uses subprocesses.
                # TODO: A better way to handle this would be to have a
                # `rsm dev run` equivalent of `on_kubernetes`, e.g. `if
                # using_rsm_dev_run(): ...`.
                if not on_kubernetes():
                    if (
                        'Failed to instantiate service' in stringified_error
                        and '/LOCK:' in stringified_error
                    ):
                        terminal.warn(
                            '\n'
                            'Did you start another instance of `rsm dev run` '
                            'in another terminal?'
                            '\n'
                        )

                raise InputError(
                    reason=f"Consensus '{consensus.id}' failed to start"
                )

            # If we didn't get an error, we must have gotten a port.
            return port_or_stringified_error

        port = await get_port()
        websocket_port = await get_port()

        # The process may still fail after it started. We can't communicate that
        # directly to the user through a raised exception on the user's thread,
        # but we can at least do our best to notice and report it in a separate
        # thread.
        def watch():
            process.join()
            if raised_signal() is None and not terminated.is_set():
                # TODO(benh): propagate the failure instead of just
                # terminating the process.
                print(
                    f"Process for consensus '{consensus.id}' has "
                    f"prematurely exited with status code '{process.exitcode}'",
                    file=sys.stderr
                )
                os.kill(os.getpid(), signal.SIGTERM)

        threading.Thread(target=watch, daemon=True).start()

        # The consensus should now be reachable at the address of the
        # server we started in the subprocess.
        addresses = placement_planner_pb2.ConsensusAddresses(
            consensus_id=consensus.id,
            addresses=[
                placement_planner_pb2.ConsensusAddress(host=host, port=port)
            ]
        )

        return LaunchedConsensus(
            consensus=consensus,
            serviceables=serviceables,
            addresses=addresses,
            local_envoy=await self._launch_local_envoy(
                host,
                port,
                websocket_port,
                consensus.application_id,
                serviceables,
                envoy_port,
            ) if launch_local_envoy else None,
            subprocess=LaunchedConsensus.Subprocess(
                process=process,
                terminated=terminated,
            ),
        )

    async def _launch_local_envoy(
        self,
        host: str,
        port: int,
        websocket_port: int,
        application_id: str,
        serviceables: list[Serviceable],
        envoy_port: int,
    ) -> LocalEnvoy:
        local_envoy = LocalEnvoy(
            application_id=application_id,
            proxied_server_host=host,
            proxied_server_port=port,
            proxied_server_websocket_port=websocket_port,
            # NOTE: we also tell `LocalEnvoy` to proxy traffic for all
            # of the `Routable`s that the `_ServiceServer` declares
            # (i.e., system services).
            routables=serviceables + _ServiceServer.ROUTABLES,
            published_port=envoy_port,
        )

        await local_envoy.start()

        return local_envoy


class FakeConsensusManager(ConsensusManager):
    """The FakeConsensusManager doesn't actually start any servers. It will just
    reply with a made-up address for any consensus that is requested.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def address_for_consensus(
        consensus_id: str
    ) -> placement_planner_pb2.ConsensusAddress:
        return placement_planner_pb2.ConsensusAddress(
            host=f'hostname-for-{consensus_id}',
            port=1337,
        )

    async def _set_consensus(
        self,
        consensus: Consensus,
    ) -> placement_planner_pb2.ConsensusAddresses:
        return placement_planner_pb2.ConsensusAddresses(
            consensus_id=consensus.id,
            addresses=[
                FakeConsensusManager.address_for_consensus(consensus.id)
            ],
            namespace=consensus.namespace,
        )

    async def _delete_consensus(
        self,
        consensus: Consensus,
    ) -> None:
        # Nothing to be done, since we don't actually create any consensuses.
        pass
