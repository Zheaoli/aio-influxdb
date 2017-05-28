import unittest
import warnings
import asyncio
from unittest import mock

from influxdb.client import AioInfluxDBClient


class TestAioInfluxDBClient(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('error', FutureWarning)
        self.cli = AioInfluxDBClient('localhost', 8086, 'username', 'password')

    def test_write(self):
        async def testwrite():
            await self.cli.write({"database": "mydb",
                                  "retentionPolicy": "mypolicy",
                                  "points": [{"measurement": "cpu_load_short",
                                              "tags": {"host": "server01",
                                                       "region": "us-west"},
                                              "time": "2009-11-10T23:00:00Z",
                                              "fields": {"value": 0.64}}]}
                                 )

        loop = asyncio.new_event_loop()
        loop.run_until_complete(testwrite())
