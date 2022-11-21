class NotFoundException(Exception):
    """Exception raised when a resource is not found."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BadRequestException(Exception):
    """Exception raised when a request is not valid."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InternalServerErrorException(Exception):
    """Exception raised when an internal error occurs."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
