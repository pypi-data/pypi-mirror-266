import asyncio
import grpc
from concurrent import futures
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from resemble.aio.types import ConsensusId
from resemble.controller.application_config import ApplicationConfig
from resemble.controller.application_config_trackers import (
    ApplicationConfigTracker,
)
from resemble.controller.consensus_managers import ConsensusManager
from resemble.controller.consensuses import Consensus
from resemble.controller.exceptions import InputError
from resemble.controller.plan_makers import PlanMaker
from resemble.naming import ApplicationId
from resemble.v1alpha1 import placement_planner_pb2, placement_planner_pb2_grpc
from respect.logging import ERROR, get_logger
from typing import AsyncGenerator, Awaitable, Callable, Optional

logger = get_logger(__name__)
# TODO(rjh, benh): set up a logging system that allows us to increase
# the verbosity level of the logs by environment variable.
logger.setLevel(ERROR)


class PlacementPlanner(placement_planner_pb2_grpc.PlacementPlannerServicer):

    def __init__(
        self, config_tracker: ApplicationConfigTracker,
        consensus_manager: ConsensusManager, address: str
    ) -> None:
        self.plan_maker = PlanMaker()
        self.config_tracker = config_tracker
        self.consensus_manager = consensus_manager
        # Use pubsub queues to be sure to notify all plan listeners whenever
        # there's a new plan.
        self.listener_queues: set[asyncio.Queue[
            placement_planner_pb2.PlanWithLocations]] = set()

        # Public set of callbacks that are called with the new PlanWithLocations
        # whenever one becomes available. Clients that want callbacks should add
        # their callbacks directly to this set.
        self.plan_change_callbacks: set[
            Callable[[placement_planner_pb2.PlanWithLocations],
                     Awaitable[None]]] = set()

        self._started = False

        self._server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=10)
        )

        placement_planner_pb2_grpc.add_PlacementPlannerServicer_to_server(
            self, self._server
        )

        self._port = self._server.add_insecure_port(address)
        self._host = address.split(':')[0]

        # Get notified when we need a new plan, either because the set of
        # ApplicationConfigs has changed or because consensuses have moved.
        async def make_plan_but_errors_are_input_errors() -> None:
            """Helper function to treat errors from `make_plan` as input errors.
            """
            try:
                await self.make_plan()
            except ValueError as e:
                raise InputError(
                    reason=str(e),
                    parent_exception=e,
                ) from e

        # Two conditions can cause a new plan to be made: either a location
        # change or a change to a `ApplicationConfig`. In case a new plan can
        # not be made, `make_plan` throws an exception, a `ValueError`. In case
        # the error stems from an change to a `ApplicationConfig`, this is an
        # `InputError` and should be propagated as such. To accomplish this we
        # use the helper function defined above as the callback in case of
        # `ApplicationConfig` changes.
        self.config_tracker.on_configs_change(
            make_plan_but_errors_are_input_errors
        )
        self.consensus_manager.on_locations_change(self.make_plan)

        self.current_plan_with_locations: Optional[
            placement_planner_pb2.PlanWithLocations] = None

    async def start(self) -> None:
        """
        Start a gRPC server at the given address to host the ListenForPlan
        endpoint.
        """
        await self.make_plan()
        await self._server.start()
        self._started = True
        logger.info(f"PlacementPlanner server started on port {self._port}")

    def port(self) -> int:
        return self._port

    def address(self) -> str:
        return f'{self._host}:{self._port}'

    async def stop(self) -> None:
        """Stop the gRPC server that was started."""
        if self._started:
            await self._server.stop(grace=None)
            logger.info('PlacementPlanner server stopped')

    async def make_plan(self) -> None:
        """
        Generate a new placement plan based on the currently valid set of
        ApplicationConfigs, update cluster resources to match the updated plan,
        and send the updated plan information out to all subscribed listeners.
        """
        application_configs: dict[
            ApplicationId, ApplicationConfig
        ] = await self.config_tracker.get_application_configs()
        logger.info(
            f'Making new plan based on {len(application_configs)} application '
            f'configs: {list(application_configs.keys())}'
        )

        new_plan = self.plan_maker.make_plan(application_configs.values())
        # Combine the Plan and the ApplicationConfigs into Consensuses.
        # Use a dict to implicitly de-duplicate so that each consensus name is
        # only included once.
        consensuses: dict[ConsensusId, Consensus] = {}
        for service_plan in new_plan.service_plans:
            assert service_plan.application_id != ""
            application_config = application_configs[
                service_plan.application_id]

            for partition_assignment in service_plan.partition_assignments:
                file_descriptor_set = FileDescriptorSet()
                file_descriptor_set.ParseFromString(
                    application_config.spec.file_descriptor_set
                )
                consensuses[partition_assignment.consensus_id] = Consensus(
                    id=partition_assignment.consensus_id,
                    container_image_name=application_config.spec.
                    container_image_name,
                    namespace=application_config.metadata.namespace,
                    service_names=application_config.spec.service_names,
                    file_descriptor_set=file_descriptor_set,
                    application_id=service_plan.application_id,
                )

        logger.info(
            f'Plan version {new_plan.version} consensuses: {consensuses.keys()}'
        )

        consensus_locations = await self.consensus_manager.set_consensuses(
            consensuses.values()
        )
        plan_with_locations = placement_planner_pb2.PlanWithLocations(
            plan=new_plan, locations=consensus_locations
        )
        self.current_plan_with_locations = plan_with_locations
        for queue in self.listener_queues:
            await queue.put(plan_with_locations)

        # Execute all callbacks for everyone.
        await asyncio.gather(
            *[
                callback(plan_with_locations)
                for callback in self.plan_change_callbacks
            ]
        )

        logger.info(f'Plan version {new_plan.version} active')

    async def ListenForPlan(
        self, request: placement_planner_pb2.ListenForPlanRequest, context
    ) -> AsyncGenerator[placement_planner_pb2.ListenForPlanResponse, None]:
        """
        Serve the current plan immediately, then send an update every time a
        new plan is generated.
        """
        queue: asyncio.Queue[placement_planner_pb2.PlanWithLocations
                            ] = asyncio.Queue()
        self.listener_queues.add(queue)

        if self.current_plan_with_locations is not None:
            # Clients should immediately get the current plan.
            await queue.put(self.current_plan_with_locations)

        while True:
            plan_with_locations = await queue.get()
            try:
                yield placement_planner_pb2.ListenForPlanResponse(
                    plan_with_locations=plan_with_locations
                )
            except GeneratorExit:
                # When the client disconnects, we will eventually get a
                # GeneratorExit thrown. We should clean up the state associated
                # with this client before returning.
                self.listener_queues.remove(queue)
                return
