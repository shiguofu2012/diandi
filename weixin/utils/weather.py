# coding=utf-8

import time
import functools
import hashlib
from weixin.utils.httpclient import HttpClient
from weixin.settings import LOGGER as LOG, HE_UNAME, HE_KEY


def sign_wrapper(func):

    @functools.wraps(func)
    def wrapper(self, url, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']
        elif 'params' in kwargs:
            data = kwargs['params']
        else:
            data = {}
        data['username'] = self.user_name
        data['t'] = int(time.time())
        key_order = sorted(data)
        data_list = []
        for key in key_order:
            data_list.append(u"{}={}".format(key, data[key]))
        sign_str = u'&'.join(data_list) + self.api_key
        sign_str = sign_str.encode("utf-8")
        sign = hashlib.md5(sign_str).hexdigest()
        data['sign'] = sign
        if 'data' in kwargs:
            kwargs['data'] = data
        elif 'params' in kwargs:
            kwargs['params'] = data
        if not url.startswith(('http', 'https')):
            url = self.API_BASE + url
        return func(self, url, **kwargs)
    return wrapper


def convert_res(func):

    @functools.wraps(func)
    def wrapper(self, url, **kwargs):
        LOG.info(kwargs)
        res = func(self, url, **kwargs)
        if not res:
            return {'errcode': -1, 'errmsg': "no data return"}
        he_res = res['HeWeather6'][0]
        if he_res['status'] != 'ok':
            LOG.error("he weather return error: %s", he_res)
            return {"errcode": -1, 'errmsg': he_res['status']}
        return {'errcode': 0, 'data': he_res}
    return wrapper


class HeFengWeather(object):

    API_BASE = 'https://free-api.heweather.net/s6'

    def __init__(self, user_name, api_key):
        self.user_name = user_name
        self.api_key = api_key
        self.client = HttpClient()

    @sign_wrapper
    @convert_res
    def get(self, url, **kwargs):
        kwargs['verify'] = False
        return self.client.get(url, **kwargs)

    @sign_wrapper
    @convert_res
    def post(self, url, **kwargs):
        kwargs['verify'] = False
        return self.client.post(url, **kwargs)

    def forecast_weather(self, city):
        url_path = '/weather/forecast'
        data = {'location': city}
        return self.get(url_path, params=data)


WEATHER_CLIENT = HeFengWeather(HE_UNAME, HE_KEY)
