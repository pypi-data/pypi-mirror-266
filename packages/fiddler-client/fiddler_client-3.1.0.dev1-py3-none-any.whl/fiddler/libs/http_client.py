from __future__ import annotations

from copy import deepcopy
from typing import Any
from urllib.parse import urljoin

import requests
import simplejson
from requests.adapters import HTTPAdapter

from fiddler.constants.common import JSON_CONTENT_TYPE
from fiddler.exceptions import (  # pylint: disable=redefined-builtin
    ConnError,
    ConnTimeout,
    HttpError,
)
from fiddler.libs.json_encoder import RequestClientJSONEncoder
from fiddler.utils.logger import get_logger

logger = get_logger(__name__)


class RequestClient:
    def __init__(
        self,
        base_url: str,
        headers: dict[str, str],
        verify: bool = True,
        proxies: dict | None = None,
    ) -> None:
        """Construct a request instance."""
        self.base_url = base_url
        self.proxies = proxies
        self.headers = headers
        self.headers.update({'Content-Type': JSON_CONTENT_TYPE})
        self.session = requests.Session()
        self.session.verify = verify
        adapter = HTTPAdapter(
            pool_connections=25,
            pool_maxsize=25,
        )
        self.session.mount(self.base_url, adapter)

    def call(
        self,
        *,
        method: str,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        data: dict | bytes | None = None,
        timeout: int | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Make request to server

        :param method: HTTP method like
        :param url: API endpoint
        :param params: Query parameters
        :param headers: Request headers
        :param data: Dict/binary data
        :param timeout: Request timeout in seconds
        """
        logger.debug('Making %s call to %s', method, url)

        full_url = urljoin(self.base_url, url)

        request_headers = self.headers
        # override/update headers coming from the calling method
        if headers:
            request_headers = deepcopy(self.headers)
            request_headers.update(headers)

        content_type = request_headers.get('Content-Type')
        if data is not None and content_type == JSON_CONTENT_TYPE:
            data = simplejson.dumps(data, ignore_nan=True, cls=RequestClientJSONEncoder)  # type: ignore

        kwargs.setdefault('allow_redirects', True)
        # requests is not able to pass the value of self.session.verify to the
        # verify param in kwargs when REQUESTS_CA_BUNDLE is set.
        # So setting that as default here
        kwargs.setdefault('verify', self.session.verify)
        try:
            response = self.session.request(
                method,
                full_url,
                params=params,
                data=data,
                headers=request_headers,
                timeout=timeout,
                proxies=self.proxies,
                **kwargs,
            )

        except requests.Timeout as exc:
            logger.error('%s call failed with Timeout error for URL %s', method, url)
            raise ConnTimeout() from exc
        except requests.ConnectionError as exc:
            logger.error('%s call failed with ConnectionError for URL %s', method, url)
            raise ConnError() from exc
        except requests.RequestException as exc:
            # catastrophic error.
            logger.error('%s call failed with RequestException for %s', method, url)
            raise HttpError() from exc

        response.raise_for_status()
        return response

    def get(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int | None = None,
        **kwargs: dict[str, Any],
    ) -> requests.Response:
        """Construct a get request instance."""
        return self.call(
            method='GET',
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def delete(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int | None = None,
        **kwargs: dict[str, Any],
    ) -> requests.Response:
        """Construct a delete request instance."""
        return self.call(
            method='DELETE',
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def post(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int | None = None,
        data: dict | bytes | None = None,
        **kwargs: dict[str, Any],
    ) -> requests.Response:
        """Construct a post request instance."""
        return self.call(
            method='POST',
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            data=data,
            **kwargs,
        )

    def put(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int | None = None,
        data: dict | None = None,
        **kwargs: dict[str, Any],
    ) -> requests.Response:
        """Construct a put request instance."""
        return self.call(
            method='PUT',
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            data=data,
            **kwargs,
        )

    def patch(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int | None = None,
        data: dict | None = None,
        **kwargs: dict[str, Any],
    ) -> requests.Response:
        """Construct a potch request instance."""
        return self.call(
            method='PATCH',
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            data=data,
            **kwargs,
        )
