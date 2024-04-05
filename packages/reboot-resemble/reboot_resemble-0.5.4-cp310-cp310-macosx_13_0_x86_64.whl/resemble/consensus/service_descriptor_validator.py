import importlib.metadata
from google.protobuf.descriptor import (
    Descriptor,
    FieldDescriptor,
    MethodDescriptor,
    ServiceDescriptor,
)
from google.protobuf.descriptor_pb2 import DescriptorProto, FileDescriptorSet
from google.protobuf.descriptor_pool import DescriptorPool
from packaging import version
from resemble.controller.exceptions import InputError
from resemble.options import get_method_options, is_resemble_service
from resemble.v1alpha1 import options_pb2
from typing import Any, Iterable, Optional


class ProtoValidationError(InputError):
    pass


def validate_descriptor_sets_are_backwards_compatible(
    original_file_descriptor_set: FileDescriptorSet,
    updated_file_descriptor_set: FileDescriptorSet
) -> None:
    """Go through each Service definition in the given encoded
    FileDescriptorSets to ensure that there are no backwards-incompatible
    changes.
    Raises a combined Exception of all the exceptions found, if any. Successful
    completion of the method means a valid update."""
    # Ensure that we have a sufficient version of protobuf as there
    # have been bugs in previous versions that did not properly set
    # fields that we need to check backwards compatibility.
    found_protobuf_version = version.Version(
        importlib.metadata.version('protobuf')
    )
    required_protobuf_version = version.Version('4.21.11')

    if found_protobuf_version < required_protobuf_version:
        raise RuntimeError(
            f"protobuf version must be >= '{required_protobuf_version}', "
            f"found '{found_protobuf_version}'"
        )

    exceptions: list[Exception] = []
    original_services_by_name = _get_all_resemble_services_by_name(
        original_file_descriptor_set
    )
    updated_services_by_name = _get_all_resemble_services_by_name(
        updated_file_descriptor_set
    )
    for service_name, original_service_descriptor in original_services_by_name.items(
    ):
        try:
            updated_service_descriptor = updated_services_by_name[service_name]
        except KeyError:
            # The whole service was deleted.
            exceptions.append(
                ProtoValidationError(
                    reason=f'Service {service_name} was deleted'
                )
            )
            continue

        exceptions += _validate_methods_are_backwards_compatible(
            original_service_descriptor, updated_service_descriptor
        )

    if len(exceptions) > 0:
        combined_exception = Exception(exceptions)
        raise ProtoValidationError(
            reason='Updated service definitions are not backwards compatible',
            parent_exception=combined_exception
        )


def _get_all_resemble_services_by_name(
    file_descriptor_set: FileDescriptorSet
) -> dict[str, ServiceDescriptor]:
    descriptor_pool = DescriptorPool()
    services_by_name: dict[str, ServiceDescriptor] = {}
    for file_descriptor_proto in file_descriptor_set.file:
        # We can't add a file to a pool if it's already been added, so let's
        # first check if it's already there.
        try:
            file_descriptor = descriptor_pool.FindFileByName(
                file_descriptor_proto.name
            )
        except KeyError:
            file_descriptor = descriptor_pool.Add(file_descriptor_proto)
        # Merge the new file descriptor's list of services with the combined
        # list.
        try:
            for service_name, service_descriptor in file_descriptor.services_by_name.items(
            ):
                if is_resemble_service(service_descriptor):
                    services_by_name[service_name] = service_descriptor

        except AttributeError:
            # This file descriptor has no services. That's fine - maybe it's
            # just some messages that services depend on. Skip it.
            continue

    return services_by_name


def _validate_methods_are_backwards_compatible(
    original: ServiceDescriptor,
    updated: ServiceDescriptor,
) -> list[Exception]:
    """Validate the given updated Service against the original version to ensure
    that no relevant RPCs have backwards-incompatible changes in the updated
    version. Ignore methods not named in the method_names_filter set.
    Returns a list of all the Exceptions found, or an empty list if the change
    is valid."""
    exceptions: list[Exception] = []
    for method in original.methods_by_name.values():
        # Ignore methods that aren't Resemble tasks.
        # TODO: Also selectively filter out task methods when they don't have
        # any persisted Task data. If there is no persisted Task, then the task
        # method can safely change, because it will never be called with an old
        # request.
        if not _is_resemble_task(method):
            continue

        # Make sure the method is still present in the updated file.
        try:
            updated_method = updated.methods_by_name[method.name]
        except KeyError:
            exceptions.append(
                ProtoValidationError(
                    reason=f'Method {method.name} was deleted'
                )
            )
            continue

        # Run several validations and collect Exceptions from each.
        exceptions += _validate_resemble_options(method, updated_method)
        exceptions += _validate_request_response(method, updated_method)

    return exceptions


