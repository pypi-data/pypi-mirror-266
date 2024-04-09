import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from pathlib import Path
from resemble.aio.workflows import Workflow
from resemble.cloud.client import client
from resemble.naming import UserId
from resemble.settings import (
    ENVVAR_RSM_CLOUD_API_KEY,
    ENVVAR_RSM_CLOUD_GATEWAY_ADDRESS,
    ENVVAR_RSM_CLOUD_GATEWAY_SECURE_CHANNEL,
    ENVVAR_RSM_DEV_SECRETS_DIRECTORY,
)
from typing import ClassVar, Optional


class SecretSource(ABC):

    @abstractmethod
    async def get(self, secret_name: str) -> bytes:
        pass


class Secrets:
    """Provides Resemble applications access to secrets that have been stored via `rsm secret`."""

    _static_secret_source: ClassVar[Optional[SecretSource]] = None

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        workflow: Optional[Workflow] = None
    ):
        super().__init__()

        self._secret_cache: dict[str, _CachedSecret] = dict()
        self._secret_source: SecretSource

        if Secrets._static_secret_source is not None:
            self._secret_source = Secrets._static_secret_source
            return
        dev_secrets_directory = os.environ.get(
            ENVVAR_RSM_DEV_SECRETS_DIRECTORY
        )
        if dev_secrets_directory is not None:
            self._secret_source = DirectorySecretSource(
                Path(dev_secrets_directory)
            )
            return

        # These environment variables are injected by `rsm dev run`, and
        # eventually the controller.
        api_key = api_key or os.environ.get(ENVVAR_RSM_CLOUD_API_KEY, "")

        if not api_key:
            raise Exception(
                "No Cloud API key was set. "
                "To enable Secrets access in a dev environment, please pass "
                "your API key using the `--api-key` flag."
            )

        if workflow is None:
            gateway = os.environ[ENVVAR_RSM_CLOUD_GATEWAY_ADDRESS]
            secure_channel = os.environ[ENVVAR_RSM_CLOUD_GATEWAY_SECURE_CHANNEL
                                       ].lower() == "true"
            workflow = Workflow(
                name="resemble-secrets-client",
                bearer_token=api_key,
                gateway=gateway,
                secure_channel=secure_channel,
            )

        self._secret_source = _CloudSecretSource(workflow, api_key=api_key)

    @classmethod
    def set_secret_source(cls, secret_source: SecretSource) -> None:
        """Allows for overriding the default source of secrets, such as in unit tests.

        After a call to this method, all constructed `Secrets` instances will use the
        given SecretSource, rather than accessing the Resemble Cloud.
        """
        cls._static_secret_source = secret_source

    async def get(self, secret_name: str, *, ttl_secs: float = 15.0) -> bytes:
        """Get the secret value that has been stored for the given secret_name.

        If less than `ttl_secs` has elapsed since the last request for a secret, a cached value
        may be returned to reduce traffic to the underlying source of secrets. Because the number
        of secrets per application is expected to be static, the internal cache does not support
        eviction.

        Raises `SecretNotFoundException` if there is no secret with the given name.
        """
        # TODO: Should eventually allow for watching the secret value without polling.
        now = time.time()
        cached_secret = self._secret_cache.get(secret_name)
        if cached_secret and cached_secret.cached_at + ttl_secs > now:
            return cached_secret.value

        value = await self._secret_source.get(secret_name)

        # TODO: It is possible for multiple threads to race to put a value in the cache.
        self._secret_cache[secret_name] = _CachedSecret(value, cached_at=now)
        return value

    def adjust_entry_age_for_tests(
        self, secret_name: str, *, age_delta: float
    ) -> None:
        entry = self._secret_cache[secret_name]
        self._secret_cache[secret_name] = replace(
            entry, cached_at=entry.cached_at + age_delta
        )


class SecretNotFoundException(Exception):
    pass


@dataclass(frozen=True)
class DirectorySecretSource(SecretSource):
    directory: Path

    async def get(self, secret_name: str) -> bytes:
        path = self.directory / secret_name
        if not path.exists():
            raise SecretNotFoundException(
                f"No secret is stored for {secret_name=} (at `{path}`)."
            )
        return path.read_bytes()


@dataclass(frozen=True)
class MockSecretSource(SecretSource):
    secrets: dict[str, bytes]

    async def get(self, secret_name: str) -> bytes:
        value = self.secrets.get(secret_name)
        if value is None:
            raise SecretNotFoundException(
                f"No mock secret was stored for {secret_name=}."
            )
        return value


@dataclass
class _CloudSecretSource(SecretSource):
    workflow: Workflow
    api_key: str
    user_id: Optional[UserId] = None

    async def get(self, secret_name: str) -> bytes:
        if self.user_id is None:
            self.user_id = await client.user_id(self.workflow, self.api_key)
        value = await client.secret_read(
            self.workflow, self.user_id, secret_name
        )
        if value is None:
            # TODO: This should render the space name too, when we have one.
            raise SecretNotFoundException(
                f"No secret is stored for {secret_name=}."
            )
        return value


@dataclass(frozen=True)
class _CachedSecret:
    value: bytes
    cached_at: float
