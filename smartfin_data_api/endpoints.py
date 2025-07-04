'''Data API handlers
'''
import datetime as dt
import json
import logging
from http import HTTPStatus
from importlib.metadata import version

from tornado.web import RequestHandler

from smartfin_data_api import __version__
from smartfin_data_api.metrics import get_counter, get_summary
from smartfin_data_api.postgres import PostgresSchema

# pylint: disable=abstract-method, arguments-differ, attribute-defined-outside-init
# This is typical behavior for tornado

class BaseHandler(RequestHandler):
    """Base Handler for E4ESF
    """

    def _request_summary(self):
        remote_ip = self.request.headers.get('X-Real-IP') or \
            self.request.headers.get('X-Forwarded-For') or \
            self.request.remote_ip
        return f'{self.request.method} {self.request.uri} ({remote_ip})'

    def prepare(self):
        if hasattr(self, 'PATH_OVERRIDE'):
            request_path = self.PATH_OVERRIDE
        else:
            request_path = self.request.path
        request_counter = get_counter(
            name='request_call'
        )
        request_counter.labels(endpoint=request_path).inc()
        return super().prepare()

    def on_finish(self):
        if hasattr(self, 'PATH_OVERRIDE'):
            request_path = self.PATH_OVERRIDE
        else:
            request_path = self.request.path
        request_counter = get_counter(
            name='request_result'
        )
        request_counter.labels(
            endpoint=request_path,
            code=self._status_code
        ).inc()

    async def _execute(self, transforms, *args, **kwargs):
        if hasattr(self, 'PATH_OVERRIDE'):
            request_path = self.PATH_OVERRIDE
        else:
            request_path = self.request.path
        with get_summary('request_timing').labels(endpoint=request_path).time():
            await super()._execute(transforms, *args, **kwargs)

    def set_default_headers(self):
        super().set_default_headers()
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, api_key, Authorization')
        self.set_header('Access-Control-Allow-Methods',
                        ', '.join(self.SUPPORTED_METHODS))

    def options(self, *_, **__):
        """Options handler
        """
        self.set_status(204)
        self.finish()


class HomePageHandler(BaseHandler):
    """Home Page Handler
    """
    SUPPORTED_METHODS = ('GET',)

    def initialize(self, start_time: dt.datetime):
        """Initialization

        Args:
            start_time (dt.datetime): Program start time
        """
        # pylint: disable=attribute-defined-outside-init
        # This is the correct pattern for tornado
        self.__start_time = start_time

    async def get(self, *_, **__) -> None:
        """Handler body
        """
        self.write(
            f'Smartfin Data API v{version('smartfin_data_api')}'
            f' deployed at {self.__start_time.isoformat()}')
        self.set_status(HTTPStatus.OK)


class VersionHandler(BaseHandler):
    """Version Handler

    """
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    async def get(self, *_, **__) -> None:
        """Gets the version information for this app
        """
        self.write({
            'version': version('smartfin_data_api')
        })
        self.set_status(HTTPStatus.OK)


class ParticleEventHandler(BaseHandler):
    """Particle Event handler

    """
    SUPPORTED_METHODS = ('POST', 'OPTIONS')

    def initialize(self, pg_schema: PostgresSchema):
        """Initializes handler
        """
        self.__log = logging.getLogger('ParticleEventHandler')
        self.__schema = pg_schema

    async def post(self, *_, **__) -> None:
        """POST method handler
        """
        self.__log.debug('Header: %s', self.request.headers)

        body = json.loads(self.request.body)
        self.__log.debug('Body: %s', body)
        self.__schema.insert_record(
            published_at=dt.datetime.fromisoformat(body['published_at']),
            event=body['event'],
            data=body['data'],
            coreid=body['coreid'],
            fw_version=int(body['fw_version'])
        )

        self.set_status(HTTPStatus.OK)
