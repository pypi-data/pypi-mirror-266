from __future__ import annotations

import grpc
import resemble.v1alpha1.errors_pb2
from google.protobuf import any_pb2, text_format
from google.protobuf.message import Message
from google.rpc import code_pb2, status_pb2
from resemble.aio.types import assert_type
from typing import Optional, TypeAlias, TypeVar, Union

# Type aliases of possible errors.
GrpcError: TypeAlias = Union[
    resemble.v1alpha1.errors_pb2.Cancelled,
    resemble.v1alpha1.errors_pb2.Unknown,
    resemble.v1alpha1.errors_pb2.InvalidArgument,
    resemble.v1alpha1.errors_pb2.DeadlineExceeded,
    resemble.v1alpha1.errors_pb2.NotFound,
    resemble.v1alpha1.errors_pb2.AlreadyExists,
    resemble.v1alpha1.errors_pb2.PermissionDenied,
    resemble.v1alpha1.errors_pb2.ResourceExhausted,
    resemble.v1alpha1.errors_pb2.FailedPrecondition,
    resemble.v1alpha1.errors_pb2.Aborted,
    resemble.v1alpha1.errors_pb2.OutOfRange,
    resemble.v1alpha1.errors_pb2.Unimplemented,
    resemble.v1alpha1.errors_pb2.Internal,
    resemble.v1alpha1.errors_pb2.Unavailable,
    resemble.v1alpha1.errors_pb2.DataLoss,
    resemble.v1alpha1.errors_pb2.Unauthenticated,
]

ResembleError: TypeAlias = Union[
    resemble.v1alpha1.errors_pb2.ActorAlreadyConstructed,
    resemble.v1alpha1.errors_pb2.ActorNotConstructed,
    resemble.v1alpha1.errors_pb2.TransactionParticipantFailedToPrepare,
    resemble.v1alpha1.errors_pb2.TransactionParticipantFailedToCommit,
    resemble.v1alpha1.errors_pb2.UnknownService,
    resemble.v1alpha1.errors_pb2.UnknownTask,
    resemble.v1alpha1.errors_pb2.InvalidMethod,
]

GRPC_ERROR_TYPES: list[type[GrpcError]] = [
    resemble.v1alpha1.errors_pb2.Cancelled,
    resemble.v1alpha1.errors_pb2.Unknown,
    resemble.v1alpha1.errors_pb2.InvalidArgument,
    resemble.v1alpha1.errors_pb2.DeadlineExceeded,
    resemble.v1alpha1.errors_pb2.NotFound,
    resemble.v1alpha1.errors_pb2.AlreadyExists,
    resemble.v1alpha1.errors_pb2.PermissionDenied,
    resemble.v1alpha1.errors_pb2.ResourceExhausted,
    resemble.v1alpha1.errors_pb2.FailedPrecondition,
    resemble.v1alpha1.errors_pb2.Aborted,
    resemble.v1alpha1.errors_pb2.OutOfRange,
    resemble.v1alpha1.errors_pb2.Unimplemented,
    resemble.v1alpha1.errors_pb2.Internal,
    resemble.v1alpha1.errors_pb2.Unavailable,
    resemble.v1alpha1.errors_pb2.DataLoss,
    resemble.v1alpha1.errors_pb2.Unauthenticated,
]

RESEMBLE_ERROR_TYPES: list[type[ResembleError]] = [
    resemble.v1alpha1.errors_pb2.ActorAlreadyConstructed,
    resemble.v1alpha1.errors_pb2.ActorNotConstructed,
    resemble.v1alpha1.errors_pb2.TransactionParticipantFailedToPrepare,
    resemble.v1alpha1.errors_pb2.TransactionParticipantFailedToCommit,
    resemble.v1alpha1.errors_pb2.UnknownService,
    resemble.v1alpha1.errors_pb2.UnknownTask,
    resemble.v1alpha1.errors_pb2.InvalidMethod,
]

# Any possible error type, i.e., possibly a `GrpcError`, a
# `ResembleError`, or a user declared error.
ErrorT = TypeVar('ErrorT', bound=Message)

