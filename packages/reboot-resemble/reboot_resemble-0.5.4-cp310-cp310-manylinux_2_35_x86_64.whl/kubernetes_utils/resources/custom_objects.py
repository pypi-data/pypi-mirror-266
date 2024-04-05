import kubernetes_asyncio
from kubernetes_utils.api import KubernetesAPIs
from kubernetes_utils.custom_object import CustomObject, CustomObjectT
from kubernetes_utils.helpers import WatchEvent, WatchEventType, wait_for_state
from respect.logging import LoggerMixin
from typing import AsyncGenerator, Optional


class AbstractCustomObjects:

    async def create(self, obj: CustomObject) -> None:
        """Create namespaced custom object."""
        raise NotImplementedError

    async def create_or_update(self, obj: CustomObject) -> None:
        """Create namespaced custom object if it doesn't exist, or update it
        in-place if it does exist."""
        raise NotImplementedError

    async def replace(self, obj: CustomObject):
        """Replace namespaced custom object. It must already exist, and the
        `body.metadata.resource_version` must match exactly what would
        be returned by a `get()` for this object. This ensures a hermetic
        replacement, without a chance of any intermediate updates being
        overwritten.
        """
        raise NotImplementedError

    async def get_by_name(
        self, *, namespace: str, name: str, object_type: type[CustomObjectT]
    ) -> CustomObjectT:
        """Get namespaced custom object."""
        raise NotImplementedError

    # Named `list_all` instead of `list` to not conflict with the built-in
    # Python keyword.
    async def list_all(
        self,
        *,
        object_type: type[CustomObjectT],
        namespace: Optional[str] = None
    ) -> list[CustomObjectT]:
        """list namespaced custom objects."""
        raise NotImplementedError

    async def delete(self, obj: CustomObjectT) -> None:
        """Delete namespaced custom object."""
        raise NotImplementedError

    async def delete_by_name(
        self,
        *,
        namespace: str,
        name: str,
        object_type: type[CustomObjectT],
    ) -> None:
        """Delete namespaced custom object by name."""
        raise NotImplementedError

    async def wait_for_applied(
        self,
        *,
        obj: CustomObject,
    ) -> None:
        """Wait for an instance of the given custom resource type to be
        applied."""
        raise NotImplementedError

    async def watch_by_name(
        self,
        *,
        namespace: str,
        name: str,
        object_type: type[CustomObjectT],
    ) -> AsyncGenerator[WatchEvent[CustomObjectT], None]:
        """Start a long-lived watch for one specific custom object."""
        if False:
            # This is here to show mypy that the _actual_ return type of this
            # method matches the declared return type: it's a generator.
            yield
        raise NotImplementedError

    async def watch_all(
        self,
        *,
        object_type: type[CustomObjectT],
        namespace: Optional[str] = None,
    ) -> AsyncGenerator[WatchEvent[CustomObjectT], None]:
        """Start a long-lived watch for all instances of the given custom
        resource type.

        If `namespace` is not `None`, only watches for objects in the given
        namespace. Otherwise, watches for objects in all namespaces.
        """
        if False:
            # This is here to show mypy that the _actual_ return type of this
            # method matches the declared return type: it's a generator.
            yield
        raise NotImplementedError


