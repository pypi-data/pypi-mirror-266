import logging

logger = logging.getLogger(__name__)


class ClientBaseException(Exception):
    pass


class ClientAlreadyExistsException(ClientBaseException):
    def __init__(self, client):
        super().__init__(f"Client {client} already exists")
        logger.error(f"Client {client} already exists")


class ClientDoesntExistException(ClientBaseException):
    def __init__(self, client):
        super().__init__(f"Client {client} doesn't exist")
        logger.error(f"Client {client} doesn't exist")


class BadResponseException(ClientBaseException):
    def __init__(self, code, message):
        super().__init__(f"Code: {code}, message: {message}")
        logger.warning(f"Code: {code}, message: {message}")


class InvalidLocationException(ClientBaseException):
    def __init__(self, location):
        super().__init__(f"Invalid location: {location}")
        logger.warning(f"Invalid location: {location}")


class AttributeValidationException(ClientBaseException):
    def __init__(self, message):
        super().__init__(message)
        logger.error(message)


class UnexpectedException(ClientBaseException):
    def __init__(self, message):
        super().__init__(f"Unexpected error! Error: {message}")
        logger.error(f"Unexpected error! Error: {message}")


class InvalidTimeException(ClientBaseException):
    def __init__(self, message):
        super().__init__(message)
        logger.warning(message)
