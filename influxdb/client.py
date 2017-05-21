# encoding: utf-8
"""
@version: ??
@author: lizheao
@contact: lizheao@wecash.net
@software: PyCharm
@file: client.py
@time: 下午5:07
"""
import json
from urllib.parse import urlparse

import aiohttp

from influxdb.httptool import ClientSession
from influxdb.resultset import ResultSet


class AioInfluxDBClient(object):
    def __init__(self,
                 host="localhost",
                 port=8086,
                 username="root",
                 password="root",
                 database=None,
                 retries=3,
                 ssl=False,
                 verify_ssl=False,
                 timeout=None):
        """
        
        :param host: 
        :param port: 
        :param username: 
        :param password: 
        :param database: 
        :param ssl: 
        :param verify_ssl: 
        :param timeout: 
        """
        # TODO :add proxy and UDP Support
        self.__host = host
        self.__port = int(port)
        self._username = username
        self._password = password
        self._database = database
        self._timeout = timeout

        self._verify_ssl = verify_ssl

        self._scheme = "http"

        if ssl is True:
            self._scheme = "https"

        self.__baseurl = "{0}://{1}:{2}".format(
            self._scheme,
            self._host,
            self._port)

        self._headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }
        self._session = ClientSession()
        self._retries = retries
        self._base_auth = aiohttp.BasicAuth(login=self._username, password=self._password, encoding="utf8")

    @property
    def _baseurl(self):
        return self._get_baseurl()

    def _get_baseurl(self):
        return self.__baseurl

    @property
    def _host(self):
        return self._get_host()

    def _get_host(self):
        return self.__host

    @property
    def _port(self):
        return self._get_port()

    def _get_port(self):
        return self.__port

    @property
    def session(self):
        return self._session

    @classmethod
    def from_DSN(cls, dsn, **kwargs):
        """
        Return an instance of :class:`~.InfluxDBClient` from the provided
        data source name. Supported schemes are "influxdb", "https+influxdb"
        and "udp+influxdb". Parameters for the :class:`~.InfluxDBClient`
        constructor may also be passed to this method.

        :param dsn: data source name
        :type dsn: string
        :param kwargs: additional parameters for `InfluxDBClient`
        :type kwargs: dict
        :raises ValueError: if the provided DSN has any unexpected values

        :Example:

        ::

            >> cli = InfluxDBClient.from_DSN('influxdb://username:password@\
            localhost:8086/databasename', timeout=5)
            >> type(cli)
            <class 'influxdb.client.InfluxDBClient'>
            >> cli = InfluxDBClient.from_DSN('udp+influxdb://username:pass@\
            localhost:8086/databasename', timeout=5, udp_port=159)
            >> print('{0._baseurl} - {0.use_udp} {0.udp_port}'.format(cli))
            http://localhost:8086 - True 159

        .. note:: parameters provided in `**kwargs` may override dsn parameters
        .. note:: when using "udp+influxdb" the specified port (if any) will
            be used for the TCP connection; specify the UDP port with the
            additional `udp_port` parameter (cf. examples).
        """

        init_args = parse_dsn(dsn)
        host, port = init_args.pop('hosts')[0]
        init_args['host'] = host
        init_args['port'] = port
        init_args.update(kwargs)

        return cls(**init_args)

    def switch_database(self, database):
        """
        Change the client's database.
        :param database: the name of the database to switch to
        :type database: str
        """
        self._database = database

    def switch_user(self, username, password):
        """
        Change the client's username.

        :param username: the username to switch to
        :type username: str
        :param password: the password for the username
        :type password: str
        """
        self._username = username
        self._password = password
        self._base_auth = aiohttp.BasicAuth(login=self._username, password=self._password, encoding="utf8")

    async def request(self, url, method="GET", params=None, data=None, expected_response_code=200, headers=None,
                      request_client=None):
        url = "{}/{}".format(self._baseurl, url)
        if request_client is None:
            request_client = self._session
        if headers is None:
            headers = self._headers
        if params is None:
            params = {}
        if isinstance(data, (dict, list)):
            data = json.dumps(data)
        retry = True
        _try = 0
        while retry:
            try:
                _response = request_client.request(method=method, url=url, params=params, data=data, headers=headers,
                                                   auth=self._base_auth)
                break
            except aiohttp.client_exceptions.ClientConnectionError as e:
                _try += 1
                if self._retries != 0:
                    retry = _try < self._retries
        else:
            raise aiohttp.client_exceptions.ClientConnectionError
        if 500 <= _response.status < 600:
            # TODO : InfluxDB Exception
            raise Exception()
        elif _response.status == expected_response_code:
            return _response
        else:
            raise Exception


def parse_dsn(dsn):
    conn_params = urlparse(dsn)
    init_args = {}
    scheme_info = conn_params.scheme.split('+')
    if len(scheme_info) == 1:
        scheme = scheme_info[0]
        modifier = None
    else:
        modifier, scheme = scheme_info

    if scheme != 'influxdb':
        raise ValueError('Unknown scheme "{0}".'.format(scheme))

    if modifier:
        if modifier == 'udp':
            init_args['use_udp'] = True
        elif modifier == 'https':
            init_args['ssl'] = True
        else:
            raise ValueError('Unknown modifier "{0}".'.format(modifier))

    netlocs = conn_params.netloc.split(',')

    init_args['hosts'] = []
    for netloc in netlocs:
        parsed = _parse_netloc(netloc)
        init_args['hosts'].append((parsed['host'], int(parsed['port'])))
        init_args['username'] = parsed['username']
        init_args['password'] = parsed['password']

    if conn_params.path and len(conn_params.path) > 1:
        init_args['database'] = conn_params.path[1:]

    return init_args


def _parse_netloc(netloc):
    info = urlparse("http://{0}".format(netloc))
    return {'username': info.username or None,
            'password': info.password or None,
            'host': info.hostname or 'localhost',
            'port': info.port or 8086}