class CustomObjects(LoggerMixin, AbstractCustomObjects):
    """An implementation of `AbstractCustomObjects` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def create(self, obj: CustomObject) -> None:

        async def retryable_create_custom_object():
            await self._apis.custom_objects.create_namespaced_custom_object(
                namespace=obj.metadata.namespace,
                group=obj.group,
                version=obj.version,
                plural=obj.get_plural(),
                body=obj.to_dict()
            )

        await self._apis.retry_api_call(retryable_create_custom_object)

    async def create_or_update(self, obj: CustomObject) -> None:
        try:
            old_obj = await self.get_by_name(
                namespace=obj.metadata.namespace,
                name=obj.metadata.name,
                object_type=type(obj),
            )
            # If the above didn't throw an exception the object exists, so
            # update it.
            obj.metadata.resource_version = old_obj.metadata.resource_version
            await self.replace(obj)

        except kubernetes_asyncio.client.exceptions.ApiException as e:
            if e.status == 404:
                # The object doesn't exist, so create it.
                await self.create(obj)
                return
            else:
                raise e

    async def replace(self, obj: CustomObject):

        async def retryable_replace_custom_object():
            response = await self._apis.custom_objects.replace_namespaced_custom_object(
                namespace=obj.metadata.namespace,
                name=obj.metadata.name,
                group=obj.group,
                version=obj.version,
                plural=obj.get_plural(),
                body=obj.to_dict(),
            )
            return response

        return await self._apis.retry_api_call(retryable_replace_custom_object)

    async def get_by_name(
        self,
        *,
        namespace: str,
        name: str,
        object_type: type[CustomObjectT],
    ) -> CustomObjectT:

        async def retryable_get_custom_object():
            response = await self._apis.custom_objects.get_namespaced_custom_object(
                namespace=namespace,
                name=name,
                group=object_type.group,
                version=object_type.version,
                plural=object_type.get_plural(),
            )
            return response

        return await object_type.from_dict_with_metadata(
            await self._apis.retry_api_call(retryable_get_custom_object)
        )

    # Named `list_all` instead of `list` to not conflict with the built-in
    # Python keyword.
    async def list_all(
        self,
        *,
        object_type: type[CustomObjectT],
        namespace: Optional[str] = None,
    ) -> list[CustomObjectT]:

        async def retryable_list_custom_object():
            if namespace is None:
                response = await self._apis.custom_objects.list_cluster_custom_object(
                    group=object_type.group,
                    version=object_type.version,
                    plural=object_type.get_plural(),
                )

            else:
                response = await self._apis.custom_objects.list_namespaced_custom_object(
                    namespace=namespace,
                    group=object_type.group,
                    version=object_type.version,
                    plural=object_type.get_plural(),
                )

            return response['items']

        return [
            (await object_type.from_dict_with_metadata(item)) for item in
            (await self._apis.retry_api_call(retryable_list_custom_object))
        ]

    async def watch_by_name(
        self,
        *,
        namespace: str,
        name: str,
        object_type: type[CustomObjectT],
    ) -> AsyncGenerator[WatchEvent[CustomObjectT], None]:
        w = kubernetes_asyncio.watch.Watch()
        async with w.stream(
            # Seemingly the most logical method for us to stream would be
            # `get_namespaced_custom_object`, but that doesn't have the ability
            # to be streamed. Instead we use `list_namespaced_custom_object`,
            # and set the `field_selector` to only return the object we want.
            self._apis.custom_objects.list_namespaced_custom_object,
            namespace=namespace,
            group=object_type.group,
            version=object_type.version,
            plural=object_type.get_plural(),
            field_selector=f'metadata.name={name}'
        ) as event_stream:
            async for event in event_stream:
                yield WatchEvent(
                    type=WatchEventType(event['type']),
                    object=(
                        await
                        object_type.from_dict_with_metadata(event['object'])
                    ),
                )
        raise ValueError('Unexpectedly reached the end of a watch stream')

    async def watch_all(
        self,
        *,
        object_type: type[CustomObjectT],
        namespace: Optional[str] = None,
    ) -> AsyncGenerator[WatchEvent[CustomObjectT], None]:

        try:
            w = kubernetes_asyncio.watch.Watch()

            # Depending on whether we are watching a specific namespace or any
            # namespace, we must setup our watcher differently.
            if namespace is None:
                # Watch for object in the cluster.
                event_provider = w.stream(
                    self._apis.custom_objects.list_cluster_custom_object,
                    group=object_type.group,
                    version=object_type.version,
                    plural=object_type.get_plural(),
                )
            else:
                # Watch for object in namespace.
                event_provider = w.stream(
                    self._apis.custom_objects.list_namespaced_custom_object,
                    namespace=namespace,
                    group=object_type.group,
                    version=object_type.version,
                    plural=object_type.get_plural(),
                )

            async with event_provider as event_stream:
                async for event in event_stream:
                    yield WatchEvent[CustomObjectT](
                        type=WatchEventType(event['type']),
                        object=(
                            await object_type.from_dict_with_metadata(
                                event['object']
                            )
                        ),
                    )

        except kubernetes_asyncio.client.exceptions.ApiException as e:
            self.logger.error(
                f'Kubernetes API exception raised ({e}); '
                'did you apply your custom resource definition ('
                f'{object_type.get_plural()}) before starting the watch?'
            )
            raise e

    async def delete(self, obj: CustomObjectT) -> None:
        await self.delete_by_name(
            namespace=obj.metadata.namespace,
            name=obj.metadata.name,
            object_type=type(obj),
        )

    async def delete_by_name(
        self,
        *,
        namespace: str,
        name: str,
        object_type: type[CustomObjectT],
    ) -> None:

        async def retryable_delete_object():
            try:
                await self._apis.custom_objects.delete_namespaced_custom_object(
                    namespace=namespace,
                    name=name,
                    group=object_type.group,
                    version=object_type.version,
                    plural=object_type.get_plural(),
                    grace_period_seconds=0
                )
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.status == 404:
                    # The object doesn't exist, so we don't need to delete it.
                    pass
                else:
                    raise e

        await self._apis.retry_api_call(retryable_delete_object)

    async def wait_for_applied(
        self,
        *,
        obj: CustomObject,
    ) -> None:

        async def check_for_custom_object_applied():
            await self._apis.custom_objects.get_namespaced_custom_object(
                namespace=obj.metadata.namespace,
                name=obj.metadata.name,
                group=obj.group,
                version=obj.version,
                plural=obj.get_plural(),
            )
            return True

        await wait_for_state(
            check_for_custom_object_applied,
            kubernetes_asyncio.client.exceptions.ApiException
        )
