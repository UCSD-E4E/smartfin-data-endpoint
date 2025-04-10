'''Data API
'''
import logging
import signal
from asyncio import Event
from typing import List

from prometheus_client import start_http_server
from tornado.web import Application, URLSpec

from smartfin_data_api.metrics import system_monitor_thread


class Service:
    def __init__(self):
        self._log = logging.getLogger('Service')
        self.stop_event = Event()
        signal.signal(signal.SIGTERM, lambda x, y: self.stop_event.set())

        routes: List[URLSpec] = [

        ]
        self._webapp = Application(
            routes
        )
    
    async def run(self):
        start_http_server(9090)
        self._webapp.listen(80)
        system_monitor_thread.start()

        self._log.info('Service started')
        
        while not self.stop_event.is_set():
            await self.stop_event.wait(1)
        