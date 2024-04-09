import json
import traceback

from .base_api import Api

from .request import HttpApiRequest
from .response import Response
from .exceptions import BadRequest, MiddlewareShortCircuit

default_cors_headers = {
    "Access-Control-Allow-Headers": "Content-Type, X-Amz-Date, Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Max-Age": 600,
    "Content-Type": "application/json"
}


class HttpApi(Api):
    def __init__(self, name="SAM-API", cors_headers=None, cors_function=None):
        super().__init__(name="SAM-API", cors_headers=None, cors_function=None)

    def __call__(self, event, context, *args, **kwargs):
        try:
            request = self._process_middlewares(HttpApiRequest(event=event, app=self, debug=self.debug))
            self.log.debug(event)

            function = self._resources[request.route_key]
            response = function(request)

            base_headers = self.cors_headers.copy()

            if isinstance(response, Response):
                rslt = response.to_dict()
                rslt_headers = rslt.get('headers', {})
                base_headers.update(rslt_headers)
                rslt['headers'] = base_headers
                return rslt

            response_headers = response.get('headers', {})
            base_headers.update(response_headers)
            response['headers'] = base_headers
            return response

        except MiddlewareShortCircuit as e:
            return e.response

        except BadRequest as e:
            return {
                "isBase64Encoded": False,
                "statusCode": 400,
                "body": json.dumps({
                    "error": e.message
                })
            }
        except Exception as e:
            self.log.error(str(e))
            debug_error = traceback.format_exc()
            return {
                "isBase64Encoded": False,
                "statusCode": 500,
                "body": json.dumps({
                    "error": debug_error if self.debug else "Internal Server Error"
                })
            }