def _is_resemble_task(method: MethodDescriptor) -> bool:
    """Returns true if the given method has Resemble options set, false
    otherwise."""
    resemble_options: options_pb2.MethodOptions = get_method_options(
        method.GetOptions()
    )
    return resemble_options.WhichOneof(
        'kind'
    ) is not None and resemble_options.HasField('task')


def _validate_resemble_options(
    original_method: MethodDescriptor, updated_method: MethodDescriptor
) -> list[Exception]:
    """Compare the Resemble options for the original and updated methods to be
    sure there are no changes.
    Return a list of Exceptions describing any discrepancies. An empty list
    means equivalent options.
    """
    # Currently, we treat all changes as backwards-incompatible.
    original_resemble_options: options_pb2.MethodOptions = get_method_options(
        original_method.GetOptions()
    )
    updated_resemble_options: options_pb2.MethodOptions = get_method_options(
        updated_method.GetOptions()
    )
    if original_resemble_options != updated_resemble_options:
        # Even though we only have one exception to return right now, return it
        # in a list for easy combining with other lists.
        return [
            ProtoValidationError(
                reason=
                f'Custom options for method {original_method.name} updated '
                f'from {original_resemble_options} '
                f'to {updated_resemble_options}'
            )
        ]
    return []


def _validate_request_response(
    original_method: MethodDescriptor, updated_method: MethodDescriptor
) -> list[ProtoValidationError]:
    """Check that the two MethodDescriptors have the same request and response
    types with the same structures.
    Return a list of Exceptions describing any discrepancies. An empty list
    means equivalent method signatures.
    """
    return _compare_messages(
        original_method.input_type,
        updated_method.input_type,
        original_method.name,
    ) + _compare_messages(
        original_method.output_type,
        updated_method.output_type,
        original_method.name,
    )


def _check_field_property(
    original_value: Any, updated_value: Any, message_name: str,
    field_name: str, property_name: str
) -> list[ProtoValidationError]:
    """Compare the two values, and if they are not the same, return a ProtoValidationError
    with a message based on the given field_name and property_name.
    Return the exception in a list for easy combining with other lists and the
    option to add more returned exceptions in the future."""
    if original_value != updated_value:
        return [
            ProtoValidationError(
                reason=
                f'Field {field_name} in message {message_name} has switched '
                f'{property_name} from {original_value} to {updated_value}'
            )
        ]
    return []


def _compare_reserved_field_numbers(
    original_ranges: Iterable[DescriptorProto.ReservedRange],
    updated_ranges: Iterable[DescriptorProto.ReservedRange],
    original_message_name: str,
    where_message: str,
) -> list[ProtoValidationError]:
    """
    Compare the reserved field numbers in the two given messages. If the updated
    field numbers are not a superset of the original field numbers, returns an
    error for every missing range.
    """
    exceptions: list[ProtoValidationError] = []
    [reserved_range for reserved_range in original_ranges]

    original_ranges = sorted(original_ranges, key=lambda r: r.start)
    original_ranges_iter = iter(original_ranges)
    original_range: Optional[DescriptorProto.ReservedRange
                            ] = (next(original_ranges_iter, None))
    updated_ranges = sorted(updated_ranges, key=lambda r: r.start)
    updated_ranges_iter = iter(updated_ranges)
    updated_range: Optional[DescriptorProto.ReservedRange
                           ] = next(updated_ranges_iter, None)

    # As long as we still have original ranges to check...
    while original_range is not None:
        # The current `updated_range` must fall before, or overlap with the
        # start of, the current `original_range`. If it falls after, then we
        # have a missing range.
        if updated_range is None or updated_range.start > original_range.start:
            missing_start = original_range.start
            # Since users think of inclusive ranges, communicate the missing
            # range with an inclusive end.
            missing_end_inclusive = original_range.end - 1
            if updated_range is not None:
                # Perhaps the updated range does cover a part of the original
                # range. Only complain about the part that's missing.
                missing_end_inclusive = min(
                    missing_end_inclusive, updated_range.start - 1
                )
            exceptions.append(
                ProtoValidationError(
                    reason=f'Field numbers {missing_start} to '
                    f'{missing_end_inclusive} are no longer `reserved` in '
                    f'message `{original_message_name}` ({where_message}).'
                )
            )
            # If we were missing the whole original range, we move on to the
            # next original range, to see whether it was also removed.
            # If we were only missing part of the original range, we move on to
            # see whether the remaining part of the original range is fully
            # present.
            if (
                updated_range is None or
                original_range.end <= updated_range.start
            ):
                # The full original range was not covered by the updated range.
                original_range = next(original_ranges_iter, None)
            else:
                # Only part of the original range was missing.
                original_range.start = updated_range.start

        # If the updated range ends before the original range, then it covers
        # nothing. We can skip to the next updated range.
        elif updated_range.end <= original_range.start:
            updated_range = next(updated_ranges_iter, None)

        # If none of the above applied, then the original range must (partially)
        # cover the updated range, so we can declare victory for that (part of
        # the) updated range and move on to the next (part of the) original
        # range.
        else:
            assert updated_range.start <= original_range.start
            assert updated_range.end > original_range.start
            if updated_range.end < original_range.end:
                # The updated range ends before the original range ends, so we
                # need still check the remainder of the original range.
                original_range.start = updated_range.end
            else:
                # The updated range ends after the original range ends, so it
                # covers the whole original range. We can move on to the next
                # original range.
                original_range = next(original_ranges_iter, None)

    return exceptions


