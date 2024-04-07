"""This is a sample python file for testing functions from the source code."""

from __future__ import annotations

import unittest

from project_async import Client


class ClientTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_hello(self):
        """
        This defines the expected usage, which can then be used in various test cases.
        Pytest will not execute this code directly, since the function does not contain the suffix "test"
        """
        client = await Client.with_session(username="foo", password="bar")
        await client.get_foo()
