import asyncio
import google
import grpc
import json
import os
import resemble.templates.tools as template_tools
import sys
import threading
import traceback
from collections import defaultdict
from google.protobuf.struct_pb2 import Struct
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from resemble.aio.internals.middleware import Middleware
from resemble.aio.state_managers import StateManager
from resemble.aio.types import ActorId, ServiceName
from resemble.v1alpha1.inspect import inspect_pb2_grpc
from resemble.v1alpha1.inspect.inspect_pb2 import (
    GetAllActorsRequest,
    GetAllActorsResponse,
)
from typing import AsyncIterator, Optional


class InspectServicer(inspect_pb2_grpc.InspectServicer):

    @staticmethod
    async def run_static_server(*, port: int, uri: str):
        template_input = {'uri': uri}
        path_to_template = os.path.join(
            os.path.dirname(__file__), 'index.html.j2'
        )
        index = template_tools.render_template(
            path_to_template, template_input
        )

        with open(
            os.path.join(os.path.dirname(__file__), 'index.html'), 'w'
        ) as file:
            file.write(index)

        DIRECTORY = os.path.dirname(__file__)

        class InspectServer(SimpleHTTPRequestHandler):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=DIRECTORY, **kwargs)

            def log_message(self, format, *args):
                # TODO(benh): if requested do more verbose logging.
                pass

        static_file_server = ThreadingHTTPServer(('', port), InspectServer)

        def serve_until_shutdown():
            with static_file_server as server:
                server.serve_forever()

        thread = threading.Thread(target=serve_until_shutdown)
        thread.start()

        # Now wait "forever" until we get cancelled in which case
        # shutdown the static file server.
        try:
            forever = asyncio.Event()
            await forever.wait()
        finally:
            static_file_server.shutdown()
            thread.join()

    def __init__(
        self,
        state_manager: StateManager,
        middleware_by_service_name: dict[ServiceName, Middleware],
    ):
        self._state_manager = state_manager
        self._middleware_by_service_name = middleware_by_service_name

    def add_to_server(self, server: grpc.aio.Server) -> None:
        inspect_pb2_grpc.add_InspectServicer_to_server(self, server)

    async def GetAllActors(
        self,
        request: GetAllActorsRequest,
        grpc_context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[GetAllActorsResponse]:
        # Dictionary representing the services and actors that we will
        # convert to JSON.
        services_and_actors: defaultdict[ServiceName,
                                         dict[ActorId,
                                              object]] = defaultdict(dict)

        # Event indicating that our dictionary has changed and we
        # should send another JSON version of it over the network.
        services_and_actors_modified = asyncio.Event()

        async def watch_actor(service: ServiceName, actor_id: ActorId):
            """Helper that watches for state updates on a specific actor."""
            middleware: Optional[
                Middleware] = self._middleware_by_service_name.get(service)

            if middleware is None:
                raise ValueError(f"Unknown service '{service}'")

            # For every state update, save a representation of the
            # state that can be converted into JSON.
            async for state in middleware.inspect(actor_id):
                # We convert our message to JSON, and then back to an
                # `object`, so that when we do the final conversion to
                # JSON we'll only have the fields from the initial
                # conversion.
                services_and_actors[service][actor_id] = json.loads(
                    google.protobuf.json_format.MessageToJson(
                        state,
                        preserving_proto_field_name=True,
                        ensure_ascii=True,
                    )
                )
                services_and_actors_modified.set()

        async def watch_actors():
            """Helper that watches for updates from the state manager for the set
               of running actors."""
            # Tasks that are running our `watch_actor(...)` helper.
            watch_actor_tasks: defaultdict[ServiceName, dict[
                ActorId, asyncio.Task]] = defaultdict(dict)

            try:
                async for actors in self._state_manager.actors():
                    # Start watching any actors that we aren't already watching.
                    for (service, actor_ids) in actors.items():
                        for actor_id in actor_ids:
                            if actor_id not in watch_actor_tasks[service]:
                                watch_actor_tasks[service][
                                    actor_id] = asyncio.create_task(
                                        watch_actor(service, actor_id)
                                    )

                    # TODO(benh): stop watching any actors that we are
                    # already watching.
                    for service in watch_actor_tasks:
                        for actor_id in watch_actor_tasks[service]:
                            if service not in actors or actor_id not in actors[
                                service]:
                                raise NotImplementedError(
                                    'Removing actors is not yet implemented'
                                )
            finally:
                # Clean up after ourselves and stop watching actors.
                for tasks in watch_actor_tasks.values():
                    for task in tasks.values():
                        task.cancel()

                    await asyncio.wait(
                        tasks.values(),
                        return_when=asyncio.ALL_COMPLETED,
                    )

        watch_actors_task = asyncio.create_task(watch_actors())

        try:
            while True:
                await services_and_actors_modified.wait()
                services_and_actors_modified.clear()
                actors = Struct()
                actors.update(services_and_actors)
                yield GetAllActorsResponse(actors=actors)
        finally:
            # Clean up after ourselves and stop watching for new
            # actors (which also will stop watching individual
            # actors).
            try:
                watch_actors_task.cancel()
                await watch_actors_task
            except asyncio.CancelledError:
                pass
            except:
                # Print a stacktrace here but don't bother raising as
                # we don't care about this task any more.
                print(
                    'Failed trying to watch for new/removed actors',
                    file=sys.stderr
                )
                traceback.print_exc()
