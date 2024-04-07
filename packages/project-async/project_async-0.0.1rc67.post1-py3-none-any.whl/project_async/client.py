"""API Client code"""

from __future__ import annotations

import functools
from typing import Self

import aiohttp

from . import model

__all__ = [
    "Client",
]


class Client:
    """Async client for your API.

    TODO: describe what the client does.
    """

    def __init__(
        self, *, session: aiohttp.ClientSession, username: str, password: str
    ):
        self._session = session
        self._username = username
        self._password = password

    @classmethod
    async def with_session(cls, **kwargs) -> Self:
        session = aiohttp.ClientSession()
        return cls(session=session, **kwargs)

    async def maybe_login(self) -> None:
        """Logic to perform for login or authentication."""

    @staticmethod
    def authenticated(fn):

        @functools.wraps(fn)
        async def wrapper(self: "Client", *args, **kwargs):
            await self.maybe_login()
            return await fn(self, *args, **kwargs)

        return wrapper

    @authenticated
    async def get_foo(self, *args, **kwargs) -> model.Response:
        """Method to implement."""
        return model.Response.from_dict({"id": 1, "fooBar": "foobar"})
