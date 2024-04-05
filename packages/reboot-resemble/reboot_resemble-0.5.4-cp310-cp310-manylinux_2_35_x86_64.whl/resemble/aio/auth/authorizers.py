import resemble.v1alpha1.errors_pb2
from abc import ABC, abstractmethod
from google.protobuf.message import Message
from resemble.aio.contexts import ReaderContext
from typing import Generic, Optional, TypeAlias, TypeVar

StateType = TypeVar('StateType', bound=Message)
RequestTypes = TypeVar('RequestTypes', bound=Message)


class Authorizer(ABC, Generic[StateType, RequestTypes]):
    """Abstract base class for general Servicer Authorizers.

    A Servicer's authorizer is used to determine whether a given call to a
    Servicer's methods should be allowed or not.
    """

    # A value of `False` will be translated into a `PermissionDenied` error.
    Decision: TypeAlias = (
        resemble.v1alpha1.errors_pb2.Unauthenticated |
        resemble.v1alpha1.errors_pb2.PermissionDenied |
        resemble.v1alpha1.errors_pb2.Ok
    )

    @abstractmethod
    async def authorize(
        self,
        *,
        method_name: str,
        context: ReaderContext,
        state: Optional[StateType] = None,
        request: Optional[RequestTypes] = None,
    ) -> Decision:
        """Determine whether a call to a the method @method_name should be
        allowed.

        :param method_name: The name of the method being called.
        :param context: A reader context to enable calling other services.
        :param state: The state where and when available.
        :param request: The request object to the servicer method being called.

        Returns:
            `resemble.v1alpha1.errors_pb2.Ok()` if the call should be allowed,
            `resemble.v1alpha1.errors_pb2.Unauthenticated()` or
            `resemble.v1alpha1.errors_pb2.PermissionDenied()` otherwise.
        """
        # Sane default.
        return resemble.v1alpha1.errors_pb2.PermissionDenied()

    @abstractmethod
    def can_authorize(self, method_name: str) -> bool:
        """Determine if the 'Authorizer' is fit for making an authorization
        decision for a given method name.
        """
        raise NotImplementedError
