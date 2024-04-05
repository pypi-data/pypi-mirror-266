class ApiException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NoAuthData(ApiException):
    pass


class RequestError(ApiException):
    pass
