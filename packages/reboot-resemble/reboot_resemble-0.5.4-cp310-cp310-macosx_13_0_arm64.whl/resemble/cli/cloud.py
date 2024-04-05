import argparse
from resemble.aio.aborted import Aborted
from resemble.aio.workflows import Workflow
from resemble.cli import terminal
from resemble.cli.rc import ArgumentParser, SubcommandParser
from resemble.cloud.api_keys import (
    InvalidAPIKeyBearerToken,
    parse_api_key_bearer_token,
)
from resemble.cloud.v1alpha1.application.application_rsm import Application
from resemble.cloud.v1alpha1.auth.auth_rsm import APIKey
from resemble.naming import (
    ApplicationName,
    QualifiedApplicationName,
    SpaceName,
    UserId,
    make_qualified_application_name,
)
from resemble.settings import CLOUD_APPLICATION_ID
from resemble.v1alpha1.errors_pb2 import (
    ActorAlreadyConstructed,
    ActorNotConstructed,
    PermissionDenied,
    Unauthenticated,
)

DEFAULT_RESEMBLE_CELL_ADDRESS = "prod1.resemble.cloud:9991"
DEFAULT_RESEMBLE_CLOUD_SECURE_CHANNEL = True

_API_KEY_FLAG = '--api-key'


def add_cloud_options(subcommand: SubcommandParser, *, api_key_required: bool):
    """Add flags common to all `rsm` commands that interact with the cloud."""
    # TODO: These should really be "global" flags, but that is not supported by
    # `rc.py`, afaict.

    subcommand.add_argument(
        '--cloud-cell-address',
        type=str,
        help="the endpoint of the Resemble cell hosting the Cloud API",
        default=DEFAULT_RESEMBLE_CELL_ADDRESS,
    )
    subcommand.add_argument(
        '--cloud-secure-channel',
        type=bool,
        help="whether to use a secure channel with the Resemble Cloud API",
        default=DEFAULT_RESEMBLE_CLOUD_SECURE_CHANNEL,
    )
    # TODO: This should probably be read from a file by default.
    subcommand.add_argument(
        _API_KEY_FLAG,
        type=str,
        help="the API key to use to connect to the Resemble Cloud API",
        default=None,
        required=api_key_required,
    )


def _application_gateway(application_id: str, cell_address: str) -> str:
    """
    Given a cell address (e.g. `prod1.resemble.cloud:9991`), returns the
    gateway for the given application (e.g. `a12345.prod1.resemble.cloud:9991`).
    """
    # TODO(rjh): once we support cross-application API calls, reconsider
    #            whether gateways should be application-specific, or whether
    #            there should be one gateway per cluster.
    return f"{application_id}.{cell_address}"


def _cloud_gateway(cloud_cell_address: str) -> str:
    return _application_gateway(CLOUD_APPLICATION_ID, cloud_cell_address)


def cloud_workflow(args) -> Workflow:
    api_key = args.api_key
    if api_key is None:
        terminal.fail(
            f"The {_API_KEY_FLAG} flag must be set in order to "
            "access the Resemble Cloud."
        )
    return Workflow(
        name="resemble-cli",
        bearer_token=api_key,
        gateway=_cloud_gateway(args.cloud_cell_address),
        secure_channel=args.cloud_secure_channel
    )


def register_cloud(parser: ArgumentParser):
    """Register the 'cloud' subcommand with the given parser."""

    def _add_common_flags(subcommand: SubcommandParser):
        """Adds flags common to every `rsm cloud` subcommand."""

        add_cloud_options(subcommand, api_key_required=True)

        subcommand.add_argument(
            '--name',
            type=str,
            required=True,
            help="name of the application",
        )

    up_subcommand = parser.subcommand('cloud up')
    _add_common_flags(up_subcommand)
    up_subcommand.add_argument(
        '--image-name',
        type=str,
        required=True,
        help='the Docker image name of the application; must be a public image',
    )

    down_subcommand = parser.subcommand('cloud down')
    _add_common_flags(down_subcommand)


async def _user_id_from_api_key(
    api_key: str,
    cloud_cell_address: str,
    secure_channel: bool,
) -> str:
    try:
        api_key_id, api_key_secret = parse_api_key_bearer_token(token=api_key)
    except InvalidAPIKeyBearerToken:
        # Note that we do not log the API key contents; they are a secret, which
        # we don't want to output to a log file (if any).
        terminal.fail(
            "Invalid API key shape (expected: "
            "'XXXXXXXXXX-XXXXXXXXXXXXXXXXXXXX')"
        )

    cloud_gateway = _cloud_gateway(cloud_cell_address)

    workflow = Workflow(
        name="user-id-from-api-key",
        gateway=cloud_gateway,
        secure_channel=secure_channel,
        # TODO(rjh): once APIKey reads the bearer token for `Authenticate`, use
        #            that instead of passing `secret` in the proto below.
    )

    try:
        return (
            await APIKey.lookup(api_key_id).Authenticate(
                workflow,
                secret=api_key_secret,
            )
        ).user_id
    except Aborted as aborted:
        match aborted.error:
            case ActorNotConstructed(  # type: ignore[misc]
            ) | PermissionDenied(  # type: ignore[misc]
            ) | Unauthenticated():  # type: ignore[misc]
                # Note that we do not log the API key contents; they
                # are a secret, which we don't want to output to a log
                # file (if any).
                terminal.fail("Invalid API key")
            case _:
                terminal.fail(f"Unexpected error: {aborted}")


