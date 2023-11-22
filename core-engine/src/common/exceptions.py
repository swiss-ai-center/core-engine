class NotFoundException(Exception):
    """Exception raised when a resource is not found."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UnprocessableEntityException(Exception):
    """Exception raised when a resource is unprocessable."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InternalServerErrorException(Exception):
    """Exception raised when an internal server error occurs."""

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


class InconsistentPipelineException(Exception):
    """Exception raised when a pipeline has an inconsistent definition."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class CouldNotSendJsonException(Exception):
    """Exception raised when a message could not be sent to the client."""

    def __init__(self, message, message_to_send, linked_id):
        self.message = message
        self.message_to_send = message_to_send
        self.linked_id = linked_id
        super().__init__(self.message)


class ConstraintException(Exception):
    """Exception raised when a constraint is not respected."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
