#!/usr/bin/env python3
import base64
import gzip
import sys
import tempfile
from google.protobuf.descriptor import FileDescriptor
from google.protobuf.descriptor_pb2 import (
    FileDescriptorProto,
    FileDescriptorSet,
)
from grpc_tools import protoc as grpc_tools_protoc
from importlib import resources
from resemble.cli import terminal
from resemble.cli.directories import chdir
from resemble.protoc_gen_resemble_generic import (
    PluginSpecificData,
    ResembleProtocPlugin,
    UserProtoError,
)
from resemble.protoc_gen_resemble_python import PythonResembleProtocPlugin
from typing import Any


def protoc(file: FileDescriptor) -> tuple[str, str]:
    """Helper for generating *_pb2.py and *_pb2_grpc.py files that we
    embed within the *_rsm.ts generated files.
    """
    protoc_args: list[str] = ["grpc_tool.protoc"]

    # We want to find the Python `site-packages`/`dist-packages` directories
    # that contain a 'resemble/v1alpha1' directory, which is where we'll
    # find our protos. We can look for the 'resemble' folder via the
    # `resources` module; the resulting path is a `MultiplexedPath`, since
    # there may be multiple. Such a path doesn't contain a `parent`
    # attribute, since there isn't one answer. Instead we use `iterdir()` to
    # get all of the children of all 'resemble' folders, and then
    # deduplicate the parents-of-the-parents-of-those-children (via the
    # `set`), which gives us the `resemble` folders' parents' paths.
    resemble_parent_paths: set[str] = set()
    for resource in resources.files('resemble').iterdir():
        with resources.as_file(resource) as path:
            resemble_parent_paths.add(str(path.parent.parent))

    if len(resemble_parent_paths) == 0:
        raise FileNotFoundError(
            "Failed to find 'resemble' resource path. "
            "Please report this bug to the maintainers."
        )

    # Now add these to '--proto_path', so that users don't need to provide
    # their own Resemble protos.
    for resemble_parent_path in resemble_parent_paths:
        protoc_args.append(f"--proto_path={resemble_parent_path}")

    # User protos may rely on `google.protobuf.*` protos. We
    # conveniently have those files packaged in our Python
    # package; make them available to users, so that users don't
    # need to provide them.
    protoc_args.append(
        f"--proto_path={resources.files('grpc_tools').joinpath('_proto')}"
    )

    with tempfile.TemporaryDirectory() as directory:
        with chdir(directory):
            protoc_args.append('--python_out=.')
            protoc_args.append('--grpc_python_out=.')

            # Create a `FileDescriptorSet` that we can use as input to
            # calling `protoc`.
            file_descriptor_set = FileDescriptorSet()

            def add_file_descriptor(file_descriptor: FileDescriptor):
                file_descriptor_proto = FileDescriptorProto()
                file_descriptor.CopyToProto(file_descriptor_proto)

                if file_descriptor_proto in file_descriptor_set.file:
                    return

                for dependency in file_descriptor.dependencies:
                    add_file_descriptor(dependency)

                file_descriptor_set.file.append(file_descriptor_proto)

            add_file_descriptor(file)

            with open('file_descriptor_set', 'wb') as file_descriptor_set_file:
                file_descriptor_set_file.write(
                    file_descriptor_set.SerializeToString()
                )
                file_descriptor_set_file.close()

            protoc_args.append('--descriptor_set_in=file_descriptor_set')

            protoc_args.append(f'{file.name}')

            returncode = grpc_tools_protoc.main(protoc_args)

            if returncode != 0:
                print(
                    'Failed to generate protobuf and gRPC code for Python adaptor',
                    file=sys.stderr,
                )
                sys.exit(-1)

            with open(
                f"{file.name.replace('.proto', '_pb2.py')}",
                "r",
            ) as pb2_py, open(
                f"{file.name.replace('.proto', '_pb2_grpc.py')}",
                "r",
            ) as pb2_grpc_py:
                return (pb2_py.read(), pb2_grpc_py.read())


class NodejsResembleProtocPlugin(ResembleProtocPlugin):

    @staticmethod
    def plugin_specific_data() -> PluginSpecificData:
        return PluginSpecificData(
            template_filename="resemble.ts.j2",
            output_filename_suffix="_rsm.ts",
            supported_features=["reader", "writer"]
        )

    def template_render(
        self,
        proto_file: FileDescriptorProto,
        template_data: dict[str, Any],
    ) -> str:
        # We embed the the `*_pb2.py`, `*_pb2_grpc.py`, and `*_rsm.py`
        # "files" as encoded strings in the generated `*_rsm.ts` file
        # so that they can be imported into Python when at runtime.
        pb2_py, pb2_grpc_py = protoc(self.pool.FindFileByName(proto_file.name))

        template_data['base64_gzip_pb2_py'] = base64.b64encode(
            gzip.compress(pb2_py.encode('utf-8'))
        ).decode('utf-8')

        template_data['base64_gzip_pb2_grpc_py'] = base64.b64encode(
            gzip.compress(pb2_grpc_py.encode('utf-8'))
        ).decode('utf-8')

        template_data['base64_gzip_rsm_py'] = base64.b64encode(
            gzip.compress(
                PythonResembleProtocPlugin().template_render(
                    proto_file, template_data
                ).encode('utf-8')
            )
        ).decode('utf-8')

        return super().template_render(proto_file, template_data)


# This is a separate function (rather than just being in `__main__`) so that we
# can refer to it as a `script` in our `pyproject.rsm.toml` file.
def main():
    try:
        NodejsResembleProtocPlugin.execute()
    except UserProtoError as error:
        terminal.fail(str(error))


if __name__ == '__main__':
    main()