async def _maybe_create_application(
    qualified_application_name: QualifiedApplicationName,
    cloud_cell_address: str,
    secure_channel: bool,
    api_key: str,
) -> Application.WeakReference:
    """
    Creates the Application with the given `qualified_application_name` if it
    doesn't exist yet.
    """
    cloud_gateway = _cloud_gateway(cloud_cell_address)

    # Use a separate workflow for `Create()`, since that call is allowed to fail
    # and will then leave its workflow unable to continue due to idempotency
    # uncertainty.
    workflow = Workflow(
        name="cloud-up-create-application",
        gateway=cloud_gateway,
        secure_channel=secure_channel,
        bearer_token=api_key,
    )
    try:
        application, _ = await Application.Create(
            qualified_application_name,
            workflow,
        )
        return application
    except Aborted as aborted:
        match aborted.error:
            case ActorAlreadyConstructed():  # type: ignore[misc]
                # That's OK; the Application already exists, so we
                # can just return a reference to it.
                return Application.lookup(qualified_application_name)
            case _:
                # Unexpected error, propagate it.
                raise


def _make_qualified_application_name(
    user_id: UserId,
    application_name: ApplicationName,
) -> QualifiedApplicationName:
    # During Alpha, the name of the space is always the same as the name of the
    # application.
    space_name: SpaceName = application_name
    return make_qualified_application_name(
        user_id, space_name, application_name
    )


async def cloud_up(args: argparse.Namespace):
    """Implementation of the 'cloud up' subcommand."""

    user_id = await _user_id_from_api_key(
        api_key=args.api_key,
        cloud_cell_address=args.cloud_cell_address,
        secure_channel=args.cloud_secure_channel,
    )
    qualified_application_name = _make_qualified_application_name(
        user_id=user_id,
        application_name=args.name,
    )

    workflow = Workflow(
        name="cloud-up",
        gateway=_cloud_gateway(args.cloud_cell_address),
        secure_channel=args.cloud_secure_channel,
        bearer_token=args.api_key,
    )

    try:
        application = await _maybe_create_application(
            qualified_application_name=qualified_application_name,
            cloud_cell_address=args.cloud_cell_address,
            secure_channel=args.cloud_secure_channel,
            api_key=args.api_key,
        )

        up_response = await application.Up(
            workflow,
            container_image_name=args.image_name,
        )
    except Aborted as aborted:
        # While `InvalidInputError` is declared for `Up()`, it is not
        # expected here as we'll fail earlier if `args.image_name` is
        # missing or invalid. And there aren't any declared errors for
        # `Create()`, so any error is unexpected. Most notably,
        # `PermissionDenied` can't happen, since the application we're
        # attempting to `Up()` is by definition owned by the user.
        terminal.fail(f"Unexpected error: {aborted}")

    application_id = up_response.application_id
    terminal.info(
        "Application starting; your application will be available at:\n\n"
        f"  {_application_gateway(application_id, args.cloud_cell_address)}"
        "\n"
    )

    # TODO(rjh): once the Cloud waits to resolve `up_response.up_task_id` until
    #            the application has completed deployment, await the completion
    #            of `up_response.up_task_id` here, and tell the user when their
    #            application is in fact up and running.


async def cloud_down(args: argparse.Namespace):
    """Implementation of the 'cloud down' subcommand."""

    user_id = await _user_id_from_api_key(
        api_key=args.api_key,
        cloud_cell_address=args.cloud_cell_address,
        secure_channel=args.cloud_secure_channel,
    )
    application_name = args.name
    qualified_application_name = _make_qualified_application_name(
        user_id=user_id,
        application_name=application_name,
    )

    workflow = Workflow(
        name="cloud-down",
        gateway=_cloud_gateway(args.cloud_cell_address),
        secure_channel=args.cloud_secure_channel,
        bearer_token=args.api_key,
    )

    try:
        await Application.lookup(qualified_application_name).Down(workflow)
    except Aborted as aborted:
        match aborted.error:
            case ActorNotConstructed():  # type: ignore[misc]
                terminal.fail(
                    f"User '{user_id}' does not have an application named "
                    f"'{application_name}'"
                )
            case _:
                # There are no other expected errors for
                # `Down()`. Most notably, `PermissionDenied` can't
                # happen, since the application we're attempting to
                # `Down()` is by definition owned by the user.
                terminal.fail(f"Unexpected error: {aborted}")

    terminal.info(
        f"Success. Your application '{application_name}' is being terminated."
    )

    # TODO(rjh): once the CLoud waits to resolve `down_response.down_task_id`
    #            until the application has terminated, await the completion of
    #            `down_response.down_task_id` here, and tell the user when their
    #            application has in fact terminated.
