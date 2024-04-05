import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from google.protobuf.message import Message
from resemble.aio.types import ActorId, GrpcMetadata, ServiceName
from typing import Iterator, Optional, overload


class Idempotency:
    """Describes how to perform a mutation idempotently, either by using a
    human readable alias, e.g., 'Charge credit card', and letting the
    system generate a key, or by explicitly providing the key.
    """

    @overload
    def __init__(self, *, alias: str):
        ...

    @overload
    def __init__(self, *, key: str):
        ...

    def __init__(
        self,
        *,
        alias: Optional[str] = None,
        key: Optional[str] = None,
    ):
        """Constructs an idempotency instance. Only one of 'alias' or 'key'
        should be specified.

        :param alias: human readable alias, e.g., 'Charge credit
        card', that _must_ be unique within the lifetime of the
        current 'Context' or 'Workflow'.

        :param key: idempotency key, e.g., stringified version of a
        UUID.
        """
        if (
            (alias is None and key is None) or
            (alias is not None and key is not None)
        ):
            raise ValueError(
                "Exactly one of 'alias' or 'key' should be specified"
            )
        self._alias = alias
        self._key = key

    @property
    def alias(self) -> Optional[str]:
        """Returns the alias or None."""
        return self._alias

    @property
    def key(self) -> Optional[str]:
        """Returns the key or None."""
        return self._key


class IdempotencyManager:

    @dataclass(kw_only=True)
    class Status:
        # Identifiers of the mutation being performed.
        service: ServiceName
        actor_id: ActorId
        method: str

        # Request of the mutation being performed.
        request: Message

        # Serialized request of the mutation being performed
        # (optionally, lazily computed in the event it is never
        # necessary so we don't always pay for serialization).
        serialized_request: Optional[bytes]

        # Metadata of the mutation being performed.
        metadata: Optional[GrpcMetadata]

    # Map from alias to a generated UUID for an idempotency key.
    _aliases: dict[str, uuid.UUID]

    # Map from idempotency key to its status.
    _statuses: dict[str, Status]

    # We need to track whether or not any RPCs without idempotency
    # have been made so that we know whether or not to toggle
    # uncertainty if a mutation fails. Not that the mutation that
    # fails might in fact be an idempotent mutation, but attempting to
    # perform a mutation without idempotency _after_ a mutation has
    # failed may be due to a user doing a manual retry which may cause
    # an additional undesired mutation.
    _rpcs_without_idempotency: bool

    # Whether or not a mutation's success or failure is uncertain.
    _uncertain_mutation: bool

    # The service, actor_id, and method of the mutation that is uncertain.
    _uncertain_mutation_service: Optional[ServiceName]
    _uncertain_mutation_actor_id: Optional[ActorId]
    _uncertain_mutation_method: Optional[str]

    def __init__(self):
        self._aliases = {}
        self._statuses = {}
        self._rpcs_without_idempotency = False
        self._uncertain_mutation = False
        self._uncertain_mutation_service = None
        self._uncertain_mutation_actor_id = None
        self._uncertain_mutation_method = None

    @contextmanager
    def idempotently(
        self,
        *,
        service: ServiceName,
        actor_id: ActorId,
        method: str,
        request: Message,
        metadata: Optional[GrpcMetadata],
        idempotency: Optional[Idempotency],
    ) -> Iterator[Optional[str]]:
        """Ensures that either all mutations are performed idempotently or
        raises in the face of uncertainty about a mutation to avoid a
        possible undesired mutation."""
        if idempotency is None:
            self._rpcs_without_idempotency = True

        if self._uncertain_mutation:
            raise RuntimeError(
                "Because we don't know if the mutation from calling "
                f"'{self._uncertain_mutation_service}.{self._uncertain_mutation_method}' "
                f"of actor '{self._uncertain_mutation_actor_id}' failed or "
                "succeeded AND you've made some NON-IDEMPOTENT RPCs we can't "
                "reliably determine whether or not the call to "
                f"'{service}.{method}' of actor '{actor_id}' is due to a retry "
                "which may cause an undesired mutation -- if you are trying to "
                "write your own manual retry logic you should ensure you're "
                "always passing 'Idempotency' to your mutations"
            )

        try:
            if idempotency is not None:
                yield self._idempotency_key_from(
                    service=service,
                    actor_id=actor_id,
                    method=method,
                    request=request,
                    metadata=metadata,
                    idempotency=idempotency,
                )
            else:
                yield None
        # TODO(benh): differentiate errors so that we only set
        # uncertainty when we are truly uncertain.
        except:
            # The `yield` threw an exception, which means the user
            # code that we're wrapping (an RPC to a mutation on
            # `service`) failed. We're uncertain whether that mutation
            # succeeded or failed (there are many ways exceptions can
            # get thrown, and not all errors can be clear on whether
            # the RPC has definitively failed on the server).
            #
            # We want to set uncertainty regardless of whether or not
            # _this_ call has an idempotency key because a user might
            # manually _retry_ another call that did not have an
            # idempotency key and accidentally perform a mutation more
            # than once.
            if self._rpcs_without_idempotency:
                assert not self._uncertain_mutation
                self._uncertain_mutation = True
                self._uncertain_mutation_service = service
                self._uncertain_mutation_actor_id = actor_id
                self._uncertain_mutation_method = method
            raise

    def acknowledge_idempotency_uncertainty(self):
        assert self._uncertain_mutation
        self._uncertain_mutation = False
        self._uncertain_mutation_service = None
        self._uncertain_mutation_actor_id = None
        self._uncertain_mutation_method = None

    def _idempotency_key_from(
        self,
        *,
        service: ServiceName,
        actor_id: ActorId,
        method: str,
        request: Message,
        metadata: Optional[GrpcMetadata],
        idempotency: Idempotency,
    ) -> str:
        idempotency_key = self._get_or_create_idempotency_key(idempotency)

        if idempotency_key not in self._statuses:
            self._statuses[idempotency_key] = IdempotencyManager.Status(
                service=service,
                actor_id=actor_id,
                method=method,
                request=request,
                serialized_request=None,
                metadata=metadata,
            )
            return idempotency_key

        status = self._statuses[idempotency_key]

        if (
            status.service != service or status.actor_id != actor_id or
            status.method != method
        ):
            raise ValueError(
                f"Idempotency key for a call to '{service}.{method}' of actor "
                f"'{actor_id}' is being reused _unsafely_; you can "
                "not reuse an idempotency key that was previously used for a "
                f"call to '{status.service}.{status.method}' of actor "
                f"'{status.actor_id}'"
            )

        if status.serialized_request is None:
            status.serialized_request = status.request.SerializeToString(
                deterministic=True,
            )

        if status.serialized_request != request.SerializeToString(
            deterministic=True,
        ):
            raise ValueError(
                f"Idempotency key for a call to '{service}.{method}' of actor "
                f"'{actor_id}' is being reused _unsafely_; you can not reuse "
                "an idempotency key with a different request"
            )

        if status.metadata != metadata:
            raise ValueError(
                f"Idempotency key for a call to '{service}.{method}' of actor "
                f"'{actor_id}' is being reused _unsafely_; you can not reuse "
                "an idempotency key with different metadata"
            )

        return idempotency_key

    def _get_or_create_idempotency_key(
        self,
        idempotency: Idempotency,
    ) -> str:
        if idempotency.key is not None:
            return idempotency.key

        alias = idempotency.alias
        assert alias is not None

        if alias not in self._aliases:
            self._aliases[alias] = uuid.uuid4()

        return str(self._aliases[alias])