AbortedT = TypeVar('AbortedT', bound='Aborted')


class Aborted(Exception):
    """Base class of all RPC specific code generated errors used for
    aborting an RPC.

    NOTE: Given the issues[1] with multiple inheritance from `abc.ABC` and `Exception`
    we do not inherit from `abc.ABC` but raise `NotImplementedError` for
    "abstract" methods.

    [1] https://bugs.python.org/issue12029
    """

    def __init__(self):
        super().__init__()
        # NOTE: we deliberately _do not_ want `Aborted` to be directly
        # instantiated, but instead want to keep it an abstract base
        # class, but can't make it an `ABC` due the reasons mentioned
        # above in the class docstring. We want to keep it an abstract
        # base class so that code uses `raise MethodAborted(...)`
        # rather than `Aborted` in their methods.
        if type(self) is Aborted:
            raise NotImplementedError

    def __str__(self):
        result = f"aborted with '{self.error.DESCRIPTOR.name}"

        # NOTE: we use `text_format` to ensure `as_one_line=True`.
        body = text_format.MessageToString(
            self.error,
            as_one_line=True,
        ).strip()

        if len(body) == 0:
            result += "'"
        else:
            result += f" {{ {body} }}'"

        if self.message is not None:
            result += f": {self.message}"

        return result

    @property
    def error(self) -> Message:
        raise NotImplementedError

    @property
    def code(self) -> grpc.StatusCode:
        raise NotImplementedError

    @property
    def message(self) -> Optional[str]:
        raise NotImplementedError

    @classmethod
    def from_status(
        cls: type[AbortedT],
        status: status_pb2.Status,
    ) -> AbortedT:
        raise NotImplementedError

    @classmethod
    def from_grpc_aio_rpc_error(
        cls: type[AbortedT],
        aio_rpc_error: grpc.aio.AioRpcError,
    ) -> AbortedT:
        raise NotImplementedError

    def to_status(self) -> status_pb2.Status:
        detail = any_pb2.Any()
        detail.Pack(self.error)

        return status_pb2.Status(
            # A `grpc.StatusCode` is a `tuple[int, str]` where the
            # `int` is the actual code that we need to pass on.
            code=self.code.value[0],
            message=self.message or "",
            details=[detail],
        )

    @classmethod
    def error_from_google_rpc_status_details(
        cls,
        status: status_pb2.Status,
        error_types: list[type[ErrorT]],
    ) -> Optional[ErrorT]:
        for detail in status.details:
            for error_type in error_types:
                if detail.Is(error_type.DESCRIPTOR):
                    error = error_type()
                    detail.Unpack(error)
                    return error

        return None

    @classmethod
    def error_from_google_rpc_status_code(
        cls,
        status: status_pb2.Status,
    ) -> GrpcError:
        if status.code == code_pb2.Code.CANCELLED:
            return resemble.v1alpha1.errors_pb2.Cancelled()

        elif status.code == code_pb2.Code.UNKNOWN:
            return resemble.v1alpha1.errors_pb2.Unknown()

        elif status.code == code_pb2.Code.INVALID_ARGUMENT:
            return resemble.v1alpha1.errors_pb2.InvalidArgument()

        elif status.code == code_pb2.Code.DEADLINE_EXCEEDED:
            return resemble.v1alpha1.errors_pb2.DeadlineExceeded()

        elif status.code == code_pb2.Code.NOT_FOUND:
            return resemble.v1alpha1.errors_pb2.NotFound()

        elif status.code == code_pb2.Code.ALREADY_EXISTS:
            return resemble.v1alpha1.errors_pb2.AlreadyExists()

        elif status.code == code_pb2.Code.PERMISSION_DENIED:
            return resemble.v1alpha1.errors_pb2.PermissionDenied()

        elif status.code == code_pb2.Code.RESOURCE_EXHAUSTED:
            return resemble.v1alpha1.errors_pb2.ResourceExhausted()

        elif status.code == code_pb2.Code.FAILED_PRECONDITION:
            return resemble.v1alpha1.errors_pb2.FailedPrecondition()

        elif status.code == code_pb2.Code.ABORTED:
            return resemble.v1alpha1.errors_pb2.Aborted()

        elif status.code == code_pb2.Code.OUT_OF_RANGE:
            return resemble.v1alpha1.errors_pb2.OutOfRange()

        elif status.code == code_pb2.Code.UNIMPLEMENTED:
            return resemble.v1alpha1.errors_pb2.Unimplemented()

        elif status.code == code_pb2.Code.INTERNAL:
            return resemble.v1alpha1.errors_pb2.Internal()

        elif status.code == code_pb2.Code.UNAVAILABLE:
            return resemble.v1alpha1.errors_pb2.Unavailable()

        elif status.code == code_pb2.Code.DATA_LOSS:
            return resemble.v1alpha1.errors_pb2.DataLoss()

        elif status.code == code_pb2.Code.UNAUTHENTICATED:
            return resemble.v1alpha1.errors_pb2.Unauthenticated()

        return resemble.v1alpha1.errors_pb2.Unknown()

    @classmethod
    def grpc_status_code_from_error(
        cls,
        error: Message,
    ) -> Optional[grpc.StatusCode]:
        if isinstance(error, resemble.v1alpha1.errors_pb2.Cancelled):
            return grpc.StatusCode.CANCELLED

        elif isinstance(error, resemble.v1alpha1.errors_pb2.Unknown):
            return grpc.StatusCode.UNKNOWN

        elif isinstance(error, resemble.v1alpha1.errors_pb2.InvalidArgument):
            return grpc.StatusCode.INVALID_ARGUMENT

        elif isinstance(error, resemble.v1alpha1.errors_pb2.DeadlineExceeded):
            return grpc.StatusCode.DEADLINE_EXCEEDED

        elif isinstance(error, resemble.v1alpha1.errors_pb2.NotFound):
            return grpc.StatusCode.NOT_FOUND

        elif isinstance(error, resemble.v1alpha1.errors_pb2.AlreadyExists):
            return grpc.StatusCode.ALREADY_EXISTS

        elif isinstance(error, resemble.v1alpha1.errors_pb2.PermissionDenied):
            return grpc.StatusCode.PERMISSION_DENIED

        elif isinstance(error, resemble.v1alpha1.errors_pb2.ResourceExhausted):
            return grpc.StatusCode.RESOURCE_EXHAUSTED

        elif isinstance(
            error, resemble.v1alpha1.errors_pb2.FailedPrecondition
        ):
            return grpc.StatusCode.FAILED_PRECONDITION

        elif isinstance(error, resemble.v1alpha1.errors_pb2.Aborted):
            return grpc.StatusCode.ABORTED

        elif isinstance(error, resemble.v1alpha1.errors_pb2.OutOfRange):
            return grpc.StatusCode.OUT_OF_RANGE

        elif isinstance(error, resemble.v1alpha1.errors_pb2.Unimplemented):
            return grpc.StatusCode.UNIMPLEMENTED

        elif isinstance(error, resemble.v1alpha1.errors_pb2.Internal):
            return grpc.StatusCode.INTERNAL

        elif isinstance(error, resemble.v1alpha1.errors_pb2.Unavailable):
            return grpc.StatusCode.UNAVAILABLE

        elif isinstance(error, resemble.v1alpha1.errors_pb2.DataLoss):
            return grpc.StatusCode.DATA_LOSS

        elif isinstance(error, resemble.v1alpha1.errors_pb2.Unauthenticated):
            return grpc.StatusCode.UNAUTHENTICATED

        return None

    @classmethod
    def error_from_grpc_aio_rpc_error(
        cls,
        aio_rpc_error: grpc.aio.AioRpcError,
    ) -> GrpcError:
        if aio_rpc_error.code() == grpc.StatusCode.CANCELLED:
            return resemble.v1alpha1.errors_pb2.Cancelled()

        elif aio_rpc_error.code() == grpc.StatusCode.UNKNOWN:
            return resemble.v1alpha1.errors_pb2.Unknown()

        elif aio_rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return resemble.v1alpha1.errors_pb2.InvalidArgument()

        elif aio_rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            return resemble.v1alpha1.errors_pb2.DeadlineExceeded()

        elif aio_rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return resemble.v1alpha1.errors_pb2.NotFound()

        elif aio_rpc_error.code() == grpc.StatusCode.ALREADY_EXISTS:
            return resemble.v1alpha1.errors_pb2.AlreadyExists()

        elif aio_rpc_error.code() == grpc.StatusCode.PERMISSION_DENIED:
            return resemble.v1alpha1.errors_pb2.PermissionDenied()

        elif aio_rpc_error.code() == grpc.StatusCode.RESOURCE_EXHAUSTED:
            return resemble.v1alpha1.errors_pb2.ResourceExhausted()

        elif aio_rpc_error.code() == grpc.StatusCode.FAILED_PRECONDITION:
            return resemble.v1alpha1.errors_pb2.FailedPrecondition()

        elif aio_rpc_error.code() == grpc.StatusCode.ABORTED:
            return resemble.v1alpha1.errors_pb2.Aborted()

        elif aio_rpc_error.code() == grpc.StatusCode.OUT_OF_RANGE:
            return resemble.v1alpha1.errors_pb2.OutOfRange()

        elif aio_rpc_error.code() == grpc.StatusCode.UNIMPLEMENTED:
            return resemble.v1alpha1.errors_pb2.Unimplemented()

        elif aio_rpc_error.code() == grpc.StatusCode.INTERNAL:
            return resemble.v1alpha1.errors_pb2.Internal()

        elif aio_rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
            return resemble.v1alpha1.errors_pb2.Unavailable()

        elif aio_rpc_error.code() == grpc.StatusCode.DATA_LOSS:
            return resemble.v1alpha1.errors_pb2.DataLoss()

        elif aio_rpc_error.code() == grpc.StatusCode.UNAUTHENTICATED:
            return resemble.v1alpha1.errors_pb2.Unauthenticated()

        return resemble.v1alpha1.errors_pb2.Unknown()


