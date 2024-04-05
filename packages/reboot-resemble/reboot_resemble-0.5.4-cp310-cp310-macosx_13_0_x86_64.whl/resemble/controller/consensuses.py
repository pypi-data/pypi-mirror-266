from dataclasses import dataclass, field
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from resemble.v1alpha1 import placement_planner_pb2
from typing import Optional


@dataclass(kw_only=True)
class Consensus:
    """Data structure used internally in the Controller to represent a
    Consensus.
    """
    # The id of the Consensus.
    id: str

    # The id of the application that the Consensus is associated with.
    application_id: str

    # List of service names that are served with the Consensus.
    service_names: list[str] = field(default_factory=list)

    # The name of the container image that the Consensus is associated with.
    # This is currently only relevant when running on Kubernetes.
    container_image_name: Optional[str] = None

    # The Kubernetes namespace that the Consensus is associated with.
    # When running on Kubernetes this must be set to a non-empty string.
    namespace: Optional[str] = None

    # The file descriptor set of the Services that the Consensus is associated
    # with.
    file_descriptor_set: Optional[FileDescriptorSet] = None

    # This might become `addresses: Optional[
    #   list[placement_planner_pb2.ConsensusAddresses]]` in the future when we
    # support replicated consensuses.
    address: Optional[placement_planner_pb2.ConsensusAddress] = None
