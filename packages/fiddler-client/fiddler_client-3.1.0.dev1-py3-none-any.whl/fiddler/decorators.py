from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, TypeVar, cast

import requests

from fiddler.exceptions import ApiError, Conflict, HttpError, NotFound, Unsupported
from fiddler.schemas.response import ErrorResponse
from fiddler.utils.logger import get_logger

logger = get_logger(__name__)

_WrappedFuncType = TypeVar(  # pylint: disable=invalid-name
    '_WrappedFuncType', bound=Callable[..., Any]
)


def handle_api_error(func: _WrappedFuncType) -> _WrappedFuncType:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except requests.JSONDecodeError as e:
            raise HttpError(message=f'Invalid JSON response - {e.doc}')  # type: ignore
        except requests.HTTPError as e:
            logger.error(
                'HTTP request to %s failed with %s - %s',
                getattr(e.request, 'url', 'unknown'),
                getattr(e.response, 'status_code', 'unknown'),
                getattr(e.response, 'content', 'missing'),
            )

            status_code = e.response.status_code or HTTPStatus.INTERNAL_SERVER_ERROR

            if status_code == HTTPStatus.METHOD_NOT_ALLOWED:
                raise Unsupported()

            try:
                error_resp = ErrorResponse(**e.response.json())
            except requests.JSONDecodeError:
                raise HttpError(
                    message=f'Invalid response content-type - {e.response.content}'
                )

            if status_code == HTTPStatus.CONFLICT:
                raise Conflict(error_resp.error)
            if status_code == HTTPStatus.NOT_FOUND:
                raise NotFound(error_resp.error)

            raise ApiError(error_resp.error)

    return cast(_WrappedFuncType, wrapper)
