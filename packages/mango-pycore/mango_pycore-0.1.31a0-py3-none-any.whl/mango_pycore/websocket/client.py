import json
import logging
from ctypes import Union
from json import JSONDecodeError

from websockets.sync.client import connect


class WebsocketClient:
    def __init__(self, server: str, log=logging):
        self._server = self._parse_server(server)
        self._log = log

    def send(self, channel: str, message, headers = None):
        connection = f"wss://{self._server}?channel={channel}"
        headers = headers if headers else {}
        with connect(connection, additional_headers=headers) as websocket:
            websocket.send(json.dumps(message, default=str))
            websocket.close()

    def wait_message(self, channel, timeout = 30, headers = None):
        connection = f"wss://{self._server}?channel={channel}"
        headers = headers if headers else {}
        with connect(connection, additional_headers=headers) as websocket:
            try:
                message = websocket.recv(timeout=timeout)
                try:
                    message = json.loads(message)
                except JSONDecodeError:
                    pass
            except TimeoutError:
                message = None
            except Exception as e:
                self._log.error(str(e))
                message = None
            return message

    def _parse_server(self, server):
        return server.split(":")[-1]
