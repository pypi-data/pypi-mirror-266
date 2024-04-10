from __future__ import annotations

from functools import cached_property
from uuid import UUID

from fiddler.configs import DEFAULT_CONNECTION_TIMEOUT, MIN_SERVER_VERSION
from fiddler.constants.common import CLIENT_NAME, FIDDLER_CLIENT_VERSION_HEADER
from fiddler.decorators import handle_api_error
from fiddler.exceptions import IncompatibleClient
from fiddler.libs.http_client import RequestClient
from fiddler.schemas.server_info import ServerInfo, Version
from fiddler.utils.logger import get_logger
from fiddler.utils.version import match_semver
from fiddler.version import __version__

logger = get_logger(__name__)


class Connection:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        url: str,
        token: str,
        proxies: dict | None = None,
        timeout: int = DEFAULT_CONNECTION_TIMEOUT,
        verify: bool = True,
        validate: bool = True,
    ) -> None:
        """
        Initiate connection to Fiddler Platform

        :param url: URL of Fiddler Platform
        :param token: Authorization token
        :param proxies: Dictionary mapping protocol to the URL of the proxy
        :param timeout: Seconds to wait for the server to send data before giving up
        :param verify: Controls whether we verify the server’s TLS certificate
        :param validate: Whether to validate the server/client version compatibility.
            Some functionalities might not work if this is turned off.
        """

        self.url = url
        self.token = token
        self.proxies = proxies
        self.timeout = timeout
        self.verify = verify

        if not url:
            raise ValueError('Please pass a valid url')

        if not token:
            raise ValueError('Please pass a valid token')

        self.request_headers = {
            'Authorization': f'Bearer {token}',
            FIDDLER_CLIENT_VERSION_HEADER: __version__,
        }

        if validate:
            self._check_server_version()
            self._check_version_compatibility()

    @cached_property
    def client(self) -> RequestClient:
        """Request client instance"""
        return RequestClient(
            base_url=self.url,
            headers=self.request_headers,
            proxies=self.proxies,
            verify=self.verify,
        )

    @cached_property
    def server_info(self) -> ServerInfo:
        """Server info instance"""
        return self._get_server_info()

    @cached_property
    def server_version(self) -> Version:
        """Server semver version"""
        return self.server_info.server_version

    @cached_property
    def organization_name(self) -> str:
        """Organization name"""
        return self.server_info.organization.name

    @cached_property
    def organization_id(self) -> UUID:
        """Organization id"""
        return self.server_info.organization.id

    @handle_api_error
    def _get_server_info(self) -> ServerInfo:
        """Get server info"""
        response = self.client.get(
            url='/v3/server-info',
        )

        return ServerInfo(**response.json().get('data'))

    @handle_api_error
    def _check_version_compatibility(self) -> None:
        """Check whether Client version is compatible with Fiddler Platform version"""

        self.client.get(
            url='/v3/version-compatibility',
            params={
                'client_version': __version__,
                'client_name': CLIENT_NAME,
            },
        )

    def _check_server_version(self) -> None:
        """Check whether Fiddler Platform version is compatible with Client version"""
        if match_semver(self.server_version, f'>={MIN_SERVER_VERSION}'):
            return

        raise IncompatibleClient(server_version=str(self.server_version))


class ConnectionMixin:
    @classmethod
    def _conn(cls) -> Connection:
        """Fiddler connection instance"""
        from fiddler import conn

        assert conn is not None
        return conn

    @classmethod
    def _client(cls) -> RequestClient:
        """Request client instance"""
        return cls._conn().client

    @property
    def organization_name(self) -> str:
        """Organization name property"""
        return self._conn().server_info.organization.name

    @property
    def organization_id(self) -> UUID:
        """Organization id property"""
        return self._conn().server_info.organization.id

    @classmethod
    def get_organization_name(cls) -> str:
        """Organization name"""
        return cls._conn().server_info.organization.name

    @classmethod
    def get_organization_id(cls) -> UUID:
        """Organization id"""
        return cls._conn().server_info.organization.id


def init(  # pylint: disable=too-many-arguments
    url: str,
    token: str,
    proxies: dict | None = None,
    timeout: int = DEFAULT_CONNECTION_TIMEOUT,
    verify: bool = True,
    validate: bool = True,
) -> None:
    """
    Initiate Python Client Connection

    :param url: URL of Fiddler Platform
    :param token: Authorization token
    :param proxies: Dictionary mapping protocol to the URL of the proxy
    :param timeout: Seconds to wait for the server to send data before giving up
    :param verify: Controls whether we verify the server’s TLS certificate
    :param validate: Whether to validate the server/client version compatibility.
         Some functionalities might not work if this is turned off.
    """
    from fiddler import set_conn

    conn = Connection(
        url=url,
        token=token,
        proxies=proxies,
        timeout=timeout,
        verify=verify,
        validate=validate,
    )

    set_conn(conn_=conn)
