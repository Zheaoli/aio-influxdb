import requests_mock
from influxdb.client import AioInfluxDBClient
import asyncio
import unittest
import warnings
from unittest import mock


class TestAioInfluxDBClient(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('error', FutureWarning)
        self.cli = AioInfluxDBClient('localhost', 8086, 'username', 'password')

    def test_write(self):
        async def testwrite():
            with mock.patch("aiohttp.client.ClientSession._request") as fake:
                await self.cli.write