from __future__ import annotations

import grpc
import uuid
from dataclasses import dataclass
from datetime import datetime
from resemble.aio.internals.contextvars import get_application_id
from resemble.aio.types import (
    ActorId,
    ApplicationId,
    GrpcMetadata,
    ServiceName,
)
from typing import Any, Callable, Optional

# This code ties in with the concept of a Context. There are a lot of open
# questions about what information is carried on a context and how it is
# represented and transmitted. We believe that the Context need to contain
# information about the full call DAG, but it is currently unclear how this
# information should be encoded. Similarly, it is unclear how this information
# should be transmitted. We believe that gRPC metadata is the correct way of
# transmitting this data but the encoding of the DAG into gRPC metadata is not
# well understood.
#
# From the full call DAG information, it should be possible to obtain various
# information that is needed by the Context, such as the current safety level,
# the actor that is currently being served, etc. Until we have a better idea for
# how we are a) representing these and b) encoding them into metadata headers,
# we are "cherry picking" the necessary DAG information and sticking it on
# individual headers.
#
# This small library is intended as an abstraction layer to provide the ability
# to encode and decode DAG information as grpc headers without having to care
# too much about the current implementation.

# If ever these header constants change, also update their invariant
# counterparts in tests/local_envoy_config.yaml.j2.
#
# The header that tells us what application we're targeting.
APPLICATION_ID_HEADER = 'x-resemble-application-id'
# The header that tells us what service we're targeting.
SERVICE_NAME_HEADER = 'x-resemble-service-name'
# The header that carries actor id information.
ACTOR_ID_HEADER = 'x-resemble-actor-id'
# The header that carries information about which consensus this request should
# be handled by.
CONSENSUS_ID_HEADER = 'x-resemble-consensus-id'

# Transaction related headers.
TRANSACTION_ID_HEADER = 'x-resemble-transaction-id'
TRANSACTION_COORDINATOR_SERVICE_HEADER = 'x-resemble-transaction-coordinator-service'
TRANSACTION_COORDINATOR_ACTOR_ID_HEADER = 'x-resemble-transaction-coordinator-actor-id'
TRANSACTION_PARTICIPANTS_HEADER = 'x-resemble-transaction-participants'

# The header that carries the idempotency key for a mutation.
#
# TODO(benh): investigate using the proposed 'Idempotency-Key' header
# instead:
# https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header
IDEMPOTENCY_KEY_HEADER = 'x-resemble-idempotency-key'

AUTHORIZATION_HEADER = 'authorization'

# Headers for calling/scheduling tasks directly.
TASK_SCHEDULE = 'x-resemble-task-schedule'

# Metadata that's only used in a _trailing_ capacity (never passed in
# a request and thus we don't try and extract it).
TASK_ID_UUID = 'x-resemble-task-id-uuid'


