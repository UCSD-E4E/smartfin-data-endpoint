'''Data API handlers
'''
import datetime as dt
from http import HTTPStatus
from importlib.metadata import version

from tornado.web import RequestHandler

from smartfin_data_api import __version__
from smartfin_data_api.metrics import get_counter, get_summary

# pylint: disable=abstract-method, arguments-differ, attribute-defined-outside-init
# This is typical behavior for tornado

class BaseHandler(RequestHandler):
    """Base Handler for E4ESF
    """

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
