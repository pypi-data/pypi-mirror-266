#!/usr/bin/env python3
import os
from collections import defaultdict
from dataclasses import dataclass
from google.protobuf.descriptor import (
    Descriptor,
    FieldDescriptor,
    FileDescriptor,
    MethodDescriptor,
    ServiceDescriptor,
)
from google.protobuf.descriptor_pb2 import FileDescriptorProto, ServiceOptions
# TODO: Dependency not recognized in git-submodule for some reason.
from pyprotoc_plugin.helpers import (  # type: ignore[import]
    add_template_path,
    load_template,
)
from pyprotoc_plugin.plugins import ProtocPlugin  # type: ignore[import]
from resemble.cli import terminal
from resemble.options import get_method_options, is_resemble_service
from resemble.v1alpha1 import options_pb2
from typing import Any, Iterable, Literal, Optional

# NOTE: we need to add the template path so we can test
# `ResembleProtocPlugin` even when we're not '__main__'.
add_template_path(os.path.join(__file__, '../templates/'))

Feature = Literal[
    'reader',
    'writer',
    'transaction',
    'task',
    'error',
    'streaming',
]


class UserProtoError(Exception):
    """Exception raised in case of a malformed user-provided proto file."""
    pass


@dataclass(kw_only=True)
class PluginSpecificData:
    template_filename: str
    output_filename_suffix: str
    supported_features: list[Feature]


def pb2_message_names(file: FileDescriptor) -> list[str]:
    """Helper to extract name of all messages from file descriptor.
    """
    # NOTE: `message_types_by_name` is undefined if no messages are present.
    try:
        return list(file.message_types_by_name.keys())
    except AttributeError as e:
        assert 'message_types_by_name' in str(e)
        return []


