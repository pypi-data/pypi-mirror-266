import kubernetes_asyncio.client
from resemble.controller.reboot_custom_object import RebootCustomObject
from resemble.naming import ApplicationId
from resemble.v1alpha1 import application_config_pb2
from typing import Optional


class ApplicationConfig(
    RebootCustomObject[application_config_pb2.ApplicationConfig]
):
    """
    This Python class wraps a generated proto object representing a Reboot
    custom object (i.e., not a K8s or Istio specific custom object). The
    CustomObject children knows how to talk to the k8s API to instantiate these
    objects in k8s.
    """

    Spec = application_config_pb2.ApplicationConfig.Spec

    @classmethod
    def create(
        cls,
        application_id: ApplicationId,
        metadata: Optional[kubernetes_asyncio.client.V1ObjectMeta],
        spec: application_config_pb2.ApplicationConfig.Spec,
    ) -> 'ApplicationConfig':
        metadata = metadata or kubernetes_asyncio.client.V1ObjectMeta()

        # Invariant: the ApplicationConfig's `metadata.name` will be the
        #            application ID. Even when we're not running on Kubernetes!
        assert metadata.name is None or metadata.name == application_id
        metadata.name = application_id

        return cls(
            metadata=metadata,
            spec=spec,
        )

    def application_id(self) -> ApplicationId:
        if self.metadata.name is None:
            raise ValueError(
                "Cannot determine application ID: ApplicationConfig has no "
                "'metadata.name'"
            )
        return self.metadata.name
