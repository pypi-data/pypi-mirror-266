class MockResponse:
    """ Mocked response from CPS """
    def __init__(self, value):
        self.json_value = value

    def json(self):
        return self.json_value


class Logger:
    """Mocked logger to easily find last log triggered from SDK server."""
    def __init__(self):
        self.last_error = []
        self.last_info = []

    def info(self, log: str):
        self.last_info.append(log)

    def error(self, log: str):
        self.last_error.append(log)
