class BadRequest(Exception):
    def __init__(self, message="Bad request format"):
        self.message = message
        super().__init__(self.message)

class MiddlewareShortCircuit(Exception):
    def __init__(self, response):
        self.response = response
        super().__init__('')