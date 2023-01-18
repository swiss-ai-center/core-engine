class NotFoundException(Exception):
    """Exception raised when a resource is not found."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ConflictException(Exception):
    """Exception raised when a resource is in conflict with another resource."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UnreachableException(Exception):
    """Exception raised when a resource is unreachable."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
