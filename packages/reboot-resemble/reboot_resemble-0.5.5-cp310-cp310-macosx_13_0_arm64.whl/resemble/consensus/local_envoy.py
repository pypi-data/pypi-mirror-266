from __future__ import annotations

import asyncio
import grpc
import grpc.aio
import json
import logging
import os
import resemble.aio.signals as signals
import resemble.templates.tools as template_tools
import shutil
import signal
import socket
import subprocess
import tempfile
import threading
import traceback
from grpc_health.v1 import health_pb2, health_pb2_grpc
from pathlib import Path
from resemble.aio.servicers import Routable
from resemble.helpers import (
    base64_serialize_proto_descriptor_set,
    generate_proto_descriptor_set,
)
from resemble.settings import (
    DEFAULT_SECURE_PORT,
    ENVOY_PROXY_IMAGE,
    EVERY_LOCAL_NETWORK_ADDRESS,
)
from respect.logging import get_logger
from typing import Optional

logger = get_logger(__name__)
logger.setLevel(logging.WARNING)

# The number of Envoy log lines we'll keep in memory for debugging purposes.
MAX_LOG_LINES = 100

# Error message we can use to help debugging.
CONTAINER_REMOVED_BEFORE_LOGGING_ERROR = (
    'Error response from daemon: can not get logs from container which is dead or marked for removal\n'
)

LOCALHOST_DIRECT_CRT = os.path.join(
    os.path.dirname(__file__), 'localhost.direct.crt'
)

# Run Envoy on this port inside the container.
# The published port, determined either by the user or picked by Docker,
# is forwarded to this static internal port.
ENVOY_INTERNAL_PORT = DEFAULT_SECURE_PORT

if not os.path.isfile(LOCALHOST_DIRECT_CRT):
    raise FileNotFoundError(
        "Expecting 'localhost.direct.crt' at path "
        f"'{LOCALHOST_DIRECT_CRT}'"
    )

LOCALHOST_DIRECT_KEY = os.path.join(
    os.path.dirname(__file__), 'localhost.direct.key'
)

if not os.path.isfile(LOCALHOST_DIRECT_KEY):
    raise FileNotFoundError(
        "Expecting 'localhost.direct.key' at path "
        f"'{LOCALHOST_DIRECT_KEY}'"
    )

RESEMBLE_LOCAL_ENVOY_DEBUG: bool = os.environ.get(
    'RESEMBLE_LOCAL_ENVOY_DEBUG',
    'false',
).lower() == 'true'


async def _cancel_task(task: asyncio.Task) -> None:
    if task.done():
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


