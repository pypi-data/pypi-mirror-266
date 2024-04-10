from __future__ import annotations

from http import HTTPStatus

from fiddler.schemas.response import ErrorData
from fiddler.utils.logger import get_logger
from fiddler.version import __version__

logger = get_logger(__name__)


class BaseError(Exception):
    message: str = 'Something went wrong'

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)

    def __str__(self) -> str:
        return str(self.message)

    @property
    def name(self) -> str:
        """Name of the error type."""
        return self.__class__.__name__


class IncompatibleClient(BaseError):
    """Python client version is incompatible with the given Fiddler Platform"""

    message = (
        'Python Client version ({client_version}) is not compatible with your '
        'Fiddler Platform version ({server_version}).'
        # @TODO - Add link to compatibility matrix doc
    )

    def __init__(self, server_version: str) -> None:
        self.message = self.message.format(
            client_version=__version__, server_version=server_version
        )

        super().__init__(self.message)


class AsyncJobFailed(BaseError):
    """Async job failed to execute successfully"""


class Unsupported(BaseError):
    """Encountered an unsupported operation"""

    message = 'This operation is not supported'


class HttpError(BaseError):
    """Base class for all HTTP errors"""


class ConnTimeout(HttpError):
    """Connection timeout error"""

    message = 'Request timed out while trying to reach endpoint'


class ConnError(HttpError):
    """Connection error"""

    message = 'Unable to reach the given endpoint'


class ApiError(HttpError):
    """HTTP error class"""

    code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    reason: str = 'ApiError'

    def __init__(self, error: ErrorData) -> None:
        self.code = error.code
        self.message = error.message
        self.errors = error.errors
        super().__init__(self.message)


class NotFound(ApiError):
    code: int = HTTPStatus.NOT_FOUND
    reason: str = 'NotFound'


class Conflict(ApiError):
    code: int = HTTPStatus.CONFLICT
    reason: str = 'Conflict'
