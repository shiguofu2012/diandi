#!/usr/bin/python
# coding=utf-8
import os
import re
from enum import Enum

TBK_TOKEN = '70000100837678567df8e4b765bbffa77b33ea4df074889271cb92ff'\
        '7b325bd2aa20708675448601'
STATIC_PATH = '/opt/front/shiguofu.cn/static'
TBK_PATH = os.path.join(STATIC_PATH, 'tbk')
QRCODE_PATH = os.path.join(STATIC_PATH, 'qrcode')
SHARE_PATH = os.path.join(STATIC_PATH, 'share')
UPLOAD_PATH = os.path.join(STATIC_PATH, 'upload')
BANNER_SAMP = os.path.join(STATIC_PATH, 'images/banners')
MORNING_SAMP = os.path.join(STATIC_PATH, 'images/banners')
TMP_PATH = os.path.join(STATIC_PATH, 'login')
STATIC_URI = 'https://shiguofu.cn/static'
HEADIMG_TMP = '/tmp/diandi/headimg'
BANNER_TMP = '/tmp/diandi/banner'
FONT_DIR = '/var/app/weixin/data/fonts'
PIC_DIR = '/var/app/weixin/data/pics'
DIANDI_QR = 'http://image.shiguofu.cn/file/2019/03/'\
        '69e833339bcc465897941d6637b57931_gh_3c6680f4008a_2581.jpg'
DETAIL_PAGE = "/pages/detail/detail?id={}"
HANZI_PATTERN = re.compile(ur"[\u4E00-\u9FA5]+")


WEEKDAY_MAP = {
        0: u'一',
        1: u'二',
        2: u'三',
        3: u'四',
        4: u'五',
        5: u'六',
        6: u'天'
        }


class PoetryOp(Enum):
    LIKE = 1
    BROWSE = 0
    DISLIKE = -1


class PayType(Enum):
    miniapp = 'JSAPI'
    wx_qrcode = 'NATIVE'


class SearchCat(Enum):
    author = 1


class HustKeMsg:
    SUBSCRIBE_MSG = '【感谢关注】国学研究系重要集中研究中华文化，'\
            '立志成为中华文化的传承者，希望中华文化融入在你我的生活中！\n回复任意内容开始国学文化之旅！'


class TemplateId(Enum):
    invited = 'pEDzLDAbUluZq9JDuT_if3QQXSgDgloWiiLL_1-YMK0'
    helper = 'PD9Y7GsiXU9EsKgcG5Rspj41UYJf2Z7XvySYp9oZlX8'
    task_ok = 'L_QmGwEPI6x-jPsPecfhxX4ClSSinX6zi8NB5Ddmq-w'


class OrderStatus(Enum):
    WXERROR = -1
    SIGNERROR = -2
    ORDERERROR = -3
    INIT = 0
    OK = 8

