import asyncio
import json
import os

from async_generator import aclosing
from jupyterhub.apihandlers import default_handlers
from jupyterhub.apihandlers.users import APIHandler
from jupyterhub.utils import iterate_until
from outpostspawner.api_flavors_update import async_get_flavors
from tornado import web
from tornado.iostream import StreamClosedError

from .utils import get_general_spawn_event


class UserSpawnNotificationAPIHandler(APIHandler):
    """EventStream handler for active spawns for a specific user"""

    keepalive_interval = 8

    def get_content_type(self):
        return "text/event-stream"

    async def send_event(self, event):
        try:
            self.write(f"data: {json.dumps(event)}\n\n")
            await self.flush()
        except StreamClosedError:
            self.log.warning("Stream closed while handling %s", self.request.uri)
            # raise Finish to halt the handler
            raise web.Finish()

    def initialize(self):
        self._finish_future = asyncio.Future()
        self._generator_future = asyncio.Future()

    def on_finish(self):
        self._finish_future.set_result(None)

    async def keepalive(self):
        """Write empty lines periodically

        to avoid being closed by intermediate proxies
        when there's a large gap between events.
        """
        while not (self._finish_future.done()):
            try:
                self.write("\n\n")
                await self.flush()
            except (StreamClosedError, RuntimeError):
                return

            await asyncio.wait([self._finish_future], timeout=self.keepalive_interval)

    async def get_event_data(self, user):
        if user is None:
            return {}
        flavors = await async_get_flavors(self.log, user)
        spawners = user.spawners.values()
        event_data = {
            # Set active spawners as event data
            "spawning": [s.name for s in spawners if s.pending == "spawn"],
            "stopping": [s.name for s in spawners if s.pending == "stop"],
            "active": [s.name for s in spawners if s.active],
            "stopped": [s.name for s in spawners if not s.active],
            "stoppedall": [
                s.name for s in spawners if not s.active or s.pending == "stop"
            ],
            "outpostflavors": flavors,
        }
        return event_data

    async def event_generator(self, user):
        general_spawn_event = get_general_spawn_event()
        while not (self._generator_future.done() or self._finish_future.done()):
            await general_spawn_event.wait()
            event_data = await self.get_event_data(user)
            yield event_data
            general_spawn_event.clear()

    async def event_generator_wrap(self, user):
        # This will always yield at least one argument
        event_data = await self.get_event_data(user)
        yield event_data

        async with aclosing(self.event_generator(user)) as events:
            async for event in events:
                yield event

    async def stop_after_n_seconds(self):
        sleep_timer = int(os.environ.get("SSESTOPTIMER", "30"))
        await asyncio.sleep(sleep_timer)
        self._generator_future.set_result(None)

    # @needs_scope('read:servers')
    async def get(self, user_name):
        self.set_header("Cache-Control", "no-cache")
        user = self.find_user(user_name)

        # start sending keepalive to avoid proxies closing the connection
        asyncio.ensure_future(self.stop_after_n_seconds())
        asyncio.ensure_future(self.keepalive())

        async with aclosing(
            iterate_until(self._generator_future, self.event_generator_wrap(user))
        ) as events:
            try:
                async for event in events:
                    await self.send_event(event)
                    # Clear event after sending in case stream has been closed
            except asyncio.CancelledError:
                pass


default_handlers.append(
    (r"/api/users/([^/]+)/notifications/spawners", UserSpawnNotificationAPIHandler)
)
