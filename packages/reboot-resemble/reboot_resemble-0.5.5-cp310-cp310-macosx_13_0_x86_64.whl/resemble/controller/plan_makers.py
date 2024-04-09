import time
from resemble.aio.servers import _ServiceServer
from resemble.controller.application_config import ApplicationConfig
from resemble.v1alpha1 import placement_planner_pb2
from respect.logging import get_logger
from typing import Iterable, Optional

logger = get_logger(__name__)


class PlanMaker:
    """
    Logic to construct a placement Plan based on a set of currently valid
    ApplicationConfigs. Designed to be extendable for different Plan structures.
    """

    last_version: Optional[int] = None

    def make_plan(
        self, application_configs: Iterable[ApplicationConfig]
    ) -> placement_planner_pb2.Plan:
        """
        Construct a Plan for consensuses that will serve the given list of
        ApplicationConfigs.
        """
        service_plans = []
        for application_config in application_configs:
            application_id = application_config.application_id()

            # NOTE: We are deliberately using a `list` here instead of a `set`
            # to avoid issues with change of ordering. Some tests rely on the
            # ordering and `set` order elements internally by hash value, which
            # is not stable between platforms.
            unique_service_names: list[str] = []
            for service_name in application_config.spec.service_names:
                if service_name in unique_service_names:
                    logger.warning(
                        "Service name '%s' is duplicated in application '%s'",
                        service_name,
                        application_id,
                    )
                    continue
                unique_service_names.append(service_name)

            for service_name in unique_service_names:
                # Ignore system services which exist on every consensus.
                if service_name in _ServiceServer.SYSTEM_SERVICE_NAMES:
                    continue

                # We will use the same consensus for all services in a server.
                consensus_id = application_id

                # We only want one partition assignment for the whole keyspace
                # of the service.
                partition_assignment = placement_planner_pb2.PartitionAssignment(
                    partition=placement_planner_pb2.Partition(
                        first_key='', last_key=''
                    ),
                    consensus_id=consensus_id
                )
                service_plans.append(
                    placement_planner_pb2.ServicePlan(
                        service_name=service_name,
                        application_id=application_id,
                        partition_assignments=[partition_assignment],
                    )
                )

        return placement_planner_pb2.Plan(
            version=self.get_version(), service_plans=service_plans
        )

    def get_version(self) -> int:
        """
        Return a valid version number that is (expected to be) greater than
        whatever was previously returned or used.
        We use a timestamp (in ns from epoch) to ensure that version numbers
        increase, and further verify that time has not somehow gone backwards.
        """
        timestamp = time.time_ns()
        if self.last_version is not None and timestamp <= self.last_version:
            raise RuntimeError(
                f'Time is not moving forward as expected! '
                f'New timestamp {timestamp} is not after '
                f'old timestamp {self.last_version}.'
            )
        self.last_version = timestamp
        return timestamp
