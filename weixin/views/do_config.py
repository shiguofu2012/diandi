#!/usr/bin/python
# coding=utf-8

from datetime import datetime
from weixin.utils.utils import get_weather_by_ip
from weixin.utils.lunar_date import OPEN_API_CLIENT as open_api_client
from weixin.utils.image_utility import upload_image_qiniu
from weixin.models.banner import Banner, Tab
from weixin.settings import LOGGER

WEEK_MAP = {
        0: u'一',
        1: u'二',
        2: u'三',
        3: u'四',
        4: u'五',
        5: u'六',
        6: u'日'
        }


def get_ip_info(ip):
    weather = '----\n----\n气温--℃/--℃'
    lunar_date = ''
    today = datetime.now()
    try:
        weather = get_ip_weather(ip)
        lunar_date = get_lunar_date()
    except Exception as ex:
        LOGGER.error("get ip info ex: %s", ex, exc_info=True)
        today = datetime.now()
        lunar_date = u'----\n----\n星期{}'.format(WEEK_MAP[today.weekday()])
    return {'weather': weather, 'lunar_date': lunar_date}


def get_ip_weather(ip):
    weather = get_weather_by_ip(ip)
    weather_info = weather.split()
    if len(weather_info) == 1:
        weather = '----\n----\n气温--℃/--℃'
    return weather


def get_lunar_date():
    today = datetime.now()
    date_str = '{0}-{1}-{2}'.format(today.year, today.month, today.day)
    lunar_date_str = open_api_client.get_lunar(date_str)
    if not lunar_date_str:
        lunar_date_str = '----\n----\n星期{}'.format(WEEK_MAP[today.weekday()])
    return lunar_date_str


def do_get_banner():
    banner_obj = Banner()
    banners = banner_obj.get_banner()
    result = []
    for banner in banners:
        img_url = banner.get("banner_url")
        if not img_url:
            continue
        page_path = banner.get("page_path")
        appid = banner.get("appid", '')
        result.append({
            'pic_url': img_url, 'page_path': page_path, 'appid': appid})
    return result


def do_get_tab():
    tab_obj = Tab()
    tabs = tab_obj.get_tab()
    tab_list = []
    for tab in tabs:
        name = tab['name']
        tab_id = tab['tab_id']
        tab_list.append({'name': name, 'id': tab_id})
    return tab_list


def upload_image(user, files):
    result_dict = {}
    for filename, file_storage in files.items():
        url = upload_image_qiniu(file_storage.read())
        LOGGER.info(
                "filename: %s, url: %s, type: %s",
                filename, url, file_storage.mimetype)
        result_dict[file_storage.filename] = url
    return result_dict