class LunarConfig:
    YEAR_START = 1901
    YEAR_STAR_TERM = 1900
    '''
    阴历年份记录表，每个元素存储格式：
    bit 16 ~ 13    12   11 ～ 0
         闰几月    闰月天数 当年每月天数
    如： 2020年 0x08a9e = 0b100 0 101010011110
     0b100 = 4 => 2020年闰四月
     0     => 闰四月为29天
     0b101010011110 => 12bit,每一位表示是29/30天 从低位表示正月
    '''
    LUNAR_CONSTANTS = [
        0x00752, 0x00ea5, 0x0ab2a, 0x0064b, 0x00a9b, 0x09aa6, 0x0056a, 0x00b59, 0x04baa, 0x00752, # 1901 ~ 1910
        0x0cda5, 0x00b25, 0x00a4b, 0x0ba4b, 0x002ad, 0x0056b, 0x045b5, 0x00da9, 0x0fe92, 0x00e92, # 1911 ~ 1920
        0x00d25, 0x0ad2d, 0x00a56, 0x002b6, 0x09ad5, 0x006d4, 0x00ea9, 0x04f4a, 0x00e92, 0x0c6a6, # 1921 ~ 1930
        0x0052b, 0x00a57, 0x0b956, 0x00b5a, 0x006d4, 0x07761, 0x00749, 0x0fb13, 0x00a93, 0x0052b, # 1931 ~ 1940
        0x0d51b, 0x00aad, 0x0056a, 0x09da5, 0x00ba4, 0x00b49, 0x04d4b, 0x00a95, 0x0eaad, 0x00536, # 1941 ~ 1950
        0x00aad, 0x0baca, 0x005b2, 0x00da5, 0x07ea2, 0x00d4a, 0x10595, 0x00a97, 0x00556, 0x0c575, # 1951 ~ 1960
        0x00ad5, 0x006d2, 0x08755, 0x00ea5, 0x0064a, 0x0664f, 0x00a9b, 0x0eada, 0x0056a, 0x00b69, # 1961 ~ 1970
        0x0abb2, 0x00b52, 0x00b25, 0x08b2b, 0x00a4b, 0x10aab, 0x002ad, 0x0056d, 0x0d5a9, 0x00da9, # 1971 ~ 1980
        0x00d92, 0x08e95, 0x00d25, 0x14e4d, 0x00a56, 0x002b6, 0x0c2f5, 0x006d5, 0x00ea9, 0x0af52, # 1981 ~ 1990
        0x00e92, 0x00d26, 0x0652e, 0x00a57, 0x10ad6, 0x0035a, 0x006d5, 0x0ab69, 0x00749, 0x00693, # 1991 ~ 2000
        0x08a9b, 0x0052b, 0x00a5b, 0x04aae, 0x0056a, 0x0edd5, 0x00ba4, 0x00b49, 0x0ad53, 0x00a95, # 2001 ~ 2010
        0x0052d, 0x0855d, 0x00ab5, 0x12baa, 0x005d2, 0x00da5, 0x0de8a, 0x00d4a, 0x00c95, 0x08a9e, # 2011 ~ 2020
        0x00556, 0x00ab5, 0x04ada, 0x006d2, 0x0c765, 0x00725, 0x0064b, 0x0a657, 0x00cab, 0x0055a, # 2021 ~ 2030
        0x0656e, 0x00b69, 0x16f52, 0x00b52, 0x00b25, 0x0dd0b, 0x00a4b, 0x004ab, 0x0a2bb, 0x005ad, # 2031 ~ 2040
        0x00b6a, 0x04daa, 0x00d92, 0x0eea5, 0x00d25, 0x00a55, 0x0ba4d, 0x004b6, 0x005b5, 0x076d2, # 2041 ~ 2050
        0x00ec9, 0x10f92, 0x00e92, 0x00d26, 0x0d516, 0x00a57, 0x00556, 0x09365, 0x00755, 0x00749, # 2051 ~ 2060
        0x0674b, 0x00693, 0x0eaab, 0x0052b, 0x00a5b, 0x0aaba, 0x0056a, 0x00b65, 0x08baa, 0x00b4a, # 2061 ~ 2070
        0x10d95, 0x00a95, 0x0052d, 0x0c56d, 0x00ab5, 0x005aa, 0x085d5, 0x00da5, 0x00d4a, 0x06e4d, # 2071 ~ 2080
        0x00c96, 0x0ecce, 0x00556, 0x00ab5, 0x0bad2, 0x006d2, 0x00ea5, 0x0872a, 0x0068b, 0x10697, # 2081 ~ 2090
        0x004ab, 0x0055b, 0x0d556, 0x00b6a, 0x00752, 0x08b95, 0x00b45, 0x00a8b, 0x04a4f           # 2091 ~ 2099
    ]
    '''
    阴历春节对应阳历日期，及对应离元旦天数
    12~7         6~5    4~0
    离元旦多少天  春节月  春节日
    如：2019年 0x11c5 = 0b100011 10 00101
    2019年正月初一对应阳历 => 2月5号
    元旦距离春节有 35天
    '''
    LUNAR_SOLAR_MAP = [
            0x18d3, 0x1348, 0x0e3d, 0x1750, 0x1144, 0x0c39, 0x15cd, 0x1042, 0x0ab6, 0x144a, # 1901 ~ 1910
            0x0ebe, 0x1852, 0x1246, 0x0cba, 0x164e, 0x10c3, 0x0b37, 0x14cb, 0x0fc1, 0x1954, # 1911 ~ 1920
            0x1348, 0x0dbc, 0x1750, 0x11c5, 0x0bb8, 0x15cd, 0x1042, 0x0b37, 0x144a, 0x0ebe, # 1921 ~ 1930
            0x17d1, 0x1246, 0x0cba, 0x164e, 0x1144, 0x0bb8, 0x14cb, 0x0f3f, 0x18d3, 0x1348, # 1931 ~ 1940
            0x0d3b, 0x16cf, 0x11c5, 0x0c39, 0x15cd, 0x1042, 0x0ab6, 0x144a, 0x0e3d, 0x17d1, # 1941 ~ 1950
            0x1246, 0x0d3b, 0x164e, 0x10c3, 0x0bb8, 0x154c, 0x0f3f, 0x1852, 0x1348, 0x0dbc, # 1951 ~ 1960
            0x16cf, 0x11c5, 0x0c39, 0x15cd, 0x1042, 0x0a35, 0x13c9, 0x0ebe, 0x17d1, 0x1246, # 1961 ~ 1970
            0x0d3b, 0x16cf, 0x10c3, 0x0b37, 0x14cb, 0x0f3f, 0x1852, 0x12c7, 0x0dbc, 0x1750, # 1971 ~ 1980
            0x11c5, 0x0c39, 0x15cd, 0x1042, 0x1954, 0x13c9, 0x0e3d, 0x17d1, 0x1246, 0x0d3b, # 1981 ~ 1990
            0x16cf, 0x1144, 0x0b37, 0x144a, 0x0f3f, 0x18d3, 0x12c7, 0x0dbc, 0x1750, 0x11c5, # 1991 ~ 2000
            0x0bb8, 0x154c, 0x0fc1, 0x0ab6, 0x13c9, 0x0e3d, 0x1852, 0x12c7, 0x0cba, 0x164e, # 2001 ~ 2010
            0x10c3, 0x0b37, 0x144a, 0x0f3f, 0x18d3, 0x1348, 0x0dbc, 0x1750, 0x11c5, 0x0c39, # 2011 ~ 2020
            0x154c, 0x0fc1, 0x0ab6, 0x144a, 0x0e3d, 0x17d1, 0x1246, 0x0cba, 0x15cd, 0x10c3, # 2021 ~ 2030
            0x0b37, 0x14cb, 0x0f3f, 0x18d3, 0x1348, 0x0dbc, 0x16cf, 0x1144, 0x0bb8, 0x154c, # 2031 ~ 2040
            0x0fc1, 0x0ab6, 0x144a, 0x0ebe, 0x17d1, 0x1246, 0x0cba, 0x164e, 0x1042, 0x0b37, # 2041 ~ 2050
            0x14cb, 0x0fc1, 0x18d3, 0x1348, 0x0dbc, 0x16cf, 0x1144, 0x0a38, 0x154c, 0x1042, # 2051 ~ 2060
            0x0a35, 0x13c9, 0x0e3d, 0x17d1, 0x11c5, 0x0cba, 0x164e, 0x10c3, 0x0b37, 0x14cb, # 2061 ~ 2070
            0x0f3f, 0x18d3, 0x12c7, 0x0d3b, 0x16cf, 0x11c5, 0x0bb8, 0x154c, 0x1042, 0x0ab6, # 2071 ~ 2080
            0x13c9, 0x0e3d, 0x17d1, 0x1246, 0x0cba, 0x164e, 0x10c3, 0x0bb8, 0x144a, 0x0ebe, # 2081 ~ 2090
            0x1852, 0x12c7, 0x0d3b, 0x16cf, 0x11c5, 0x0c39, 0x154c, 0x0fc1, 0x0a35, 0x13c9, # 2091 ~ 2100
    ]
    '''
    节气速查表16进制压缩
    '''
    TERMS_YEAR = [
        '9778397bd097c36b0b6fc9274c91aa','97b6b97bd19801ec9210c965cc920e','97bcf97c3598082c95f8c965cc920f',  # 1900 ～ 1903
        '97bd0b06bdb0722c965ce1cfcc920f','b027097bd097c36b0b6fc9274c91aa','97b6b97bd19801ec9210c965cc920e',
        '97bcf97c359801ec95f8c965cc920f','97bd0b06bdb0722c965ce1cfcc920f','b027097bd097c36b0b6fc9274c91aa',
        '97b6b97bd19801ec9210c965cc920e','97bcf97c359801ec95f8c965cc920f','97bd0b06bdb0722c965ce1cfcc920f',
        'b027097bd097c36b0b6fc9274c91aa','9778397bd19801ec9210c965cc920e','97b6b97bd19801ec95f8c965cc920f',
        '97bd09801d98082c95f8e1cfcc920f','97bd097bd097c36b0b6fc9210c8dc2','9778397bd197c36c9210c9274c91aa',
        '97b6b97bd19801ec95f8c965cc920e','97bd09801d98082c95f8e1cfcc920f','97bd097bd097c36b0b6fc9210c8dc2',
        '9778397bd097c36c9210c9274c91aa','97b6b97bd19801ec95f8c965cc920e','97bcf97c3598082c95f8e1cfcc920f',
        '97bd097bd097c36b0b6fc9210c8dc2','9778397bd097c36c9210c9274c91aa','97b6b97bd19801ec9210c965cc920e',
        '97bcf97c3598082c95f8c965cc920f','97bd097bd097c35b0b6fc920fb0722','9778397bd097c36b0b6fc9274c91aa',
        '97b6b97bd19801ec9210c965cc920e','97bcf97c3598082c95f8c965cc920f','97bd097bd097c35b0b6fc920fb0722',
        '9778397bd097c36b0b6fc9274c91aa','97b6b97bd19801ec9210c965cc920e','97bcf97c359801ec95f8c965cc920f',
        '97bd097bd097c35b0b6fc920fb0722','9778397bd097c36b0b6fc9274c91aa','97b6b97bd19801ec9210c965cc920e',
        '97bcf97c359801ec95f8c965cc920f','97bd097bd097c35b0b6fc920fb0722','9778397bd097c36b0b6fc9274c91aa',
        '97b6b97bd19801ec9210c965cc920e','97bcf97c359801ec95f8c965cc920f','97bd097bd07f595b0b6fc920fb0722',
        '9778397bd097c36b0b6fc9210c8dc2','9778397bd19801ec9210c9274c920e','97b6b97bd19801ec95f8c965cc920f',
        '97bd07f5307f595b0b0bc920fb0722','7f0e397bd097c36b0b6fc9210c8dc2','9778397bd097c36c9210c9274c920e',
        '97b6b97bd19801ec95f8c965cc920f','97bd07f5307f595b0b0bc920fb0722','7f0e397bd097c36b0b6fc9210c8dc2',
        '9778397bd097c36c9210c9274c91aa','97b6b97bd19801ec9210c965cc920e','97bd07f1487f595b0b0bc920fb0722',
        '7f0e397bd097c36b0b6fc9210c8dc2','9778397bd097c36b0b6fc9274c91aa','97b6b97bd19801ec9210c965cc920e',
        '97bcf7f1487f595b0b0bb0b6fb0722','7f0e397bd097c35b0b6fc920fb0722','9778397bd097c36b0b6fc9274c91aa',
        '97b6b97bd19801ec9210c965cc920e','97bcf7f1487f595b0b0bb0b6fb0722','7f0e397bd097c35b0b6fc920fb0722',
        '9778397bd097c36b0b6fc9274c91aa','97b6b97bd19801ec9210c965cc920e','97bcf7f1487f531b0b0bb0b6fb0722',
        '7f0e397bd097c35b0b6fc920fb0722','9778397bd097c36b0b6fc9274c91aa','97b6b97bd19801ec9210c965cc920e',
        '97bcf7f1487f531b0b0bb0b6fb0722','7f0e397bd07f595b0b6fc920fb0722','9778397bd097c36b0b6fc9274c91aa',
        '97b6b97bd19801ec9210c9274c920e','97bcf7f0e47f531b0b0bb0b6fb0722','7f0e397bd07f595b0b0bc920fb0722',
        '9778397bd097c36b0b6fc9210c91aa','97b6b97bd197c36c9210c9274c920e','97bcf7f0e47f531b0b0bb0b6fb0722',
        '7f0e397bd07f595b0b0bc920fb0722','9778397bd097c36b0b6fc9210c8dc2','9778397bd097c36c9210c9274c920e',
        '97b6b7f0e47f531b0723b0b6fb0722','7f0e37f5307f595b0b0bc920fb0722','7f0e397bd097c36b0b6fc9210c8dc2',
        '9778397bd097c36b0b70c9274c91aa','97b6b7f0e47f531b0723b0b6fb0721','7f0e37f1487f595b0b0bb0b6fb0722',
        '7f0e397bd097c35b0b6fc9210c8dc2','9778397bd097c36b0b6fc9274c91aa','97b6b7f0e47f531b0723b0b6fb0721',
        '7f0e27f1487f595b0b0bb0b6fb0722','7f0e397bd097c35b0b6fc920fb0722','9778397bd097c36b0b6fc9274c91aa',
        '97b6b97bd19801ec9210c9274c920e','97bcf7f0e47f531b0b0bb0b6fb0722','7f0e397bd07f595b0b0bc920fb0722',
        '9778397bd097c36b0b6fc9210c91aa','97b6b97bd197c36c9210c9274c920e','97bcf7f0e47f531b0b0bb0b6fb0722',
        '7f0e397bd07f595b0b0bc920fb0722','9778397bd097c36b0b6fc9210c8dc2','9778397bd097c36c9210c9274c920e',
        '97b6b7f0e47f531b0723b0b6fb0722','7f0e37f5307f595b0b0bc920fb0722','7f0e397bd097c36b0b6fc9210c8dc2',
        '9778397bd097c36b0b70c9274c91aa','97b6b7f0e47f531b0723b0b6fb0721','7f0e37f1487f595b0b0bb0b6fb0722',
        '7f0e397bd097c35b0b6fc9210c8dc2','9778397bd097c36b0b6fc9274c91aa','97b6b7f0e47f531b0723b0b6fb0721',
        '7f0e27f1487f595b0b0bb0b6fb0722','7f0e397bd097c35b0b6fc920fb0722','9778397bd097c36b0b6fc9274c91aa',
        '97b6b7f0e47f531b0723b0b6fb0721','7f0e27f1487f531b0b0bb0b6fb0722','7f0e397bd097c35b0b6fc920fb0722',
        '9778397bd097c36b0b6fc9274c91aa','97b6b7f0e47f531b0723b0b6fb0721','7f0e27f1487f531b0b0bb0b6fb0722',
        '7f0e397bd097c35b0b6fc920fb0722','9778397bd097c36b0b6fc9274c91aa','97b6b7f0e47f531b0723b0b6fb0721',
        '7f0e27f1487f531b0b0bb0b6fb0722','7f0e397bd07f595b0b0bc920fb0722','9778397bd097c36b0b6fc9274c91aa',
        '97b6b7f0e47f531b0723b0787b0721','7f0e27f0e47f531b0b0bb0b6fb0722','7f0e397bd07f595b0b0bc920fb0722',
        '9778397bd097c36b0b6fc9210c91aa','97b6b7f0e47f149b0723b0787b0721','7f0e27f0e47f531b0723b0b6fb0722',
        '7f0e397bd07f595b0b0bc920fb0722','9778397bd097c36b0b6fc9210c8dc2','977837f0e37f149b0723b0787b0721',
        '7f07e7f0e47f531b0723b0b6fb0722','7f0e37f5307f595b0b0bc920fb0722','7f0e397bd097c35b0b6fc9210c8dc2',
        '977837f0e37f14998082b0787b0721','7f07e7f0e47f531b0723b0b6fb0721','7f0e37f1487f595b0b0bb0b6fb0722',
        '7f0e397bd097c35b0b6fc9210c8dc2','977837f0e37f14998082b0787b06bd','7f07e7f0e47f531b0723b0b6fb0721',
        '7f0e27f1487f531b0b0bb0b6fb0722','7f0e397bd097c35b0b6fc920fb0722','977837f0e37f14998082b0787b06bd',
        '7f07e7f0e47f531b0723b0b6fb0721','7f0e27f1487f531b0b0bb0b6fb0722','7f0e397bd097c35b0b6fc920fb0722',
        '977837f0e37f14998082b0787b06bd','7f07e7f0e47f531b0723b0b6fb0721','7f0e27f1487f531b0b0bb0b6fb0722',
        '7f0e397bd07f595b0b0bc920fb0722','977837f0e37f14998082b0787b06bd','7f07e7f0e47f531b0723b0b6fb0721',
        '7f0e27f1487f531b0b0bb0b6fb0722','7f0e397bd07f595b0b0bc920fb0722','977837f0e37f14998082b0787b06bd',
        '7f07e7f0e47f149b0723b0787b0721','7f0e27f0e47f531b0b0bb0b6fb0722','7f0e397bd07f595b0b0bc920fb0722',
        '977837f0e37f14998082b0723b06bd','7f07e7f0e37f149b0723b0787b0721','7f0e27f0e47f531b0723b0b6fb0722',
        '7f0e397bd07f595b0b0bc920fb0722','977837f0e37f14898082b0723b02d5','7ec967f0e37f14998082b0787b0721',
        '7f07e7f0e47f531b0723b0b6fb0722','7f0e37f1487f595b0b0bb0b6fb0722','7f0e37f0e37f14898082b0723b02d5',
        '7ec967f0e37f14998082b0787b0721','7f07e7f0e47f531b0723b0b6fb0722','7f0e37f1487f531b0b0bb0b6fb0722',
        '7f0e37f0e37f14898082b0723b02d5','7ec967f0e37f14998082b0787b06bd','7f07e7f0e47f531b0723b0b6fb0721',
        '7f0e37f1487f531b0b0bb0b6fb0722','7f0e37f0e37f14898082b072297c35','7ec967f0e37f14998082b0787b06bd',
        '7f07e7f0e47f531b0723b0b6fb0721','7f0e27f1487f531b0b0bb0b6fb0722','7f0e37f0e37f14898082b072297c35',
        '7ec967f0e37f14998082b0787b06bd','7f07e7f0e47f531b0723b0b6fb0721','7f0e27f1487f531b0b0bb0b6fb0722',
        '7f0e37f0e366aa89801eb072297c35','7ec967f0e37f14998082b0787b06bd','7f07e7f0e47f149b0723b0787b0721',
        '7f0e27f1487f531b0b0bb0b6fb0722','7f0e37f0e366aa89801eb072297c35','7ec967f0e37f14998082b0723b06bd',
        '7f07e7f0e47f149b0723b0787b0721','7f0e27f0e47f531b0723b0b6fb0722','7f0e37f0e366aa89801eb072297c35',
        '7ec967f0e37f14998082b0723b06bd','7f07e7f0e37f14998083b0787b0721','7f0e27f0e47f531b0723b0b6fb0722',
        '7f0e37f0e366aa89801eb072297c35','7ec967f0e37f14898082b0723b02d5','7f07e7f0e37f14998082b0787b0721',
        '7f07e7f0e47f531b0723b0b6fb0722','7f0e36665b66aa89801e9808297c35','665f67f0e37f14898082b0723b02d5',
        '7ec967f0e37f14998082b0787b0721','7f07e7f0e47f531b0723b0b6fb0722','7f0e36665b66a449801e9808297c35',
        '665f67f0e37f14898082b0723b02d5','7ec967f0e37f14998082b0787b06bd','7f07e7f0e47f531b0723b0b6fb0721',
        '7f0e36665b66a449801e9808297c35','665f67f0e37f14898082b072297c35','7ec967f0e37f14998082b0787b06bd',
        '7f07e7f0e47f531b0723b0b6fb0721','7f0e26665b66a449801e9808297c35','665f67f0e37f1489801eb072297c35',
        '7ec967f0e37f14998082b0787b06bd','7f07e7f0e47f531b0723b0b6fb0721','7f0e27f1487f531b0b0bb0b6fb0722'
    ]
    TERMS_LIST = [
        u"小寒", u"大寒", u"立春", u"雨水", u"惊蛰", u"春分", u"清明", u"谷雨", u"立夏", u"小满",
        u"芒种", u"夏至", u"小暑", u"大暑", u"立秋", u"处暑", u"白露", u"秋分", u"寒露", u"霜降",
        u"立冬", u"小雪", u"大雪", u"冬至"]
    LUNAR_MONTH = [u'正', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十', u'冬', u'腊']
    LUNAR_DAY = [u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十']
    LUNAR_FIRST = 1984
    LUNAR_TIAN = [u'甲', u'乙', u'丙', u'丁', u'戊', u'己', u'庚', u'辛', u'壬', u'癸']
    LUNAR_DIZHI = [u'子', u'丑', u'寅', u'卯', u'辰', u'巳', u'午', u'未', u'申', u'酉', u'戌', u'亥']
    SOLAR_HOLIDAY = {
        '01-01': u'元旦节',
        '02-02': u'湿地日',
        '02-14': u'情人节',
        '03-08': u'妇女节',
        '03-12': u'植树节',
        '03-15': u'消费者日',
        '04-01': u'愚人节',
        '04-22': u'地球日',
        '05-01': u'劳动节',
        '05-04': u'青年节',
        '05-08': u'微笑日',
        '05-12': u'护士节',
        '05-18': u'博物馆日',
        '05-31': u'无烟日',
        '06-01': u'儿童节',
        '06-05': u'环境日',
        '06-23': u'奥林匹克',
        '1921-07-01': u'建党日',
        '08-01': u'建军节',
        '1945-08-15': u'日本投降',
        '09-10': u'教师节',
        '1945-09-03': u'抗战胜利',
        '09-18': u'九一八',
        '10-01': u'国庆节',
        '1911-10-10': u'辛亥革命',
        '10-24': u'程序员节',
        '10-31': u'万圣夜',
        '11-11': u'光棍节',
        '12-01': u'艾滋病日',
        '12-13': u'公祭日',
        '1999-12-20': u'澳门回归',
        '12-25': u'圣诞节'
    }
    LUNAR_HOLIDAY = {
        '01-01': u'春节',
        '01-15': u'元宵节',
        '02-02': u'龙抬头',
        '03-03': u'上巳节',
        '05-05': u'端午节',
        '07-07': u'七夕节',
        '08-15': u'中秋节',
        '09-09': u'重阳节',
        '12-08': u'腊八节',
        '12-23': u'小年',
        '12-30': u'除夕'
    }
