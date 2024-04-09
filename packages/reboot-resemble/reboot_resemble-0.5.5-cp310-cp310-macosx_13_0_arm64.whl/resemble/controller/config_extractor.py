import asyncio
import grpc
import kubernetes_asyncio
import uuid
from kubernetes_utils.helpers import WatchEventType
from kubernetes_utils.kubernetes_client import AbstractEnhancedKubernetesClient
from kubernetes_utils.resources.pods import PodFailedError
from kubernetes_utils.retry import retry_insecure_grpc_unless_pods_have_failed
from resemble.aio.servicers import Serviceable
from resemble.aio.types import RoutableAddress
from resemble.controller.application_config import ApplicationConfig
from resemble.controller.application_deployment import ApplicationDeployment
from resemble.controller.exceptions import InputError
from resemble.controller.settings import (
    ENVVAR_RESEMBLE_CONFIG_SERVER_PORT,
    ENVVAR_RESEMBLE_MODE,
    RESEMBLE_APPLICATION_DEPLOYMENT_NAMESPACE,
    RESEMBLE_MODE_CONFIG,
)
from resemble.controller.spaces import (
    ensure_application_service_account_in_space,
    ensure_namespace_for_space,
)
from resemble.helpers import generate_proto_descriptor_set, maybe_cancel_task
from resemble.naming import get_local_application_id_from_serviceables
from resemble.v1alpha1 import (
    application_config_pb2,
    config_mode_pb2,
    config_mode_pb2_grpc,
)
from respect.logging import get_logger
from typing import Optional

logger = get_logger(__name__)

# This hardcoded server port KUBERNETES_CONFIG_SERVER_PORT is safe because
# it will only ever run on Kubernetes where there is no chance of
# a port conflict due to simultaneous tests.
KUBERNETES_CONFIG_SERVER_PORT = 56653

# The name we will assign to the container running inside the config pod.
CONFIG_CONTAINER_NAME = 'config-server'

# The prefix used for the names of all config pods.
CONFIG_POD_NAME_PREFIX = 'config-pod-'

# The maximum time to wait for the config pod to come up and the maximum
# time to wait after that to connect to the pod.
#
# TODO(rjh, stephanie): use this timeout ONLY for AFTER the pod has been
#                       reported as up. Before that, no timeout, but detect
#                       permanent errors.
CONFIG_POD_TIMEOUT_SECONDS = 30


class LocalConfigExtractor:

    def config_from_serviceables(
        self, serviceables: list[Serviceable]
    ) -> ApplicationConfig:
        file_descriptor_set = generate_proto_descriptor_set(
            routables=serviceables
        )

        return ApplicationConfig.create(
            # Because we're running locally we don't know the
            # application name, and therefore can't compute the usual
            # application ID thus we use a helper to construct a
            # well-known "local" application ID based on the services
            # included in this config.
            application_id=get_local_application_id_from_serviceables(
                serviceables
            ),
            metadata=None,  # We're local, so no (Kubernetes) metadata.
            spec=ApplicationConfig.Spec(
                file_descriptor_set=file_descriptor_set.SerializeToString(),
                container_image_name='local.noop',
                service_names=[s.service_name() for s in serviceables],
            ),
        )


