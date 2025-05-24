'''Data API
'''
import datetime as dt
import logging
import signal
from asyncio import Event
from typing import List

import pytz
from prometheus_client import start_http_server
from tornado.web import Application, URLSpec

from smartfin_data_api.endpoints import HomePageHandler, VersionHandler
from smartfin_data_api.metrics import system_monitor_thread


class Service:
    """Service class
    """
    # pylint: disable=too-few-public-methods
    # Main entrypoint
    def __init__(self):
        self._log = logging.getLogger('Service')
        self.stop_event = Event()
        signal.signal(signal.SIGTERM, lambda x, y: self.stop_event.set())

        start_time = dt.datetime.now(tz=pytz.UTC)

        routes: List[URLSpec] = [
            URLSpec(
                pattern=r'/$',
                handler=HomePageHandler,
                kwargs={'start_time': start_time}
            ),
            URLSpec(
                pattern=r'/version$',
                handler=VersionHandler
            )
        ]
        self._webapp = Application(
            routes
        )

    async def run(self):
        """Run entrypoing
        """
        start_http_server(9090)
        self._webapp.listen(80)
        system_monitor_thread.start()

        self._log.info('Service started')

        await self.stop_event.wait()
