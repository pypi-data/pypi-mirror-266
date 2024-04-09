import decimal
import json


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if float(o) == int(o):
                return int(o)
            else:
                return float(0)
        return super().default(o)


class Response:
    def __init__(self, code=200, encoded=False, body=None, headers={}):
        self.headers = {
            "Content-Type": "application/json",
        }
        self.headers.update(headers)
        self.code = code
        self.encoded = encoded
        self.body = body

    def to_dict(self):
        response = {
            "isBase64Encoded": self.encoded,
            "statusCode": self.code,
            "headers": self.headers,
        }
        if self.body is not None:
            response.update({
                "body": json.dumps(self.body, cls=CustomEncoder)
            })

        return response