class LocalEnvoy:
    """Wrapper class for setting up a local Envoy outside of Kubernetes. This
    runs Envoy in a Docker container, not in process.

    The user of this class is responsible for calling .start() and .stop().

    Args:
        - proxied_server_host: the host address of the server Envoy proxies to.
        - proxied_server_port: the port address of the server Envoy proxies to.
        - proxied_server_websocket_port: the websocket port address of the
                                         server Envoy proxies to.
        - servicers: the servicers to proxy.
        - published_port: The 'self._published_port' is the port that the
                                host machine holds and that we'll forward to
                                the Envoy container. We assume only 2 cases for
                                'self._published_port':
                                    1. 0: we don't know the port yet and we'll
                                    have to ask Docker later
                                    2. non-0: we know the port and we'll use it
                                    directly and forward it to the Envoy
                                    container.
    Sample use:
        envoy = LocalEnvoy(
            proxied_server_host='127.0.0.1',
            proxied_server_port=5001,
            proxied_server_websocket_port=5002,
            servicers=[MyGreeterServicer]
        )
        await envoy.start()
        await envoy.stop()
    """

    # LocalEnvoy needs to know something about Resemble servicers in the
    # current implementation.
    # TODO: create a generic abstraction, e.g. LocalEnvoyBase, that doesn't
    # know anything about Resemble.
    def __init__(
        self,
        *,
        application_id: str,
        proxied_server_host: str,
        proxied_server_port: int,
        proxied_server_websocket_port: int,
        routables: list[Routable],
        published_port: int = 0,
    ):
        self._published_port: int = published_port
        self._container_id: Optional[str] = None

        proto_descriptor_set = generate_proto_descriptor_set(routables)

        base64_encoded_proto_desc_set = base64_serialize_proto_descriptor_set(
            proto_descriptor_set
        )

        service_names = [r.service_name() for r in routables]

        # Generate envoy config and write it to temporary files that get
        # cleaned up on .stop(). We copy all files without their metadata
        # to ensure that they are readable by the envoy user.
        self._tmp_envoy_dir = tempfile.TemporaryDirectory()
        self._tmp_envoy_config = f'{self._tmp_envoy_dir.name}/envoy.yaml'
        self._tmp_envoy_crt = f'{self._tmp_envoy_dir.name}/localhost.direct.crt'
        self._tmp_envoy_key = f'{self._tmp_envoy_dir.name}/localhost.direct.key'

        path_to_template = os.path.join(
            os.path.dirname(__file__), 'local_envoy_config.yaml.j2'
        )
        Path(self._tmp_envoy_config).write_text(
            self._generate_envoy_yaml(
                proxied_server_host=proxied_server_host,
                proxied_server_port=proxied_server_port,
                proxied_server_websocket_port=proxied_server_websocket_port,
                proto_descriptor_bin=base64_encoded_proto_desc_set,
                template_path=path_to_template,
                application_id=application_id,
                service_names=service_names,
                envoy_port=ENVOY_INTERNAL_PORT,
            )
        )
        shutil.copyfile(LOCALHOST_DIRECT_CRT, self._tmp_envoy_crt)
        shutil.copyfile(LOCALHOST_DIRECT_KEY, self._tmp_envoy_key)

        # Open a server socket that listens for connections from the
        # 'local_envoy_nanny' so that in the event our process is
        # killed abruptly the nanny will get an EOF (or error) and
        # send a SIGTERM to envoy which should stop the container.
        self._nanny_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._nanny_socket.bind((EVERY_LOCAL_NETWORK_ADDRESS, 0))

        # Indicator of whether or not we are stopping. Used at the
        # least by the nanny server thread to avoid spamming stderr
        # with exceptions when the server socket gets closed.
        self._stopping = False

        # A background task that follows the logs of the Envoy container,
        # possibly forwarding them to the `self._unprocessed_log_lines`, and
        # handles container termination by (if needed) dumping some logs.
        self._follow_logs_and_handle_termination_task: Optional[asyncio.Task
                                                               ] = None

        # A list of the latest log lines from the Envoy container.
        self._latest_log_lines: list[str] = []

        # A queue containing log lines of the Envoy container, used to find the
        # Envoy admin endpoint in those logs. Once set to `None` it means we're
        # no longer interested in the logs for that purpose.
        self._unprocessed_log_lines: Optional[asyncio.Queue[str]
                                             ] = asyncio.Queue()

    @property
    def port(self) -> int:
        """Returns the port of the Envoy proxy.
        """
        if self._published_port == 0:
            raise ValueError(
                'LocalEnvoy.start() must be called before you can get the port'
            )
        return self._published_port

    async def start(self) -> None:
        """Starts Envoy in a container on an unused port. The port started on
        is retrieved and saved.
        """

        # There is a race between when we've successfully started the
        # Envoy container and when we get the nanny started where a
        # container may get orphaned if our process gets terminated or
        # our coroutine is cancelled.
        #
        # We minimize the likelihood of an orphaned container here by
        # registering a cleanup handler to be executed when a SIGINT
        # or SIGTERM signal is raised that will stop the container (if
        # it was started).
        def stop_on_sigterm_sigquit_exception():
            if self._container_id is not None:
                # NOTE: deliberately not using `asyncio` in here as
                # this may be run within an interrupt handler.
                subprocess.run(
                    ['docker', 'stop', self._container_id],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

        with signals.cleanup_on_raise(
            [signal.SIGTERM, signal.SIGQUIT],
            handler=stop_on_sigterm_sigquit_exception,
        ):
            try:
                # Shell out to docker to start envoy and return a container id.
                await self._docker_run_envoy()

                # Now 'docker exec' the local envoy nanny inside the
                # container we just started with envoy.
                await self._exec_local_envoy_nanny()
            except:
                stop_on_sigterm_sigquit_exception()
                raise

    async def stop(self) -> None:
        """Stop the Envoy container and cleans up temp files.
        """
        self._stopping = True
        if (
            self._container_id is None or
            self._follow_logs_and_handle_termination_task is None
        ):
            raise RuntimeError('.start() must be called before .stop()')

        try:
            docker_stop = await asyncio.create_subprocess_exec(
                'docker',
                'stop',
                self._container_id,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await docker_stop.wait()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f'LocalEnvoy .stop() failed with: {str(e)}; '
                'this likely means that .start() was unsuccessful'
            ) from e
        finally:
            # Now that Envoy has been told to stop (or has already stopped), we
            # can wait for it to terminate. That will also print logs if Envoy
            # terminated with an error.
            await self._follow_logs_and_handle_termination_task

            self._tmp_envoy_dir.cleanup()
            self._nanny_socket.close()

    @staticmethod
    async def _async_check_output(*args, **kwargs) -> str:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs,
        )

        stdout_data, _ = await process.communicate()
        return stdout_data.decode()

    async def _get_forwarded_local_port_from_docker(
        self,
        container_id: str,
        container_port: int,
    ):
        """If Docker dynamically mapped the local port to the container 'envoy'
        port, we need to know that port and we ask Docker via 'docker inspect'.
        """
        json_inspect: str = await LocalEnvoy._async_check_output(
            'docker',
            'inspect',
            container_id,
            '--format',
            "'{{json .NetworkSettings.Ports}}'",
        )
        # Cut the leading and trailing single quotes.
        json_inspect = json_inspect.strip()[1:-1]
        ports_parsed = json.loads(json_inspect.strip())
        if len(ports_parsed) == 0:
            raise RuntimeError(
                "Failed to inspect Envoy Docker container" + (
                    "; try setting the env var 'RESEMBLE_LOCAL_ENVOY_DEBUG=true' "
                    "to help debug" if not RESEMBLE_LOCAL_ENVOY_DEBUG else ""
                )
            )

        return ports_parsed[f'{container_port}/tcp'][0]['HostPort']

    async def _wait_for_grpc_health_check_through_envoy(self):
        while True:
            async with grpc.aio.secure_channel(
                # Calling a 'healthcheck.*' domain name as a workaround on a
                # gRPC bug that produces log message error about not matching
                # the entry (*.localhost.direct) in the certificate.
                # See https://github.com/reboot-dev/respect/issues/2305
                f'healthcheck.localhost.direct:{self._published_port}',
                grpc.ssl_channel_credentials(),
            ) as channel:
                stub = health_pb2_grpc.HealthStub(channel)
                request = health_pb2.HealthCheckRequest()
                try:
                    response = await stub.Check(request)
                    if response.status == health_pb2.HealthCheckResponse.SERVING:
                        break
                except grpc.aio.AioRpcError:
                    pass

    async def _docker_run_envoy(self) -> None:
        """Checks that Docker is installed and starts up Envoy in a container.
        """
        try:
            await LocalEnvoy._async_check_output('docker', '--version')
        except Exception as e:
            raise RuntimeError(
                'Docker likely not installed; install docker to use LocalEnvoy: '
                f'`docker --version` failed with {str(e)}'
            )

        if self._published_port != 0:
            # We're coming up on a specific port. That means there's a chance we
            # could clash with an old, orphaned Envoy - if there's still one
            # around. Check if we have an orphaned Envoy from a previous run and
            # stop it first.
            #
            # This may stop an envoy that is running because a user has an `rsm
            # dev` (or `rsm serve`, etc) running, e.g., in a different terminal.
            orphaned_container_ids_lines = await LocalEnvoy._async_check_output(
                'docker',
                'ps',
                '--filter',
                f'label=RESEMBLE_LOCAL_ENVOY_PORT={self._published_port}',
                '--format="{{.ID}}"',
            )

            orphaned_container_ids = [
                line.strip('"')
                for line in orphaned_container_ids_lines.split('\n')
            ]
            for orphaned_container_id in orphaned_container_ids:
                if orphaned_container_id == '':
                    continue

                # Stopping the container may take a little while, so tell the
                # user what's going on so they don't think we're hanging.
                logger.warning(
                    'Performing cleanup of an orphaned Envoy container...'
                )

                docker_stop = await asyncio.create_subprocess_exec(
                    'docker',
                    'stop',
                    orphaned_container_id,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )

                try:
                    # Just wait for the process to exit; we don't care about the
                    # `returncode` and the container might also have terminated
                    # on it's own before we called stop!
                    await docker_stop.wait()
                finally:
                    # In the event we were cancelled or an exception was raised
                    # make sure the process has been terminated so we don't
                    # leave around any orphans (the exact thing this code is
                    # trying to clean up from!)
                    if docker_stop.returncode is None:
                        try:
                            docker_stop.terminate()
                            # Wait for the process to terminate, but don't wait
                            # too long.
                            try:
                                await asyncio.wait_for(
                                    docker_stop.wait(), timeout=5.0
                                )
                            except asyncio.TimeoutError:
                                # The process still hasn't gracefully
                                # terminated. Kill the process. There's no way
                                # to ignore that signal, so we can safely do a
                                # non-timeout-based `await` for it to finish.
                                docker_stop.kill()
                                await docker_stop.wait()
                        except ProcessLookupError:
                            # The process already exited. That's fine.
                            pass
                    logger.warning('... Done!')

        # NOTE: we pass each necessary file individually than a single
        # directory that includes all of the files because symlinks in
        # dirctories are not accessible from within a Docker container
        # and at least at the time of writing this comment Bazel
        # sometimes uses symlinks for files.

        local_envoy_nanny_path = os.path.join(
            os.path.dirname(__file__), 'local_envoy_nanny'
        )
        if not os.path.isfile(local_envoy_nanny_path):
            raise FileNotFoundError(
                "Expecting 'local_envoy_nanny' executable at path "
                f"'{local_envoy_nanny_path}'"
            )

        local_envoy_run_command = [
            'docker',
            'run',
            '--label',
            f'RESEMBLE_LOCAL_ENVOY_PORT={self._published_port}',
            '--detach',
        ]

        # When trying to debug why Envoy might be crashing we might
        # miss the logs if Docker removes the container too
        # quickly. Thus, we omit the '--rm' and let the user know that
        # they'll be responsible for removing the container.
        if RESEMBLE_LOCAL_ENVOY_DEBUG:
            print(
                '\n'
                '\n'
                '\n'
                'RESEMBLE_LOCAL_ENVOY_DEBUG is "true" and thus you are '
                'responsible for removing any Envoy containers! '
                '(Consider using `docker container prune`)'
                '\n'
                '\n'
                '\n'
            )

        else:
            local_envoy_run_command += [
                '--rm',
            ]

        if self._published_port != 0:
            local_envoy_run_command += [
                # Publish 'ENVOY_INTERNAL_PORT' to 'self._published_port'.
                '-p'
                f'{self._published_port}:{ENVOY_INTERNAL_PORT}',
            ]
        else:
            local_envoy_run_command += [
                # If user didn't specify a port, we'll let Docker pick a
                # random port and we'll ask Docker later. But to be able to
                # access the port from the host machine, we need to publish
                # all exposed ports, so we use '--expose' and '--publish-all'.
                # We will then ask Docker for the port that was mapped to
                # 'ENVOY_INTERNAL_PORT'.
                '--expose',
                f'{ENVOY_INTERNAL_PORT}',
                '--publish-all',
            ]

        local_envoy_run_command += [
            '--add-host=host.docker.internal:host-gateway',
            f'--volume={self._tmp_envoy_config}:/etc/envoy/envoy.yaml:ro',
            f'--volume={self._tmp_envoy_crt}:/etc/envoy/localhost.direct.crt',
            f'--volume={self._tmp_envoy_key}:/etc/envoy/localhost.direct.key',
            f'--volume={local_envoy_nanny_path}:/local_envoy_nanny',
            # NOTE: invariant here that the default entry point of the
            # container will run envoy at PID 1 because that is what
            # the 'local_envoy_nanny' will send a SIGTERM to in the
            # event of orphaning.
            ENVOY_PROXY_IMAGE,
            '-c',
            '/etc/envoy/envoy.yaml',
            # We need to disable hot restarts in order to run multiple
            # proxies at the same time otherwise they will clash
            # trying to create a domain socket. See
            # https://www.envoyproxy.io/docs/envoy/latest/operations/cli#cmdoption-base-id
            # for more details.
            '--disable-hot-restart',
        ]

        # TODO(riley): even if we get back a container_id, it doesn't mean
        # everything is good. Envoy may have crashed. Poll this process for
        # a non-0 exit code so we can notify the user that
        # there is likely an issue with their proto descriptor.
        container_id = await LocalEnvoy._async_check_output(
            *local_envoy_run_command
        )
        self._container_id = container_id.strip()

        # Start a task that will handle logging in case of (unexpected) Envoy
        # termination.
        self._follow_logs_and_handle_termination_task = asyncio.create_task(
            self._follow_logs_and_handle_termination()
        )

        if self._published_port == 0:
            self._published_port = await self._get_forwarded_local_port_from_docker(
                self._container_id,
                ENVOY_INTERNAL_PORT,
            )

        assert self._published_port != 0

        await self._wait_for_grpc_health_check_through_envoy()

    @staticmethod
    def _generate_envoy_yaml(
        *,
        proxied_server_host: str,
        proxied_server_port: int,
        proxied_server_websocket_port: int,
        proto_descriptor_bin: bytes,
        template_path: str,
        application_id: str,
        service_names: list[str],
        envoy_port: int,
    ) -> str:
        """Takes an Envoy config Jinja template, fills its values and returns a
        yaml string.
        """
        # Inject the Lua filter that handles "mangled" HTTP paths that
        # need to be translated into something that can be routed.
        mangled_http_path_filter_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'controller',
            'mangled_http_path_filter.lua',
        )

        with open(
            mangled_http_path_filter_path, 'r'
        ) as mangled_http_path_filter_file:
            mangled_http_path_filter = mangled_http_path_filter_file.read()

        template_input = {
            'proxied_server_host': proxied_server_host,
            'proxied_server_port': proxied_server_port,
            'proxied_server_websocket_port': proxied_server_websocket_port,
            'application_id': application_id,
            'services': service_names,
            # We have to turn the base64 encoded proto descriptor into a string
            # using .decode() because Jinja can only handle str types.
            'proto_descriptor_bin': proto_descriptor_bin.decode(),
            'envoy_port': envoy_port,
            'mangled_http_path_filter': mangled_http_path_filter,
        }

        return template_tools.render_template_path(
            template_path, template_input
        )

    async def _exec_local_envoy_nanny(self):
        # Start listening for the 'local_envoy_nanny' to connect. We
        # use a daemon thread which ignores any errors after we've
        # stopped so that we don't spam stderr with an exception.
        self._nanny_socket.listen(1)

        def accept():
            clients: list[socket.socket] = []
            try:
                while True:
                    client, address = self._nanny_socket.accept()
                    clients.append(client)
            except Exception as e:
                if not self._stopping:
                    raise RuntimeError(
                        'Failed to accept on "nanny socket; '
                        '*** ENVOY MAY BECOME AN ORPHANED CONTAINER ***'
                    ) from e

        threading.Thread(target=accept, daemon=True).start()

        _, port = self._nanny_socket.getsockname()

        # Run the nanny which will connect back to our server socket!
        #
        # We do this by forking of a process that starts `local_envoy_nanny` in
        # the docker container of the envoy we just started.
        # We then create an `asyncio` task that watches the local_envoy_nanny
        # process and waits for it to terminate. Should it terminate early with
        # a non-zero exit code we'll raise an error and stop the container.
        local_envoy_nanny_launcher = await asyncio.create_subprocess_exec(
            'docker',
            'exec',
            f'{self._container_id}',
            '/local_envoy_nanny',
            'host.docker.internal',
            f'{port}',
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        async def local_envoy_nanny_launcher_watchdog():
            status_code = await local_envoy_nanny_launcher.wait()

            log = logger.warning if status_code != 0 else logger.debug

            log('Local envoy nanny exited with status code %d', status_code)
            if status_code != 0:
                stdout_data, _ = await local_envoy_nanny_launcher.communicate()
                log('Output from local_envoy_nanny: %s', stdout_data.decode())

                error = RuntimeError(
                    f"Failed to run 'local_envoy_nanny': {stdout_data.decode()}; "
                    '*** ENVOY MAY BECOME AN ORPHANED CONTAINER ***'
                )
                try:
                    # Try and stop the container so we don't have orphans
                    # since our nanny won't be there for them!
                    await self.stop()
                except Exception as e:
                    raise error from e
                else:
                    raise error

        # Launch watchdog task in the background.
        # ISSUE(https://github.com/reboot-dev/respect/issues/2312): it would be
        # could if we could propagate the exception from the watchdog task to
        # the main task. Storing a handle to the task and having a
        # synchronization point such as a `wait()` method would be a way to
        # achieve this.
        _ = asyncio.create_task(local_envoy_nanny_launcher_watchdog())

    async def _follow_logs_and_handle_termination(self) -> None:
        """Waits for the Envoy container to terminate and its logs to be
        collected. Will print the logs if Envoy terminated unsuccessfully.
        """
        # Start a task that waits for the Envoy container to terminate.
        # This must be done while Envoy is still running.
        wait_for_termination_task = asyncio.create_task(
            self._wait_for_termination()
        )

        # Start a task that follows the logs of the Envoy container.
        follow_logs_task = asyncio.create_task(self._follow_logs())

        # Wait for both of these tasks to complete; that indicates that Envoy
        # has terminated, and that we have all of the logs.
        try:
            envoy_returncode, _ = await asyncio.gather(
                wait_for_termination_task, follow_logs_task
            )
        except asyncio.CancelledError:
            # We're being cancelled. That might mean that Envoy is still
            # running, but we're no longer interested in its logs. Our `finally`
            # block will cancel the tasks if they're still running; there's
            # nothing else we need to do.
            raise
        except Exception as e:
            # Something went wrong while waiting for the tasks to complete.
            # If Envoy crashes that should NOT cause these tasks to crash;
            # rather there is some internal error that causes us to not be able
            # to follow Envoy's logs or wait for it to terminate.
            logger.error(
                "Failed to track Envoy's health. Please report this "
                "bug to the maintainers.\n"
                "\n"
                f"{traceback.format_exc()}"
            )
            # Re-raise the error. We're in undefined-behavior territory with
            # this internal error, so it's safest just to crash. That also
            # greatly increases the odds that tests will notice this issue.
            raise e
        finally:
            # If any of the tasks are still running at this point, cancel them.
            await _cancel_task(wait_for_termination_task)
            await _cancel_task(follow_logs_task)

        # Envoy terminated and the logs have been collected. We print the logs
        # if Envoy terminated unsuccessfully.
        if envoy_returncode != 0:
            logger.error(
                f"Envoy terminated with exit code {envoy_returncode} (an error)\n"
                "\n"
                "Did you stop Envoy manually or did you attempt to run another "
                "application using the same Envoy port and it just killed this one?\n"
                + (
                    "\n"
                    f"----- ENVOY LOGS (last {MAX_LOG_LINES} lines) -----\n"
                    "\n"
                    # The log lines all end with a newline, so we don't need
                    # to add another one.
                    f"{''.join(self._latest_log_lines)}"
                    "\n"
                    "----- END ENVOY LOGS -----\n"
                    if not RESEMBLE_LOCAL_ENVOY_DEBUG else ""
                ) + (
                    "\n"
                    "\n"
                    "Try setting the env var 'RESEMBLE_LOCAL_ENVOY_DEBUG=true' "
                    "to get logs from the Docker Enovy container"
                    "\n"
                    "\n" if CONTAINER_REMOVED_BEFORE_LOGGING_ERROR in
                    self._latest_log_lines and not RESEMBLE_LOCAL_ENVOY_DEBUG
                    else ""
                )
            )

    async def _wait_for_termination(self) -> int:
        """Waits for the Envoy container to exit.

        This must be called while Envoy is still running.
        """
        assert self._container_id is not None
        wait_process = await asyncio.create_subprocess_exec(
            'docker',
            'wait',
            self._container_id,
            stdin=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.STDOUT,
            stdout=asyncio.subprocess.PIPE,
        )
        try:
            stdout, _ = await wait_process.communicate()
            if wait_process.returncode != 0:
                # This indicates that our 'docker wait' command failed; it doesn't
                # say anything about the status of the Envoy container.
                logger.error(
                    "Failed to wait for Envoy termination\n"
                    "\n"
                    "'docker wait' output:\n"
                    "\n"
                    f"{stdout.decode()}"
                )
                raise RuntimeError(
                    f'Unable to get exit code for container {self._container_id}'
                )
            # A successful 'docker wait' process has a return code of 0, and prints
            # Envoy's return code (0 or non-0) to its stdout.
            envoy_returncode = int(stdout.decode())
            return envoy_returncode

        finally:
            # We're done waiting for termination. Terminate the `wait` process
            # if it is still running.
            if wait_process.returncode is None:
                try:
                    wait_process.terminate()
                    # Wait for the process to terminate, but don't wait too long.
                    try:
                        await asyncio.wait_for(
                            wait_process.wait(), timeout=5.0
                        )
                    except asyncio.TimeoutError:
                        # The process still hasn't gracefully terminated. Kill the
                        # process. There's no way to ignore that signal, so we can
                        # safely do a non-timeout-based `await` for it to finish.
                        wait_process.kill()
                        await wait_process.wait()
                except ProcessLookupError:
                    # The process already exited. That's fine.
                    pass

    async def _follow_logs(self) -> None:
        """Runs a process that follows the logs of the given Docker container,
        storing the latest log lines in `self._unprocessed_log_lines`, and also
        "tee"ing them to `self._unprocessed_log_lines` if relevant.
        """
        assert self._container_id is not None

        # Start tailing Envoy's logs.
        process = await asyncio.create_subprocess_exec(
            'docker',
            'logs',
            '-f',
            self._container_id,
            stdin=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.STDOUT,
            stdout=asyncio.subprocess.PIPE,
        )

        try:
            # process.stdout should not be None since we set it to PIPE.
            assert process.stdout is not None

            async def read_stdout():
                # process.stdout will also not suddenly become None.
                assert process.stdout is not None
                while not process.stdout.at_eof():
                    yield await process.stdout.readline()

            async for line in read_stdout():
                decoded_line = line.decode()

                if RESEMBLE_LOCAL_ENVOY_DEBUG:
                    print(decoded_line)

                # We always accumulate the latest log line into `latest_logs`,
                # truncating it if it goes above the maximum number of lines
                # we want to keep around.
                self._latest_log_lines.append(decoded_line)

                if len(self._latest_log_lines) > MAX_LOG_LINES:
                    self._latest_log_lines.pop(0)

                # We also "tee" the log line into the
                # `self._unprocessed_log_lines` queue if still necessary
                # (determined by whether or not it is `None`).
                if self._unprocessed_log_lines is not None:
                    self._unprocessed_log_lines.put_nowait(decoded_line)

        finally:
            # We've either reached EOF or an exception (possibly due to
            # cancellation) has been raised. In any case, ensure the
            # log-following process has been terminated.
            try:
                process.terminate()
                # Wait for the process to terminate, but don't wait too long.
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    # The process still hasn't gracefully terminated. Kill the
                    # process. There's no way to ignore that signal, so we can
                    # safely do a non-timeout-based `await` for it to finish.
                    process.kill()
                    await process.wait()
            except ProcessLookupError:
                # The process already exited. That's fine.
                pass