@dataclass(kw_only=True, frozen=True)
class Headers:
    """Dataclass for working with resemble metadata headers.
    """
    # NOTE: in tests when using a `Workflow` we might not know our
    # application ID and thus this is optional. That being said, when
    # we receive an RPC we always fill in the application ID based on
    # the asyncio context variable that has been set, and thus we know
    # that we always have an application ID when we have a `Context`.
    application_id: Optional[ApplicationId]
    service_name: ServiceName
    actor_id: ActorId
    transaction_id: Optional[uuid.UUID] = None
    transaction_coordinator_service: Optional[str] = None
    transaction_coordinator_actor_id: Optional[str] = None

    idempotency_key: Optional[uuid.UUID] = None

    bearer_token: Optional[str] = None

    task_schedule: Optional[datetime] = None

    def __post_init__(self):
        # We're supposed to check the validity of the header values earlier, so
        # that the user-facing stack trace is shorter, but it's possible that we
        # miss a call path. If so, this set of checks is the backstop.
        ascii_required_fields = [
            ('actor_id', self.actor_id),
            (
                'transaction_coordinator_actor_id',
                self.transaction_coordinator_actor_id
            ),
            ('bearer_token', self.bearer_token),
        ]
        for field_name, value in ascii_required_fields:
            if value is not None and not value.isascii():
                raise ValueError(
                    f"Field '{field_name}' must be ASCII; given value "
                    f"'{value}' is not ASCII"
                )

    def copy_for_token_verification_and_authorization(self):
        """Returns a copy of the headers that is suitable for use when doing
        token verification or authorization.

        In particular, we drop anything related to transactions (as we
        don't want to include token verification or authorization as
        part of the transaction), the idempotency key, and the bearer
        token (it will be passed explicitly to the token verifier and
        if valid will also be passed via `context.auth` to the
        authorizer).
        """
        return Headers(
            application_id=self.application_id,
            service_name=self.service_name,
            actor_id=self.actor_id,
        )

    @classmethod
    def from_grpc_context(
        cls,
        grpc_context: grpc.aio.ServicerContext,
    ) -> Headers:
        """Convert and parse gRPC metadata to `Headers`."""
        # Extract the raw gRPC metadata from gRPC context to dictionary.
        raw_headers = dict(grpc_context.invocation_metadata())

        def extract_maybe(
            name: str,
            *,
            required=False,
            convert: Callable[[str], Any] = lambda value: value
        ) -> Optional[Any]:
            try:
                return convert(raw_headers[name])
            except KeyError as e:
                if required:
                    raise ValueError(f"gRPC metadata missing '{name}'") from e
                else:
                    return None

        def extract(
            name: str,
            *,
            convert: Callable[[str], Any] = lambda value: value
        ) -> Any:
            return extract_maybe(name, required=True, convert=convert)

        # For now, we always use the application ID provided in the
        # asyncio context variable because in tests when using a
        # `Workflow` we don't always know the application ID (e.g.,
        # because we've done `rsm.up(...)` more than once but aren't
        # passing a `gateway` to `Workflow`).
        #
        # NOTE: the asyncio context variable gets set via the
        # `UseApplicationIdInterceptor` which is added to every
        # server. If we have a `grpc_context`, then we must have been
        # called through a gRPC server, with which we injected the
        # interceptor.
        application_id = get_application_id()
        assert application_id is not None

        service_name = extract(SERVICE_NAME_HEADER)
        actor_id = extract(ACTOR_ID_HEADER)

        transaction_id: Optional[uuid.UUID] = extract_maybe(
            TRANSACTION_ID_HEADER,
            convert=lambda value: uuid.UUID(value),
        )

        transaction_coordinator_service: Optional[str] = extract_maybe(
            TRANSACTION_COORDINATOR_SERVICE_HEADER,
            required=transaction_id is not None
        )

        transaction_coordinator_actor_id: Optional[str] = extract_maybe(
            TRANSACTION_COORDINATOR_ACTOR_ID_HEADER,
            required=transaction_id is not None
        )

        idempotency_key: Optional[uuid.UUID] = extract_maybe(
            IDEMPOTENCY_KEY_HEADER,
            convert=lambda value: uuid.UUID(value),
        )

        bearer_token: Optional[str] = extract_maybe(
            AUTHORIZATION_HEADER,
            convert=lambda value: value.removeprefix('Bearer '),
        )

        task_schedule: Optional[datetime] = extract_maybe(
            TASK_SCHEDULE,
            convert=lambda value: datetime.fromisoformat(value),
        )

        return cls(
            application_id=application_id,
            service_name=service_name,
            actor_id=actor_id,
            transaction_id=transaction_id,
            transaction_coordinator_service=transaction_coordinator_service,
            transaction_coordinator_actor_id=transaction_coordinator_actor_id,
            idempotency_key=idempotency_key,
            bearer_token=bearer_token,
            task_schedule=task_schedule,
        )

    def to_grpc_metadata(self) -> GrpcMetadata:
        """Encode these headers as gRPC metadata."""

        def maybe_add_application_id_header() -> GrpcMetadata | tuple[()]:
            if self.application_id is not None:
                return ((APPLICATION_ID_HEADER, self.application_id),)
            return ()

        def maybe_add_authorization_header() -> GrpcMetadata | tuple[()]:
            if self.bearer_token is not None:
                return (
                    (AUTHORIZATION_HEADER, f'Bearer {self.bearer_token}'),
                )
            return ()

        def maybe_add_transaction_headers() -> GrpcMetadata | tuple[()]:
            if self.transaction_id is not None:
                assert self.transaction_coordinator_service is not None
                assert self.transaction_coordinator_actor_id is not None
                return (
                    (TRANSACTION_ID_HEADER, str(self.transaction_id)),
                    (
                        TRANSACTION_COORDINATOR_SERVICE_HEADER,
                        self.transaction_coordinator_service
                    ),
                    (
                        TRANSACTION_COORDINATOR_ACTOR_ID_HEADER,
                        self.transaction_coordinator_actor_id
                    ),
                )
            return ()

        return (
            (
                (SERVICE_NAME_HEADER, self.service_name),
                (ACTOR_ID_HEADER, self.actor_id),
            ) + maybe_add_application_id_header() +
            maybe_add_authorization_header() + maybe_add_transaction_headers()
        )
