#!/usr/bin/python
# coding=utf-8
'''
common utils;
'''

import uuid
import re
from lxml.html import fromstring
from weixin.utils.httpclient import HttpClient
from weixin.utils.decorator import cache_wrapper
from weixin.utils.weather import WEATHER_CLIENT as weather_client
from weixin.cache import session_cache, weather_cache, web_session_cache
from weixin.utils.tuling_client import TURING_CLIENT as tuling_client
from weixin.settings import LOGGER


class Session(object):

    def __init__(self, session_cache=web_session_cache):
        self.session_cache = session_cache

    def generate_token(self, uid, expire=3600 * 4):
        key = uuid.uuid4().hex
        self.session_cache.set(key, uid, expire)
        return key

    def get_uid(self, token):
        return self.session_cache.get(token)


USER_SESSION = Session()
WECHAT_USR_SESSION = Session(session_cache)


class IPData(object):

    def __init__(self):
        self.http_client = HttpClient()

    @cache_wrapper('location', 86400)
    def get_ip_location(self, ip):
        '''
        get the user city name accroding to its ip;
        query it from baidu.com
        '''
        return self._query_ip_from_ali(ip)

    @cache_wrapper('weather', 3600)
    def get_ip_weather(self, ip):
        res = weather_client.forecast_weather(ip)
        if res['errcode'] != 0:
            return ''
        resp_data = res['data']
        status = resp_data['status']
        weather_msg = ''
        if status.lower() == 'ok':
            weather_data = resp_data['daily_forecast'][0]
            day_wea = weather_data['cond_txt_d']
            night_wea = weather_data['cond_txt_n']
            if day_wea != night_wea:
                weather = day_wea + u'转' + night_wea
            else:
                weather = day_wea
            wind = weather_data['wind_dir'] + weather_data['wind_sc'] + u'级'
            weather_msg = u"{weather}\n{wind}\n气温{low}℃/{high}℃".format(
                weather=weather,
                wind=wind,
                low=weather_data['tmp_min'],
                high=weather_data['tmp_max']
            )
        else:
            LOGGER.info(resp_data)
        return weather_msg

    def _query_ip_from_ali(self, ip):
        url = 'http://ip.taobao.com/service/getIpInfo.php?ip={}'.format(ip)
        resp = self.http_client.get(url)
        if 'data' in resp:
            regin = resp['data'].get('region')
            city = resp['data'].get('city')
            if regin == city:
                return regin + u'市'
            return u'{}省{}市'.format(regin, city)
        return ''

    def _query_ip_from_baidu(self, ip):
        url = 'http://www.baidu.com/s?wd=%s'
        url = url % ip
        ip_xpath = '//div[@id="content_left"]//div[@class="c-border"]'\
            '//table/tr/td'
        content = self.http_client.get(url)
        dom = fromstring(content)
        ip_content = dom.xpath(ip_xpath)
        if ip_content:
            ip_content = ip_content[0]
            ip_content = ip_content.xpath("string()")
            ip_content = ip_content.strip()
            ip_content = ip_content.replace("\n", '')
            ip_content = ip_content.replace("\t", '')
            address = self._match_address(ip_content)
            # if address:
            #     weather_cache.cache_ip_location(ip, address)
        else:
            address = ''
        LOGGER.info("ip: %s, addr: %s", ip, address)
        return address

    def _match_address(self, ip_content):
        pattern = u'IP地址: [^\u4E00-\u9FA5]*(?P<address>[\u4E00-\u9FA5]+)[ ]?'
        pattern = re.compile(pattern)
        match = pattern.search(ip_content)
        address = ''
        if match:
            address = match.group("address")
        return address


def get_weather_by_ip(ip):
    # ip = '61.183.69.254'
    ip_instance = IPData()
    address = ip_instance.get_ip_location(ip)
    if not address:
        LOGGER.info("ip: %s, not found address: %s", ip, address)
        return ''
    weather_info = ip_instance.get_ip_weather(ip)
    # weather_info = get_weather_msg_hefeng(ip, address)
    # weather_info = get_weather_msg_turing(address)
    if isinstance(weather_info, unicode):
        weather_info = weather_info.encode("utf-8")
    if isinstance(address, unicode):
        address = address.encode("utf-8")
    return address + ' ' + weather_info


def get_weather_msg_turing(city):
    weather = weather_cache.get_city_weather(city)
    if weather:
        return weather
    if not isinstance(city, unicode):
        city = unicode(city, 'utf-8')
    query_msg = city + u"天气"
    result = tuling_client.query_text(query_msg)
    pattern = u",(?P<weather>[\u4e00-\u9fa5]+) "\
        u"(?P<wind>[\u4e00-\u9fa5]+(\\d+-\\d+[\u4e00-\u9fa5])?),"\
        u"[\u4e00-\u9fa5]+(?P<low_temp>\\d+)[\u4e00-\u9fa5][，,]"\
        u"[\u4e00-\u9fa5]+(?P<high_temp>\\d+)[\u4e00-\u9fa5]"
    p = re.compile(pattern)
    match = p.search(result)
    msg = ''
    if match:
        weather = match.group("weather")
        wind = match.group("wind")
        low_temp = match.group("low_temp")
        high_temp = match.group("high_temp")
        msg = u"{weather}\n{wind}\n气温{low}℃/{high}℃".format(
            weather=weather,
            wind=wind,
            low=low_temp,
            high=high_temp
        )
        weather_cache.cache_city_weather(city, msg)
    return msg


def unicode2utf(data):
    if isinstance(data, dict):
        return {
            unicode2utf(key): unicode2utf(value) for
            (key, value) in data.items()}
    if isinstance(data, list):
        return [unicode2utf(item) for item in data]
    if isinstance(data, unicode):
        return data.encode("utf-8")
    return data
