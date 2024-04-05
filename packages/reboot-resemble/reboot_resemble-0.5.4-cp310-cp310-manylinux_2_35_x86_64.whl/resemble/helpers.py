import asyncio
import base64
from google.api import annotations_pb2
from google.protobuf.descriptor import FileDescriptor
from google.protobuf.descriptor_pb2 import (
    FileDescriptorProto,
    FileDescriptorSet,
)
from resemble.aio.servicers import Routable
from resemble.aio.types import ServiceName
# TODO: Generated code. See https://github.com/reboot-dev/respect/issues/1698
from resemble.v1alpha1 import options_pb2  # type: ignore[attr-defined]
from typing import Optional, TypeVar

RoutableT = TypeVar('RoutableT', bound=Routable)


def add_file_descriptor_to_file_descriptor_set(
    return_set: FileDescriptorSet, file_descriptor: FileDescriptor
) -> None:
    """Helper that mutates the provided file descriptor set by adding a
    file descriptor proto to it based on the provided file descriptor."""
    file_descriptor_proto = FileDescriptorProto()
    file_descriptor.CopyToProto(file_descriptor_proto)

    # Add 'google.api.http' options for any resemble methods they were
    # not already added.
    for service in file_descriptor_proto.service:
        for method in service.method:
            path = f"/{file_descriptor_proto.package}.{service.name}.{method.name}"
            options = method.options
            if options.HasExtension(options_pb2.method):
                if not options.HasExtension(annotations_pb2.http):
                    # Users HAVE NOT added their own `google.api.http`
                    # options, let's add them so that our generated
                    # code can reach them.
                    #
                    # Invariant here is that we always use POST
                    # (because even for readers we might need to pass
                    # a request which currently gets passed in the
                    # body), and the full '/package.service.method'
                    # for the path.
                    #
                    # See also 'resemble/templates/resemble.ts.j2'.
                    if options.Extensions[options_pb2.method
                                         ].HasField('reader'):
                        options.Extensions[annotations_pb2.http].post = path
                    else:
                        options.Extensions[annotations_pb2.http].post = path
                else:
                    # Users have added their own `google.api.http`
                    # options, let's validate that they will work with
                    # our generated code.
                    #
                    # Invariant here is that we always use POST
                    # (because even for readers we might need to pass
                    # a request which currently gets passed in the
                    # body), and the full '/package.service.method'
                    # for the path.
                    #
                    # See also 'resemble/templates/resemble.ts.j2'.
                    if options.Extensions[annotations_pb2.http
                                         ].HasField('get'):
                        raise ValueError(
                            f"RPC method '{file_descriptor_proto.package}.{service.name}.{method.name}' "
                            "must use HTTP 'POST' (use 'post' not 'get' in your '.proto' file)"
                        )
                    if options.Extensions[annotations_pb2.http].post != path:
                        raise ValueError(
                            f"RPC method '{file_descriptor_proto.package}.{service.name}.{method.name}' "
                            f"must use HTTP path '{path}'"
                        )

    # The fields returned from `message_descriptor_proto.fields` do not
    # contain the `json_name` whereas the fields returned from
    # `message_descriptor.fields` do. Why? We're not sure.
    # These `for` loops attach the json name to the field descriptor
    # proto so the json_name is present when transcoding.
    # TODO: figure out if these fields can be inferred.
    for message_descriptor_proto in file_descriptor_proto.message_type:
        message_descriptor = file_descriptor.message_types_by_name[
            message_descriptor_proto.name]
        for field_descriptor_proto in message_descriptor_proto.field:
            field_descriptor = message_descriptor.fields_by_name[
                field_descriptor_proto.name]
            field_descriptor_proto.json_name = field_descriptor.json_name

    if file_descriptor_proto in return_set.file:
        return

    # Dependencies MUST be added to the file descriptor set first.
    # Envoy depends on the ProtoDescriptorPool and the
    # ProtoDescriptorPool requires this ordering.
    for dependency in file_descriptor.dependencies:
        add_file_descriptor_to_file_descriptor_set(return_set, dependency)

    return_set.file.append(file_descriptor_proto)


# This function is used to generate a `FileDescriptorSet` of any
# `Routable`s.
#
# Since it is logically grouped with extracting a config, we place it here as a
# top level function.
def generate_proto_descriptor_set(
    routables: list[RoutableT]
) -> FileDescriptorSet:
    """Generates a file descriptor set for the specified `Routable`s."""
    file_descriptor_set = FileDescriptorSet()

    for routable in routables:
        add_file_descriptor_to_file_descriptor_set(
            file_descriptor_set, routable.file_descriptor()
        )

    return file_descriptor_set


def service_names_from_descriptor_set(
    proto_descriptor_set: FileDescriptorSet
) -> list[ServiceName]:
    """Given a ProtoDescriptorSet, return the fully namespaced service names.
    """
    service_names = []
    for file_descriptor_proto in proto_descriptor_set.file:
        package_name = file_descriptor_proto.package
        for service in file_descriptor_proto.service:
            service_names.append(f'{package_name}.{service.name}')

    if len(service_names) == 0:
        raise ValueError(
            'no service names found in proto files: ' +
            str([f'{proto.name}' for proto in proto_descriptor_set.file])
        )

    return service_names


def base64_parse_proto_descriptor_set(
    serialized_proto_descriptor: bytes
) -> FileDescriptorSet:
    decoded_descriptor = base64.b64decode(serialized_proto_descriptor)
    file_descriptor_set = FileDescriptorSet()
    file_descriptor_set.ParseFromString(decoded_descriptor)
    return file_descriptor_set


def base64_serialize_proto_descriptor_set(
    file_descriptor_set: FileDescriptorSet
) -> bytes:
    return base64.b64encode(file_descriptor_set.SerializeToString())


async def maybe_cancel_task(task: Optional[asyncio.Task]):
    if task is not None and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
