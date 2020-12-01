# coding=utf-8

import json
from weixin.cache import tbk_cache


def cache_coupon_info(goods_id, coupon_info, expire=3600):
    return tbk_cache.save_dict(goods_id, coupon_info, expire)


def get_cache_coupon(goods_id):
    return tbk_cache.hget(goods_id)


def save_goods_info(num_id, goods_data):
    key = 'goods_info_' + str(num_id)
    return tbk_cache.set(key, json.dumps(goods_data), 1800)


def get_goods_info_by_id(num_id):
    key = 'goods_info_' + str(num_id)
    data = tbk_cache.get(key)
    if data:
        data = json.loads(data)
    return data


def get_goods_by_key(goods_key):
    data = tbk_cache.get(goods_key)
    if data:
        data = json.loads(data)
    return data


def all_cached_goods():
    key = 'goods_info_*'
    return tbk_cache.keys(key)
