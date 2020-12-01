#!/usr/bin/python
# coding=utf-8
'''
wrapper for tbk api;
'''
import re
import requests
from weixin.utils.tbk_client import TBK_CRAWLER_CLIENT as tbk_client
from weixin.settings import LOGGER as _LOGGER

_ID_PATTERN = u'\\.taobao\\.com.*[\\&\\?_]id=(?P<id>\\d+)'


def get_goods_info(num_iid):
    resp = tbk_client.tbk_goods_info(num_iid)
    if resp is None:
        return {}
    goods_info = resp.get(
        'tbk_item_info_get_response', {}).get(
        "results", {}).get("n_tbk_item", [])
    ret_goods_info = {}
    if len(goods_info) >= 1:
        _id = long(goods_info[0]['num_iid'])
        title = goods_info[0]['title']
        pic_url = goods_info[0]['pict_url']
        price = round(float(goods_info[0]['zk_final_price']), 2)
        sales = long(goods_info[0].get('volume', 0))
        tmall = long(goods_info[0]['user_type'])
        ret_goods_info['id'] = _id
        ret_goods_info['title'] = title
        ret_goods_info['pic_url'] = pic_url
        ret_goods_info['price'] = price
        ret_goods_info['sales_month'] = sales
        ret_goods_info['tmall'] = tmall
        ret_goods_info['images'] = goods_info[0].get('small_images', [])
    return ret_goods_info


def decrypt_tpw(tpw):
    '''
    from tpw to long url;
    '''
    resp = tbk_client.decrypt_tpw(tpw)
    _LOGGER.info(resp)
    if resp is None:
        return {}
    resp_data = resp.get('wireless_share_tpwd_query_response', {})
    tpw_info = {}
    suc = resp_data.get('suc')
    if suc:
        title = resp_data.get('content', '')
        coupon_url = resp_data['url']
        _id = get_gid_coupon_url(coupon_url)
        tpw_info['title'] = title
        tpw_info['id'] = _id
    return tpw_info


def generate_tpw(url, text, logo=''):
    resp = tbk_client.convert_tpw(url, text, logo) or {}
    tbk_tpw_info = resp.get('tbk_tpwd_create_response')
    if not tbk_tpw_info:
        return None
    data = tbk_tpw_info.get('data', {})
    return data.get('model', '')


def get_gid_coupon_url(coupon_url):
    '''
    get goods id from coupon url like "https://uland.taobao.com/coupon/edetail"
    '''
    pattern = re.compile(_ID_PATTERN)
    match = pattern.search(coupon_url)
    _id = 0
    if match:
        _id = match.group("id")
    else:
        location = ''
        try:
            resp = requests.head(coupon_url)
            headers = resp.headers
            location = headers.get('location')
        except Exception as ex:
            _LOGGER.error("head url: %s, ex: %s", coupon_url, ex)
        if location:
            match = pattern.search(location)
            if match:
                _id = match.group('id')
    return long(_id)