class ConfigPodRunner:
    """
    A class that will run a config pod and return the ApplicationConfig it
    produces.

    Factored out from `KubernetesConfigExtractor` for testing.
    """

    def __init__(self, k8s_client: AbstractEnhancedKubernetesClient):
        self._k8s_client = k8s_client

    async def create_config_pod(
        self,
        namespace: str,
        service_account_name: str,
        pod_name: str,
        container_name: str,
        image: str,
    ) -> RoutableAddress:
        """Create config pod and return the IP address of the config pod."""
        metadata = kubernetes_asyncio.client.V1ObjectMeta(
            namespace=namespace,
            name=pod_name,
        )

        pod = kubernetes_asyncio.client.V1Pod(
            metadata=metadata,
            spec={
                'serviceAccountName':
                    service_account_name,
                'containers':
                    [
                        {
                            'name':
                                container_name,
                            'image':
                                image,
                            'imagePullPolicy':
                                'IfNotPresent',
                            'env':
                                [
                                    {
                                        'name': ENVVAR_RESEMBLE_MODE,
                                        'value': RESEMBLE_MODE_CONFIG
                                    },
                                    {
                                        'name':
                                            ENVVAR_RESEMBLE_CONFIG_SERVER_PORT,
                                        'value':
                                            f'{KUBERNETES_CONFIG_SERVER_PORT}'
                                    },
                                    # Ensure that any Python process
                                    # always produces their output
                                    # immediately. This is helpful for
                                    # debugging purposes.
                                    {
                                        'name': 'PYTHONUNBUFFERED',
                                        'value': '1'
                                    },
                                ],
                        }
                    ]
            }
        )

        logger.info(
            'Creating config pod: (namespace=%s, pod_name=%s, container_name=%s, image=%s)',
            namespace, pod_name, container_name, image
        )

        # TODO: Consider making the ApplicationDeployment the owner of the Pod
        # object for added safety, in case the ApplicationDeployment is deleted
        # while the config pod is running.
        # ISSUE(https://github.com/reboot-dev/respect/issues/1430): Fix
        # ownership.
        await self._k8s_client.pods.create(pod=pod)

        logger.info('Waiting for config pod to come up...')
        try:
            await self._k8s_client.pods.wait_for_running(
                namespace=namespace, name=pod_name
            )
        except PodFailedError as e:
            raise InputError(
                reason='Config pod failed before becoming ready',
                parent_exception=e,
            ) from e

        pods = await self._k8s_client.pods.list_all(namespace=namespace)

        # Return first found ip-address if pod metadata name matches pod name,
        # if no ip address is found, raise an error.
        for ip_address in [
            pod.status.pod_ip for pod in pods if pod.metadata.name == pod_name
        ]:
            return ip_address

        raise InputError(reason='IP address not found for config-pod')

    async def get_application_config(
        self,
        *,
        namespace: str,
        pod_name: str,
        pod_ip: RoutableAddress,
    ) -> application_config_pb2.ApplicationConfig:
        async for retry in retry_insecure_grpc_unless_pods_have_failed(
            # This hardcoded server port KUBERNETES_CONFIG_SERVER_PORT
            # is safe because it will only ever run on Kubernetes
            # where there is no chance of a port conflict due to
            # simultaneous tests.
            f'{pod_ip}:{KUBERNETES_CONFIG_SERVER_PORT}',
            k8s_client=self._k8s_client,
            pods=[(namespace, [pod_name])],
            # TODO(benh): we only catch AioRpcError, but we should
            # also consider catching protobuf decoding errors.
            exceptions=[grpc.aio.AioRpcError],
        ):
            logger.info(
                "Trying to get application config from namespace "
                f"'{namespace}' pod '{pod_name}' ..."
            )
            with retry() as channel:
                config_server_stub = config_mode_pb2_grpc.ConfigStub(channel)

                response = await config_server_stub.Get(
                    config_mode_pb2.GetConfigRequest()
                )

                return response.application_config

    async def delete_config_pod(self, namespace: str, pod_name: str) -> None:
        await self._k8s_client.pods.delete(namespace, pod_name)

    async def delete_all_config_pods(self) -> None:
        logger.info("Deleting existing config pods...")
        config_pods = await self._k8s_client.pods.list_for_name_prefix(
            namespace=None, name_prefix=CONFIG_POD_NAME_PREFIX
        )
        for pod in config_pods:
            await self._k8s_client.pods.delete(
                pod.metadata.namespace, pod.metadata.name
            )
            logger.info(
                f"Deleted config pod {pod.metadata.name} in namespace {pod.metadata.namespace}."
            )


def _get_revision(application_deployment: ApplicationDeployment) -> str:
    # We may expose "revision" as a user-determined setting in the future, but
    # for the time being it is simply the Kubernetes object's resource version.
    return application_deployment.metadata.resource_version


