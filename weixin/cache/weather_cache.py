#!/usr/bin/python

import time
from weixin.cache import data_cache


def cache_ip_location(ip, location, expire=86400):
    return data_cache.set(ip, location, expire)


def get_ip_location(ip):
    return data_cache.get(ip)


def cache_city_weather(city, weather, expire=1800):
    return data_cache.set(city, weather, expire)


def get_city_weather(city):
    return data_cache.get(city)


def cache_lunar_date(date_str, lunar_info):
    return data_cache.set(date_str, lunar_info, 86400)


def get_lunar_date(date_str):
    return data_cache.get(date_str)