class ResembleProtocPlugin(ProtocPlugin):

    @staticmethod
    def plugin_specific_data() -> PluginSpecificData:
        raise NotImplementedError

    @classmethod
    def get_file_services(cls,
                          file: FileDescriptor) -> Iterable[ServiceDescriptor]:
        """Helper as file.services_by_name is undefined if len(file.service)
        is 0.
        """
        # TODO: move to ProtocPlugin.
        try:
            return file.services_by_name.values()
        except AttributeError:
            return []

    def analyze_method_options(
        self,
        method: MethodDescriptor,
        streaming: bool,
    ) -> dict[str, Any]:
        """Finds the resemble.MethodOptions, if any, and returns a dictionary of
        the options.
        """
        method_options = get_method_options(method.GetOptions())
        kind: Optional[str] = method_options.WhichOneof('kind')
        if kind is None:
            raise UserProtoError(
                f"'{method.name}' is missing the required Resemble annotation 'kind'"
            )

        state_streaming = streaming

        if kind == 'reader':
            if (
                method_options.reader.state ==
                options_pb2.ReaderMethodOptions.State.STREAMING
            ):
                state_streaming = True
            elif (
                method_options.reader.state ==
                options_pb2.ReaderMethodOptions.State.UNARY
            ):
                state_streaming = False

        # From error name, e.g., 'product.api.ErrorName' to dictionary
        # of types depending on language, e.g., { 'py_type':
        # 'product.api.file_pb2.ErrorName' }.
        errors: defaultdict[str, dict[str, str]] = defaultdict(dict)

        for error in method_options.errors:
            file = self.get_file_for_message_name(
                error,
                method.containing_service.file,
            )
            errors[f"{file.package}.{error.split('.')[-1]}"][
                'py_type'] = self.full_py_type_name(
                    file.message_types_by_name[error.split('.')[-1]]
                )

        # NOTE: to get the _actual_ field that is set in the oneof we need
        # to use `getattr()` which takes the name of the field that we've
        # stored in `kind`.
        kind_options = getattr(method_options, kind)

        options = {
            'kind': kind,
            kind: kind_options,
            'constructor':
                (
                    (kind == 'writer' or kind == 'transaction') and
                    kind_options.HasField('constructor')
                ),
            'state_streaming': state_streaming,
            'errors': errors,
        }

        if method_options.HasField('task'):
            options['task'] = method_options.task

        return options

    @classmethod
    def rsm_module_name(cls, file: FileDescriptor) -> str:
        """Get rsm Python module name from file descriptor name and package.
        """
        file_name = os.path.basename(file.name).removesuffix('.proto')
        return file.package + '.' + file_name + '_rsm'

    @classmethod
    def py_module_name(cls, file: FileDescriptor) -> str:
        """Get gRPC Python module name from file descriptor name and package.
        """
        # TODO: move to ProtocPlugin.
        file_name = os.path.basename(file.name).removesuffix('.proto')
        return file.package + '.' + file_name + '_pb2'

    @classmethod
    def py_type_name(cls, message: Descriptor) -> str:
        """Get type name of the given message type, including any enclosing
        types.
        """
        if message.containing_type is None:
            return message.name
        return f"{cls.py_type_name(message.containing_type)}.{message.name}"

    @classmethod
    def full_py_type_name(cls, message: Descriptor) -> str:
        """Get full name (package and type) of generated grpc message from
        message descriptor.
        """
        # TODO: move to ProtocPlugin.
        py_type_name = cls.py_type_name(message)
        py_module_name = cls.py_module_name(message.file)
        full_py_type_name = f'{py_module_name}.{py_type_name}'
        return full_py_type_name

    @classmethod
    def analyze_message_fields(
        cls,
        message: Descriptor,
    ) -> dict[str, dict[str, str]]:
        """Returns a dict from field name, e.g., 'foo' to dictionary of types
        depending on language, e.g., { 'py_type': 'product.api.file_pb2.Foo' }.
        """
        # TODO: consider moving to ProtocPlugin.
        py_types: dict[int, str] = {
            FieldDescriptor.TYPE_DOUBLE: 'float',
            FieldDescriptor.TYPE_FLOAT: 'float',
            FieldDescriptor.TYPE_INT32: 'int',
            FieldDescriptor.TYPE_INT64: 'int',
            FieldDescriptor.TYPE_UINT32: 'int',
            FieldDescriptor.TYPE_UINT64: 'int',
            FieldDescriptor.TYPE_SINT32: 'int',
            FieldDescriptor.TYPE_SINT64: 'int',
            FieldDescriptor.TYPE_FIXED32: 'int',
            FieldDescriptor.TYPE_FIXED64: 'int',
            FieldDescriptor.TYPE_SFIXED32: 'int',
            FieldDescriptor.TYPE_SFIXED64: 'int',
            FieldDescriptor.TYPE_BOOL: 'bool',
            FieldDescriptor.TYPE_STRING: 'str',
            FieldDescriptor.TYPE_BYTES: 'bytes',
            FieldDescriptor.TYPE_ENUM: 'int',
        }

        message_fields: defaultdict[str, dict[str, str]] = defaultdict(dict)

        for field in message.fields:
            if field.type == FieldDescriptor.TYPE_GROUP:
                raise UserProtoError(
                    "Fields of type 'group' are currently not supported"
                )
            elif field.type == FieldDescriptor.TYPE_MESSAGE:
                message_fields[field.name]['py_type'] = cls.full_py_type_name(
                    field.message_type
                )
            else:
                assert field.type in py_types
                message_fields[field.name]['py_type'] = py_types[field.type]

            if field.label == FieldDescriptor.LABEL_REPEATED:
                # TODO(benh): can we use 'Iterable' instead of 'list'?
                message_fields[field.name].update(
                    {
                        'py_type':
                            f"list[{message_fields[field.name]['py_type']}]"
                    }
                )

        return message_fields

    @classmethod
    def analyze_imports(cls, file: FileDescriptor) -> set[str]:
        """Return set of python imports necessary for our generated code
        based on the file descriptor.
        """
        # NOTE: While most of this function is general for any python plugin and
        # could be moved up to `ProtocPlugin` parts of the code is resemble
        # specific.

        # Firstly, we need the standard grpc modules, i.e., `_pb2` and
        # `_pb2_grpc`...
        imports = {
            cls.py_module_name(file),
            cls.py_module_name(file) + '_grpc'
        }

        # Also include each 'import' in the .proto file.
        for dependency in file.dependencies:
            imports.add(cls.py_module_name(dependency))

        return imports

    @classmethod
    def analyze_google_protobuf_imports(cls, file: FileDescriptor) -> set[str]:
        """Returns a set of message type names from the google.protobuf package.
        """
        google_protobuf_deps = []
        for dep in file.dependencies:
            if dep.package.startswith('google.protobuf'):
                google_protobuf_deps += list(dep.message_types_by_name.keys())

        return set(google_protobuf_deps)

    @classmethod
    def get_service_options(
        cls, options: ServiceOptions
    ) -> options_pb2.ServiceOptions:
        """Takes a proto descriptor of options specified on a service, and extracts the
           resemble.ServiceOptions, if such an option is set.
        """
        # This is the proto API for accessing our custom options used in the
        # given `ServiceOptions`. Returns an empty resemble.ServiceOptions if no
        # option is set, which means its options will default to the proto
        # defaults for their field types.
        return options.Extensions[options_pb2.service]

    def get_file_for_message_name(
        self,
        message_name: str,
        current_file: FileDescriptor,
    ) -> FileDescriptor:
        if '.' not in message_name:
            # If we don't have a package name, assume it is the same
            # package as the current file.
            package_name = current_file.package
            message_name = f'{package_name}.{message_name}'

        try:
            return self.pool.FindFileContainingSymbol(message_name)
        except KeyError as e:
            raise UserProtoError(
                f'Can not resolve message type: {message_name}'
            ) from e

    def analyze_service_options(
        self,
        service: ServiceDescriptor,
    ) -> dict[str, Any]:
        """Finds the resemble.ServiceOptions, if any, and returns a dictionary of
        the options.
        """

        service_options = self.get_service_options(service.GetOptions())

        state_name = service_options.state

        file = self.get_file_for_message_name(state_name, service.file)

        return {
            'state_pb2_name': self.py_module_name(file),
            'state_name': state_name.split('.')[-1],
            'default_constructible': service_options.default_constructible,
        }

    def is_reader_only(
        self, file: FileDescriptor, service: ServiceDescriptor
    ) -> bool:
        """Returns True if all RPCs defined in the service are Readers.
        False, otherwise.
        """
        for method in service.method:
            method_options = self.analyze_method_options(
                file.services_by_name[service.name].methods_by_name[method.name
                                                                   ],
                (method.client_streaming or method.server_streaming),
            )
            if method_options['kind'] != 'reader':
                return False

        return True

    def analyze_file(self, proto_file: FileDescriptorProto) -> dict[str, Any]:
        # TODO(benh): the Python protobuf library does not correctly
        # set fields in MethodDescriptor and ServiceDescriptor, (see
        # https://github.com/protocolbuffers/protobuf/issues/4731).
        # Therefore, we need to use both FileDescriptorProto and
        # FileDescriptor otherwise we'll miss information! For
        # example, 'client_streaming' and 'server_streaming' are not
        # correctly set on MethodDescriptor but are correctly set with
        # MethodDescriptorProto.
        file = self.pool.FindFileByName(proto_file.name)

        if file.package == '':
            raise UserProtoError(
                f"{file.name} is missing a (currently) required 'package'"
            )

        directory = os.path.dirname(file.name)
        package_directory = file.package.replace('.', os.path.sep)
        if package_directory != directory:
            raise UserProtoError(
                f"Proto file '{file.name}' has package '{file.package}', but "
                "based on the file's path the expected package was "
                f"'{directory.replace(os.path.sep, '.')}'. 'rsm protoc' "
                "expects the package to match the directory structure. Check "
                "that the API base directory is correct, and if so, adjust "
                "either the proto file's location or its package."
            )

        template_data = {
            'proto_file_name':
                file.name,
            'package_name':
                file.package,
            'imports':
                self.analyze_imports(file),
            'google_protobuf_used_messages':
                self.analyze_google_protobuf_imports(file),
            'rsm_name':
                self.rsm_module_name(file),
            'pb2_name':
                self.py_module_name(file),
            'pb2_grpc_name':
                f'{self.py_module_name(file)}_grpc',
            'pb2_messages':
                pb2_message_names(file),
            'services':
                [
                    {
                        'name':
                            service.name,
                        'options':
                            self.analyze_service_options(
                                file.services_by_name[service.name]
                            ),
                        'reader_only':
                            self.is_reader_only(file, service),
                        'methods':
                            [
                                {
                                    'name':
                                        method.name,
                                    'input_type':
                                        self.full_py_type_name(
                                            file.services_by_name[
                                                service.name].methods_by_name[
                                                    method.name].input_type
                                        ),
                                    'output_type':
                                        self.full_py_type_name(
                                            file.services_by_name[
                                                service.name].methods_by_name[
                                                    method.name].output_type
                                        ),
                                    'input_type_fields':
                                        self.analyze_message_fields(
                                            file.services_by_name[
                                                service.name].methods_by_name[
                                                    method.name].input_type
                                        ),
                                    'client_streaming':
                                        method.client_streaming,
                                    'server_streaming':
                                        method.server_streaming,
                                    'options':
                                        self.analyze_method_options(
                                            file.services_by_name[service.name]
                                            .methods_by_name[method.name],
                                            (
                                                method.client_streaming or
                                                method.server_streaming
                                            ),
                                        ),
                                } for method in service.method
                            ],
                    } for service in proto_file.service if
                    is_resemble_service(file.services_by_name[service.name])
                ],
            'legacy_grpc_services':
                [
                    {
                        'name': service.name,
                    }
                    for service in proto_file.service
                    if not is_resemble_service(
                        file.services_by_name[service.name]
                    )
                ],
        }
        all_types: set[str] = set()
        for service in template_data['services']:
            for method in service['methods']:
                all_types.add(method['input_type'])
                all_types.add(method['output_type'])
                if method['client_streaming'] and method['options'][
                    'kind'] != 'reader':
                    raise UserProtoError(
                        'Client streaming only supported for readers'
                    )
                if method['server_streaming'] and method['options'][
                    'kind'] != 'reader':
                    raise UserProtoError(
                        'Server streaming only supported for readers'
                    )
                if (method['client_streaming'] or method['server_streaming']
                   ) and 'task' in method['options']:
                    raise UserProtoError('Streaming not supported for tasks')

        template_data['all_types'] = list(all_types)

        # Determine which services require a constructor.
        #
        # By default, if no writers or transactions are marked as
        # constructors, then a constructor is not required. However, a
        # user can set the 'default_constructible' option on their
        # service to 'false' to require that only a constructor can
        # get called. Likewise, even if there are constructors, a user
        # can set 'default_constructible' to 'true' to allow
        # writers/transactions to act as constructors.
        for service in template_data['services']:
            service['requires_constructor'] = False
            if service['options']['default_constructible']:
                continue
            for method in service['methods']:
                if method['options']['constructor']:
                    service['requires_constructor'] = True
                    break

        return template_data

    def validate_features(self, template_data: dict[str, Any]) -> None:
        """Raises an error if not all user-requested features are implemented.
        """
        feature_set_in_template_data = set()

        for service in template_data['services']:
            for method in service['methods']:
                feature_set_in_template_data.add(method['options']['kind'])
                if method['options']['errors'] != defaultdict(dict):
                    feature_set_in_template_data.add('error')
                if 'task' in method['options']:
                    feature_set_in_template_data.add('task')
                if method['options']['state_streaming'] or method[
                    'client_streaming'] or method['server_streaming']:
                    feature_set_in_template_data.add('streaming')

        supported_feature_set = set(
            self.plugin_specific_data().supported_features
        )

        if not feature_set_in_template_data.issubset(supported_feature_set):
            terminal.fail(
                'You are attempting to use Resemble features in your .proto '
                'file that are not yet supported.\n'
                '\n'
                f'Unsupported features: {feature_set_in_template_data - supported_feature_set}'
            )

    def template_render(
        self,
        proto_file: FileDescriptorProto,
        template_data: dict[str, Any],
    ) -> str:
        template = load_template(
            self.plugin_specific_data().template_filename,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            extensions=['jinja2_strcase.StrcaseExtension'],
        )

        return template.render(**template_data)

    def process_file(self, proto_file: FileDescriptorProto) -> None:
        try:
            template_data: dict[str, Any] = self.analyze_file(proto_file)

            # 'template_data['services']' only contains Resemble services. If the
            # `proto_file` does not contain resemble services, i.e. dependencies,
            # do not generate Resemble-specific code.
            if len(template_data['services']) == 0:
                return None

            self.validate_features(template_data)

            content = self.template_render(proto_file, template_data)

            output_file = self.response.file.add()
            output_file.name = template_data['proto_file_name'].replace(
                '.proto',
                self.plugin_specific_data().output_filename_suffix,
            )
            output_file.content = content

        except (UserProtoError, ValueError) as error:
            # NOTE: we catch `ValueError` here because we're using methods from
            # `options.py` might raise `ValueError` in response to malformed input.
            # We re-raise any error as a `UserProtoError`
            # but with additional information in the error message.
            raise UserProtoError(
                f'Error processing {proto_file.name}: {error}'
            ) from error