def _compare_messages(
    original_message: Descriptor,
    updated_message: Descriptor,
    # TODO(rjh): make sure the `method_name` is used in all of the error
    # messages produced by this function.
    method_name: str,
) -> list[ProtoValidationError]:
    """Check that the two messages have the same structure.
    Return a list of Exceptions describing any discrepancies. An empty list
    means equivalent options."""

    # Annoyingly, some information (notably the list of reserved field numbers
    # and names) is only accessible from the DescriptorProto, not the
    # Descriptor. So we have to convert the Descriptor to a DescriptorProto
    # first.
    original_message_proto = DescriptorProto()
    original_message.CopyToProto(original_message_proto)
    updated_message_proto = DescriptorProto()
    updated_message.CopyToProto(updated_message_proto)

    # What do we call the message(s) we're comparing? If it didn't change names,
    # it's easy. But if it changed names, we should hint the user that any
    # errors are possibly due to the change from one message type to another.
    where_message = f'in `{method_name}`'
    if original_message.name != updated_message.name:
        where_message = f'changed to `{updated_message.name}` {where_message}'

    # Check that none of the reserved fields in the original message were
    # removed.
    exceptions: list[ProtoValidationError] = _compare_reserved_field_numbers(
        original_message_proto.reserved_range,
        updated_message_proto.reserved_range,
        original_message_proto.name,
        where_message,
    )
    for reserved_name in original_message_proto.reserved_name:
        if reserved_name not in updated_message_proto.reserved_name:
            exceptions.append(
                ProtoValidationError(
                    reason=
                    f'Field name `{reserved_name}` is no longer `reserved` in '
                    f'message `{original_message.name}` ({where_message}).'
                )
            )

    for field_number, original_field in original_message.fields_by_number.items(
    ):
        try:
            updated_field = updated_message.fields_by_number[field_number]
        except KeyError:
            # This field has been deleted. That's a backwards compatible change,
            # but ONLY if the field number and name have now been `reserved`.
            field_number_reserved = False
            for reserved_range in updated_message_proto.reserved_range:
                field_number_reserved |= (
                    reserved_range.start <= field_number and
                    reserved_range.end > field_number
                )
            if not field_number_reserved:
                exceptions.append(
                    ProtoValidationError(
                        reason=f'Field `{original_field.name}` was deleted from '
                        f'message `{original_message.name}` ({where_message}), '
                        'and its field number was not reserved. See: '
                        'https://protobuf.dev/programming-guides/proto3/#reserved'
                    )
                )

            if original_field.name not in updated_message_proto.reserved_name:
                exceptions.append(
                    ProtoValidationError(
                        reason=f'Field `{original_field.name}` was deleted from '
                        f'message `{original_message.name}` ({where_message}), '
                        'and its field name was not reserved. See: '
                        'https://protobuf.dev/programming-guides/proto3/#reserved'
                    )
                )

            # Since this field doesn't exist anymore, there's nothing more to
            # validate about it. On to the next.
            continue

        # Every property in the FieldDescriptor needs to be the same.
        for property_name in ['type', 'label']:
            exceptions += _check_field_property(
                getattr(original_field, property_name),
                getattr(updated_field, property_name),
                # Use the updated names in error messages - if it's changed,
                # the new one will be more recognizable.
                updated_message.name,
                updated_field.name,
                property_name
            )

        # If this field is a nested proto message, descend into it recursively.
        if original_field.type == FieldDescriptor.TYPE_MESSAGE:
            exceptions += _compare_messages(
                original_field.message_type,
                updated_field.message_type,
                method_name,
            )

    return exceptions