class SystemAborted(Aborted):
    """Encapsulates errors due to the system aborting."""

    Error = Union[GrpcError, ResembleError]

    ERROR_TYPES: list[type[Error]] = GRPC_ERROR_TYPES + RESEMBLE_ERROR_TYPES

    _error: Error
    _code: grpc.StatusCode
    _message: Optional[str]

    def __init__(
        self,
        error: Error,
        *,
        message: Optional[str] = None,
    ):
        super().__init__()

        assert_type(error, self.ERROR_TYPES)

        self._error = error

        code = self.grpc_status_code_from_error(self._error)

        if code is None:
            # Must be one of the Resemble specific errors.
            code = grpc.StatusCode.ABORTED

        self._code = code

        self._message = message

    @property
    def error(self) -> Error:
        return self._error

    @property
    def code(self) -> grpc.StatusCode:
        return self._code

    @property
    def message(self) -> Optional[str]:
        return self._message

    @classmethod
    def from_status(
        cls,
        status: status_pb2.Status,
    ) -> SystemAborted:
        error = cls.error_from_google_rpc_status_details(
            status,
            cls.ERROR_TYPES,
        )

        message = status.message if len(status.message) > 0 else None

        if error is not None:
            return cls(error, message=message)

        error = cls.error_from_google_rpc_status_code(status)

        assert error is not None

        # TODO(benh): also consider getting the type names from
        # `status.details` and including that in `message` to make
        # debugging easier.

        return cls(error, message=message)

    @classmethod
    def from_grpc_aio_rpc_error(
        cls,
        aio_rpc_error: grpc.aio.AioRpcError,
    ) -> SystemAborted:
        return cls(
            cls.error_from_grpc_aio_rpc_error(aio_rpc_error),
            message=aio_rpc_error.details(),
        )
