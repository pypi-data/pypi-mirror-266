"""Async Python client for SABnzbd."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import socket
from typing import TYPE_CHECKING, Self

from aiohttp import ClientError, ClientSession
from yarl import URL

from .exceptions import SabnzbdConnectionError, SabnzbdConnectionTimeoutError
from .models.queue import Queue, QueueOperationRequest, QueueRequest, QueueResponse
from .models.status import StatusResponse

if TYPE_CHECKING:
    from .const import QueueOperationCommand
    from .models.base import SabnzbdRequest

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True)
class Sabnzbd:
    """SABnzbd API client."""

    host: str
    port: int
    api_key: str
    path: str = "/api"
    session: ClientSession | None = None

    _close_session: bool = False

    def __post_init__(self) -> None:
        """Initialize the Tailwind object."""
        self._build_url = URL.build(
            scheme="http",
            host=self.host,
            port=self.port,
            path=self.path,
        )

    async def _request(self, request: SabnzbdRequest) -> str:
        """Execute a GET request against the API."""
        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        request_params = request.query_params
        _LOGGER.debug("Doing request: GET %s %s", self._build_url, request_params)

        params = {
            "output": "json",
            "apikey": self.api_key,
        }
        params.update(request_params)

        try:
            async with self.session.get(
                self._build_url,
                params=params,
            ) as response:
                response.raise_for_status()
                response_text = await response.text()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the SABnzbd API"
            raise SabnzbdConnectionTimeoutError(msg) from exception
        except (
            ClientError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating to the SABnzbd API"
            raise SabnzbdConnectionError(msg) from exception

        _LOGGER.debug(
            "Got response with status %s and body: %s",
            response.status,
            response_text,
        )

        return response_text

    async def queue(
        self,
    ) -> Queue:
        """Get carbon intensity."""
        result = await self._request(
            QueueRequest(),
        )

        return QueueResponse.from_json(result).queue

    async def operate_queue(self, *, command: QueueOperationCommand) -> StatusResponse:
        """Operate the queue."""
        result = await self._request(
            QueueOperationRequest(mode=command),
        )
        return StatusResponse.from_json(result)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter."""
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit."""
        await self.close()