class KubernetesConfigExtractor:

    def __init__(
        self,
        k8s_client: AbstractEnhancedKubernetesClient,
        config_pod_runner: Optional[ConfigPodRunner] = None,
    ):
        self._k8s_client = k8s_client
        self._config_pod_runner = config_pod_runner or ConfigPodRunner(
            k8s_client
        )

        self._update_task_by_application_id: dict[str, asyncio.Task] = {}
        self._need_reconciliation = asyncio.Event()
        # Always do a reconciliation after startup.
        self._need_reconciliation.set()

    async def run(self) -> None:
        # Delete any existing config pods. They are left over from an
        # old controller run and will never be used by this run.
        await self._config_pod_runner.delete_all_config_pods()

        reconcile_task = asyncio.create_task(
            self._reconcile_deployments_and_configs()
        )
        watch_task = asyncio.create_task(
            self._watch_for_application_deployment_objects()
        )
        try:
            await asyncio.gather(reconcile_task, watch_task)
        finally:
            # The fact that we got here is unexpected; we would expect `gather`
            # to run forever. Therefore, we must have encountered an error. We
            # will let the exception propagate to crash the controller, but to
            # be sure that we'll exit as expected we'll first cancel any task
            # that didn't fail yet.
            await maybe_cancel_task(reconcile_task)
            await maybe_cancel_task(watch_task)

    async def _watch_for_application_deployment_objects(self) -> None:
        logger.info(
            "Watching for ApplicationDeployment changes in the "
            f"'{RESEMBLE_APPLICATION_DEPLOYMENT_NAMESPACE}' namespace..."
        )

        # TODO(rjh): it is possible that un-scary events may raise errors here.
        #            We haven't actually seen any such false alarms happen, but
        #            we anticipate that something like a Kubernetes leader
        #            election might cause an exception here. If/when we do see
        #            that, we can add a try/except retry loop here instead of
        #            crashing the controller.
        async for watch_event in self._k8s_client.custom_objects.watch_all(
            object_type=ApplicationDeployment,
            namespace=RESEMBLE_APPLICATION_DEPLOYMENT_NAMESPACE,
        ):

            event_type: WatchEventType = watch_event.type
            logger.info(
                "ApplicationDeployment '%s': '%s'",
                watch_event.object.metadata.name or 'Unknown',
                event_type,
            )

            self._need_reconciliation.set()

        # This is unexpected; we would expect the `watch_all` loop to run
        # forever. Crash the controller, so that it can be restarted by
        # Kubernetes.
        raise RuntimeError(
            'Unexpectedly stopped watching for ApplicationDeployment changes'
        )

    async def _reconcile_deployments_and_configs(self) -> None:
        """
        The reconciliation loop is triggered when there are any changes that may
        prompt a need for reconciliation between ApplicationDeployments and
        ApplicationConfigs.

        Triggers of the reconciliation loop include:
        * Startup.
        * Any changes to ApplicationDeployments.
        * Completed updates (by the reconciliation loop) of ApplicationConfigs.

        Each iteration of the loop will do a full reconciliation, comparing all
        deployments to all configs.

        If any updates of ApplicationConfigs are needed, they are performed in
        parallel. However, each ApplicationConfig can only have one concurrent
        update - this is why each completed update must schedule another round
        of reconciliation: to ensure that any changes that occurred after the
        start of the update are also handled.
        """
        # Note: no try/catch here. Any errors that bubble up to this level are
        #       unexpected and should crash the controller, so that it can be
        #       restarted by Kubernetes.
        #
        # TODO(rjh): as in `_watch_for_application_deployment_objects()`, it is
        #            possible that our calls out to Kubernetes may raise errors
        #            that are temporary in nature and not worth crashing the
        #            controller over. We haven't observed such false alarms
        #            (yet), but when we do we likely want to add a try/except
        #            retry loop here instead of crashing the controller.
        while True:
            logger.debug(
                "Awaiting need for ApplicationDeployment/Config "
                "reconciliation"
            )
            await self._need_reconciliation.wait()
            self._need_reconciliation.clear()
            logger.info("Reconciling ApplicationDeployment/Config now")

            await self._reconcile_deployments_and_configs_once()

    async def _reconcile_deployments_and_configs_once(self) -> None:
        """
        The body of the `_reconcile_deployments_and_configs` loop. See there for
        detailed comments.

        Factored out for testing.
        """
        # TODO(rjh): this method of doing reconciliation, where we list all of
        # the ApplicationDeployments and ApplicationConfigs, is O(existent
        # applications). If we had a more diff-based approach to building these
        # lists we could reduce that to O(changed applications). But that would
        # be more complex to build and test, and we have a long way to go until
        # we hit current scalability limits.

        # Remove any completed update tasks, freeing up slots for subsequent
        # updates on the same objects.
        completed_update_application_ids = [
            application_id for application_id, update_task in
            self._update_task_by_application_id.items() if update_task.done()
        ]
        for application_id in completed_update_application_ids:
            # Await the completed task, so we can discover if it encountered an
            # error. Such an error will be re-thrown by the `await`; we don't
            # catch the error, since we want such an unexpected issue to crash
            # the controller.
            await self._update_task_by_application_id[application_id]
            del self._update_task_by_application_id[application_id]

        # Fetch all ApplicationDeployments and ApplicationConfigs.
        all_deployments = await self._k8s_client.custom_objects.list_all(
            object_type=ApplicationDeployment,
            namespace=RESEMBLE_APPLICATION_DEPLOYMENT_NAMESPACE,
        )
        deployments_by_application_id: dict[str, ApplicationDeployment] = {
            deployment.application_id(): deployment
            for deployment in all_deployments
        }
        all_configs = await self._k8s_client.custom_objects.list_all(
            object_type=ApplicationConfig,
            namespace=None,  # Anywhere in the cluster.
        )
        configs_by_application_id: dict[str, ApplicationConfig] = {
            config.application_id(): config for config in all_configs
        }

        all_application_ids = (
            set(configs_by_application_id.keys()) |
            set(deployments_by_application_id.keys())
        )

        for application_id in all_application_ids:

            # For every `ApplicationConfig` there must be a matching
            # `ApplicationDeployment`. If there isn't, the `ApplicationConfig`
            # must be deleted.
            if (
                application_id in configs_by_application_id and
                application_id not in deployments_by_application_id
            ):
                if application_id in self._update_task_by_application_id:
                    # We could attempt to cancel the ongoing update so we can
                    # immediately perform this new deletion, but making sure
                    # that our logic works in the face of cancellations at
                    # arbitrary moments would be complex. Instead, we'll simply
                    # come back to this deletion when the update is complete -
                    # every update will schedule another reconciliation when it
                    # completes.
                    logger.info(
                        f"Delaying delete of '{application_id}' because there is "
                        "still an update in progress"
                    )
                    continue

                logger.info(
                    f"Will delete orphaned ApplicationConfig '{application_id}'"
                )
                await self._k8s_client.custom_objects.delete(
                    configs_by_application_id[application_id]
                )
                continue

            assert application_id in deployments_by_application_id

            # For every `ApplicationDeployment` there must be a matching
            # `ApplicationConfig`, AND that config must have the same revision as
            # the ApplicationDeployment. If there isn't, we must handle an
            # update.
            deployment = deployments_by_application_id[application_id]
            deployment_revision = _get_revision(deployment)
            needs_update = False
            if application_id not in configs_by_application_id:
                logger.info(
                    "Reconciliation detected missing ApplicationConfig "
                    f"'{application_id}'. Needs creating."
                )
                needs_update = True
            else:
                config = configs_by_application_id[application_id]
                if config.spec.revision != deployment_revision:
                    logger.info(
                        "Reconciliation detected stale ApplicationConfig "
                        f"'{application_id}' (have revision "
                        f"'{config.spec.revision}', want revision "
                        f"'{deployment_revision}'). Needs update."
                    )
                    needs_update = True

            if not needs_update:
                continue

            # To keep things simple we only want to have one update task per
            # application at any given time. If an update is already in progress,
            # don't schedule the next one yet.
            #
            # To ensure we don't miss newer updates while we're still handling older
            # updates, every update task will finish by requesting another round of
            # reconciliation. This will ensure that reconciliation continues until
            # there are no update tasks running AND there is a round of
            # reconciliation that doesn't find any additional updates to handle.
            if application_id in self._update_task_by_application_id:
                logger.info(
                    f"Delaying update of '{application_id}' because there is "
                    "still a prior update in progress"
                )
                continue

            # This application needs an update, so we'll start a task to handle
            # that.
            async def do_update(deployment: ApplicationDeployment):
                try:
                    await self._handle_application_deployment_update(
                        deployment
                    )

                    # Now that the ApplicationConfig has been updated,
                    # trigger another round of reconciliation to detect any
                    # ApplicationDeployment changes that may have come in
                    # during this update.
                    self._need_reconciliation.set()
                except InputError as e:
                    # TODO: Report these errors to the developer who wrote
                    # the `ApplicationDeployment`, e.g. by updating the
                    # `ApplicationDeployment.status` field.
                    logger.error(f"Got user input error: '{e.reason}'")
                except Exception as e:
                    # TODO: Report these errors to the developer who wrote
                    # the `ApplicationDeployment` on a best effort basis,
                    # e.g. by attempting to update the
                    # `ApplicationDeployment.status` field.
                    logger.critical(
                        f"Got unknown error for object '{type(e).__name__}': "
                        f"'{str(e)}'",
                    )
                    raise

            self._update_task_by_application_id[
                application_id] = asyncio.create_task(do_update(deployment))

    async def _handle_application_deployment_update(
        self,
        application_deployment: ApplicationDeployment,
    ) -> None:
        application_id = application_deployment.application_id()

        if application_deployment.spec.space_id == '':
            raise InputError(
                reason="In 'ApplicationDeployment' for application "
                f"'{application_id}': field 'space_id' must not be empty"
            )
        space_id = application_deployment.spec.space_id

        if application_deployment.spec.container_image_name == '':
            raise InputError(
                reason="In 'ApplicationDeployment' with name "
                f"'{application_id}': field 'container_image_name' must not be "
                "empty"
            )

        deployment_revision = _get_revision(application_deployment)
        logger.info(
            f"Will create or update ApplicationConfig '{application_id}' at/to "
            f"revision '{deployment_revision}'"
        )

        # The appropriate Kubernetes namespace to run the config pod in is based
        # on the application's space ID.
        #
        # Create the Kubernetes namespace if it doesn't exist yet.
        space_namespace = await ensure_namespace_for_space(
            k8s_client=self._k8s_client,
            space_id=space_id,
        )
        service_account_name = await ensure_application_service_account_in_space(
            k8s_client=self._k8s_client,
            space_id=space_id,
            application_id=application_id,
        )

        # Come up with a unique name for the config pod. Having a unique name is
        # important, since even if we handle just one ApplicationDeployment at a
        # time it is possible for an old config pod to still be in state
        # `Terminating`when we want to create the next one.
        config_pod_name = f'{CONFIG_POD_NAME_PREFIX}{uuid.uuid4()}'
        logger.info(
            'Creating config pod %s for %s',
            config_pod_name,
            application_id,
        )

        try:
            config_pod_ip = await self._config_pod_runner.create_config_pod(
                namespace=space_namespace,
                service_account_name=service_account_name,
                pod_name=config_pod_name,
                container_name=CONFIG_CONTAINER_NAME,
                image=application_deployment.spec.container_image_name,
            )

            application_config_proto = await asyncio.wait_for(
                self._config_pod_runner.get_application_config(
                    namespace=space_namespace,
                    pod_name=config_pod_name,
                    pod_ip=config_pod_ip,
                ),
                timeout=CONFIG_POD_TIMEOUT_SECONDS
            )

            application_config = ApplicationConfig.from_proto(
                metadata=kubernetes_asyncio.client.V1ObjectMeta(
                    namespace=space_namespace,
                    name=application_id,
                ),
                proto=application_config_proto,
            )

            # The ApplicationConfig we get back from the config pod is
            # incomplete. Fill in the blanks.
            application_config.spec.container_image_name = application_deployment.spec.container_image_name
            application_config.spec.revision = deployment_revision

            await self._k8s_client.custom_objects.create_or_update(
                application_config
            )
            logger.info(
                f"Created/updated ApplicationConfig '{application_id}' at revision "
                f"'{application_config.spec.revision}'"
            )
        except asyncio.exceptions.TimeoutError as e:
            raise InputError(
                reason='Timed out fetching application config from config pod',
                parent_exception=e,
            ) from e

        finally:
            await self._config_pod_runner.delete_config_pod(
                space_namespace, config_pod_name
            )

            logger.debug(
                f"Deleted config pod '{config_pod_name}' for "
                f"'{application_deployment.application_id()}'. Be aware, it may "
                "still be in state `Terminating`."
            )
