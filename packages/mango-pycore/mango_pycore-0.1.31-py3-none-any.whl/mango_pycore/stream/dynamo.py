import logging
import traceback

from ..tools.utils import from_dynamodb_to_json


class Stream:
    def __init__(self, pk_name, sk_name, name="Dynamo"):
        self._resources = {}
        self.pk_name = pk_name
        self.sk_name = sk_name
        self.name = name
        self._debug = False
        self.log = self._config_logging()

    def __call__(self, event, context, *args, **kwargs):
        self.rawEvent = event
        self.rawContext = context

        self.log.debug(event)
        try:
            assert 'Records' in event.keys(), "Key 'Records' is missing in stream"
            for record in event["Records"]:
                assert 'eventName' in record.keys(), "Key 'eventName' is missing in stream"
                action = record["eventName"]
                assert 'eventSourceARN' in record.keys(), "Key 'eventSourceARN' is missing in stream"
                arn = record['eventSourceARN']
                table_name = arn.split("/")[1]

                pk = ""
                db_data_old = None
                db_data_new = None
                if action == "INSERT":
                    self.action = "INSERT"
                    db_data_new = from_dynamodb_to_json(record["dynamodb"]["NewImage"])
                    db_data_old = None
                    assert self.pk_name in db_data_new.keys(), f"Key {self.pk_name} is missing in data stream"
                    pk = db_data_new[self.pk_name]
                if action == "MODIFY":
                    self.action = "MODIFY"
                    db_data_new = from_dynamodb_to_json(record["dynamodb"]["NewImage"])
                    db_data_old = from_dynamodb_to_json(record["dynamodb"]["OldImage"])
                    assert self.pk_name in db_data_new.keys(), f"Key {self.pk_name} is missing in data stream"
                    pk = db_data_new[self.pk_name]
                if action == "REMOVE":
                    self.action = "REMOVE"
                    db_data_new = None
                    db_data_old = from_dynamodb_to_json(record["dynamodb"]["OldImage"])
                    assert self.pk_name in db_data_old.keys(), f"Key {self.pk_name} is missing in data stream"
                    pk = db_data_old[self.pk_name]

                key = f"{action} {pk}"
                if key in self._resources.keys():
                    self._resources[key](db_data_old, db_data_new, table_name)
                else:
                    self.log.debug(f"No handler was found for key '{key}'")
            return True

        except AssertionError as e:
            self.log.debug(traceback.format_exc())
            self.log.critical(str(e))
            exit(0)
        except IndexError as e:
            self.log.debug(traceback.format_exc())
            self.log.critical(str(e))
            exit(0)

    def register(self, p_key, actions: list):
        def inner_register(function):
            for action in actions:
                self._register_actions(action, p_key, function)
        return inner_register

    def _register_actions(self, action, p_key, function):
        if action in ['INSERT', 'MODIFY', "REMOVE"]:
            key = f"{action} {p_key}"
            if key in self._resources.keys():
                self.log.error(f"Key '{key}' already registered and will be replaced by last function used")
            self._resources[key] = function

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
