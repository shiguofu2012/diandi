# coding=utf-8
'''http request client'''

import json
import requests
from weixin.settings import LOGGER, DEFAULT_HEADER


class HttpClient(object):

    _http = requests.Session()

    def __init__(self):
        self.timeout = 10

    def _request(self, method, url, **kwargs):
        data_format = kwargs.pop("data_fromat", "")
        if not data_format:
            data_format = 'json'
        data = kwargs.get("data", {})
        if data and data_format == 'json' and isinstance(data, dict):
            kwargs['data'] = json.dumps(data)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        if 'headers' not in kwargs:
            kwargs['headers'] = DEFAULT_HEADER
        res = self._http.request(method=method, url=url, **kwargs)
        try:
            res.raise_for_status()
        except requests.RequestException as reqex:
            LOGGER.error("request exception: %s", reqex)
        return self._handle_result(res)

    def _handle_result(self, resp):
        """handle http response content"""
        result = None
        try:
            result = resp.json()
        except (TypeError, ValueError):
            # LOGGER.error("res content: %s", resp.content)
            result = resp.content
        return result

    def get(self, url, **kwargs):
        """http request get client"""
        return self._request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        """http request post client"""
        return self._request("POST", url, **kwargs)
