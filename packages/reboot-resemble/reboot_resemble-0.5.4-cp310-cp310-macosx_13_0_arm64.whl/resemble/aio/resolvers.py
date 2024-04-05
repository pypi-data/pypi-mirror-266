import asyncio
import grpc
from abc import ABC, abstractmethod
from resemble.aio.servicers import Servicer
from resemble.aio.types import (
    ActorId,
    ConsensusId,
    RoutableAddress,
    ServiceName,
)
from resemble.v1alpha1 import placement_planner_pb2, placement_planner_pb2_grpc
from respect.grpc.options import make_retry_channel_options
from respect.logging import get_logger
from typing import Optional

logger = get_logger(__name__)


class ActorResolver(ABC):
    """Abstract base class for a resolver able to resolve an actor id and
    service name into a routable address.
    """

    @abstractmethod
    def resolve_actor(
        self,
        service_name: ServiceName,
        actor_id: ActorId,
    ) -> Optional[RoutableAddress]:
        """Get routable address for actor."""
        # This function is not allowed to block.
        # ISSUE(#1178): This function is deliberately not async.
        pass

    def resolve(
        self,
        servicer_type: type[Servicer],
        actor_id: ActorId,
    ) -> Optional[RoutableAddress]:
        """Get routable address for actor."""
        return self.resolve_actor(servicer_type.__service_name__, actor_id)


class DictResolver(ActorResolver):
    """A dictionary backed resolver.

    Resolves actors based on a dictionary from an service name to a routable
    addresses.
    """

    def __init__(
        self,
        servicer_dict: Optional[dict[ServiceName, RoutableAddress]] = None
    ):
        self._lookup: dict[ServiceName, RoutableAddress] = servicer_dict or {}

    def resolve_actor(
        self,
        service_name: ServiceName,
        actor_id: ActorId,
    ) -> Optional[RoutableAddress]:
        """Resolve actor using internal dictionary. The actor id is unused."""
        return self._lookup.get(service_name)

    def update(self, update: dict[ServiceName, RoutableAddress]) -> None:
        """Update the internal dictionary with items from the input."""
        self._lookup.update(update)


class DirectResolver(ActorResolver):
    """A resolver that listens directly to a PlacementPlanner to learn
    about actors and their addresses.

    Primarily expected to be useful in unit tests, where more sophisticated
    (and scalable) mechanisms like using an Envoy routing filter are
    unavailable.
    """

    def __init__(self, placement_planner_address: RoutableAddress):
        self._placement_planner_address = placement_planner_address
        self._address_by_consensus: dict[ConsensusId, RoutableAddress] = {}
        self._consensus_by_service: dict[ServiceName, ConsensusId] = {}
        self._change_event = asyncio.Event()
        self._control_loop_task: Optional[asyncio.Task] = None

    async def _control_loop(self):
        """Start the DirectResolver's process of listening to the
        PlacementPlanner. Runs forever, except in case of errors. Must be
        called before `resolve_actor()` can return useful values.
        """
        async with grpc.aio.insecure_channel(
            self._placement_planner_address,
            options=make_retry_channel_options()
        ) as channel:
            stub = placement_planner_pb2_grpc.PlacementPlannerStub(channel)
            request = placement_planner_pb2.ListenForPlanRequest()
            async for response in stub.ListenForPlan(request):
                new_address_by_consensus: dict[ConsensusId,
                                               RoutableAddress] = {}
                for location in response.plan_with_locations.locations:
                    # Always pick the first address.
                    if len(location.addresses) < 1:
                        # This consensus is not routable. That's strange.
                        logger.warning(
                            f'Got consensus {location.consensus_id} '
                            'without address'
                        )
                        continue
                    consensus_address = location.addresses[0]
                    routable_address: RoutableAddress = f'{consensus_address.host}:{consensus_address.port}'
                    new_address_by_consensus[location.consensus_id
                                            ] = routable_address

                new_consensus_by_service: dict[ServiceName, ConsensusId] = {}
                for service_plan in response.plan_with_locations.plan.service_plans:
                    num_partitions = len(service_plan.partition_assignments)
                    if num_partitions != 1:
                        raise ValueError(
                            'Expected exactly 1 partition for service '
                            f'{service_plan.service_name}; got {num_partitions}'
                        )
                    partition = service_plan.partition_assignments[0]
                    new_consensus_by_service[service_plan.service_name
                                            ] = partition.consensus_id

                self._address_by_consensus = new_address_by_consensus
                self._consensus_by_service = new_consensus_by_service

                # Tell everyone currently waiting that a new plan was received,
                # but then immediately block any future waiters.
                self._change_event.set()
                self._change_event.clear()

    async def start(self):
        """Start the DirectResolver control loop in an asyncio Task."""
        self._control_loop_task = asyncio.create_task(self._control_loop())

    async def stop(self):
        """Stop the DirectResolver control loop and wait for it to complete."""
        if self._control_loop_task is not None:
            try:
                if not self._control_loop_task.done():
                    self._control_loop_task.cancel()

                await self._control_loop_task
            except (asyncio.exceptions.CancelledError, Exception):
                # The control loop's gRPC connection may have raised
                # some errors due to cancellation (from us or from
                # another component) - we're done using it now, so we
                # don't actually care.
                pass

    def addresses(self) -> dict[ServiceName, RoutableAddress]:
        """Return all the current mappings of service name to addresses."""
        return {
            service_name: self._address_by_consensus[consensus_id] for
            service_name, consensus_id in self._consensus_by_service.items()
        }

    async def wait_for_expected(
        self, expected: dict[ServiceName, RoutableAddress]
    ):
        """Wait for the mapping between `ServiceName`s and `RoutableAddress`es
        to reach an expected state.
        """
        if len(expected) == 0:
            while len(self._consensus_by_service) != 0:
                await self._change_event.wait()
        else:
            while self.addresses() != expected:
                await self._change_event.wait()

    async def wait_for_servicers(self, servicers: list[type[Servicer]]):
        """Syntactic sugar for wait_for_service_names that takes `Servicer`s.
        """
        service_names = [servicer.__service_name__ for servicer in servicers]

        await self.wait_for_service_names(service_names)

    def _raise_if_done(self):
        if self._control_loop_task is None:
            raise RuntimeError('DirectResolver control loop was never started')
        elif self._control_loop_task.done():
            exception = self._control_loop_task.exception()
            if exception is not None:
                raise RuntimeError(
                    'DirectResolver control loop failed'
                ) from exception
            else:
                raise RuntimeError('DirectResolver control loop has stopped')

    async def wait_for_service_names(self, service_names: list[str]):
        """Returns once a placement plan with the all the service names has
        been created, which may be immediately."""
        self._raise_if_done()
        while not all(
            service_name in self._consensus_by_service
            for service_name in service_names
        ):
            self._raise_if_done()
            await self._change_event.wait()

    def resolve_actor(
        self,
        service_name: ServiceName,
        actor_id: ActorId,
    ) -> Optional[RoutableAddress]:
        """Finds the routable address for the given actor id on the given
        service."""
        # Actor id is unused, since (for the time being), all actors for a
        # service have the same routable address. This will likely change in the
        # future.
        self._raise_if_done()

        consensus_id = self._consensus_by_service.get(service_name)

        if consensus_id is not None:
            return self._address_by_consensus.get(consensus_id)

        return None


class StaticResolver(ActorResolver):
    """A resolver that always returns the same address for all actors."""

    def __init__(self, address: RoutableAddress):
        self.address = address

    def resolve_actor(
        self,
        service_name: ServiceName,
        actor_id: ActorId,
    ) -> Optional[RoutableAddress]:
        return self.address
