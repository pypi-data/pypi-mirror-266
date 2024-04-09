import logging
import traceback
from copy import copy

from .request import WebsocketApiRequest
from .response import Response

from .exceptions import MiddlewareShortCircuit


class WebsocketApi:
    def __init__(self, name="SAM-API-WEBSOCK"):
        self.name = name
        self._resources = {}
        self._middlewares = []
        self._debug = False
        self.log = self._config_logging()

    def __call__(self, event, context, *args, **kwargs):
        self.log.debug(event)
        try:
            request = self._process_middlewares(WebsocketApiRequest(event, self.debug))
            function = self._resources[request.route_key]
            response = function(request)

            if isinstance(response, Response):
                rslt = response.to_dict()
                return rslt

            return response

        except Exception as e:
            self.log.error(str(e))
            debug_error = traceback.format_exc()
            self.log.error(debug_error)
            raise Exception("Internal Server Error")

    def route(self, route_key: str):

        def inner_register(function):
            # Default route
            self._register_route(route_key=route_key, func=function)
        return inner_register

    def middleware(self):
        def inner_register(function):
            self._register_middleware(function)
        return inner_register

    def _register_route(self, route_key, func):
        if route_key in self._resources.keys():
            self.log.warning(f"Route Key '{route_key}'  already registered and will be replaced by last function")
        self._resources[route_key] = func

    def _register_middleware(self, func):
        self._middlewares.append(func)

    def _process_middlewares(self, request: WebsocketApiRequest):
        req = copy(request)
        for midd in self._middlewares:
            rslt = midd(req)
            if isinstance(rslt, WebsocketApiRequest):
                req = copy(rslt)
            if isinstance(rslt, Response):
                raise MiddlewareShortCircuit(response=rslt.to_dict())
        return req

    def _config_logging(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG if self._debug else logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s::[%(levelname)s]: %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = 0
        return logger

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value: bool):
        self._debug = value
        self.log.setLevel(logging.DEBUG if self._debug else logging.INFO)
