'''Data API
'''
import datetime as dt
import logging
import signal
from asyncio import Event
from threading import Thread
from typing import List

import pytz
from prometheus_client import start_http_server
from tornado.web import Application, URLSpec

from smartfin_data_api.config import settings
from smartfin_data_api.endpoints import (HomePageHandler, ParticleEventHandler,
                                         VersionHandler)
from smartfin_data_api.metrics import system_monitor_thread
from smartfin_data_api.postgres import PostgresSchema


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
            ),
            URLSpec(
                pattern=r'/api/v1/publish$',
                handler=ParticleEventHandler
            )
        ]
        self._webapp = Application(
            routes
        )
        with open(settings.postgres.password_file, 'r', encoding='utf-8') as handle:
            pg_password = handle.read(256)
        self._postgres_schema = PostgresSchema(
            host=settings.postgres.host,
            user=settings.postgres.user,
            password=pg_password,
            database=settings.postgres.database
        )

    async def run(self):
        """Run entrypoing
        """

        start_http_server(9090)
        migrate_thread = Thread(
            target=self._postgres_schema.migrate,
            name='DB setup/migrate'
        )
        migrate_thread.start()

        self._postgres_schema.wait_ready()
        migrate_thread.join()

        self._webapp.listen(80)
        system_monitor_thread.start()

        self._log.info('Service started')

        await self.stop_event.wait()
