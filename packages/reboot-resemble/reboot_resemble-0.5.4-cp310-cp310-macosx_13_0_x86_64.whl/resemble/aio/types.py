from typing import Any

# Collection of types used throughout our code with more meaningful names than
# the underlying python types.

ApplicationId = str
ActorId = str
ServiceName = str
ConsensusId = str
GrpcMetadata = tuple[tuple[str, str], ...]
RoutableAddress = str
KubernetesNamespace = str


def assert_type(
    t: Any,
    types: list[type[Any]],
    *,
    may_be_subclass: bool = True,
) -> None:
    """Check that 't' is an instance of one of the expected types.

    Raises TypeError if 't' is not one of the expected types.
    """

    def check(t: Any, expected_type: Any) -> bool:
        if may_be_subclass:
            return isinstance(t, expected_type)
        else:
            return type(t) is expected_type

    if any([check(t, expected_type) for expected_type in types]):
        return

    def type_name(cls):
        return f'{cls.__module__}.{cls.__qualname__}'

    if may_be_subclass:
        raise TypeError(
            f'{type_name(type(t))} is not an instance or subclass of one of the expected '
            f'type(s): {[type_name(expected_type) for expected_type in types]}'
        )
    else:
        raise TypeError(
            f'{type_name(type(t))} is not a non-subclass instance of one of the expected '
            f'type(s): {[type_name(expected_type) for expected_type in types]}'
        )
