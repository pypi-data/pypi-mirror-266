class TiqsException(Exception):
    def __init__(self, message: str, code: int = 500):
        """Initialize the exception."""
        super(TiqsException, self).__init__(message)
        self.code = code


class GeneralException(TiqsException):
    def __init__(self, message: str, code: int = 500):
        super(GeneralException, self).__init__(message, code)


class DataException(TiqsException):
    def __init__(self, message: str, code: int = 502):
        """Initialize the exception."""
        super(DataException, self).__init__(message, code)
