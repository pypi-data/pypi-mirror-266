"""Local exceptions used by library."""


class ConnectionFailedError(Exception):
    """Thrown when connecting to a processor fails immediately due to an error."""

    def __init__(self, exception):
        message = f"Connection failed: {exception}"
        super().__init__(message)


class ConnectionTimeoutError(Exception):
    """Thrown when connecting to a processor times out."""


class NotConnectedError(Exception):
    """Raised when an operation is performed that requires a connect and none is present."""

    def __init__(
        self, message="Not connected to Trinnov Altitude. Did you call `connect()`?"
    ):
        self.message = message
        super().__init__(self.message)
