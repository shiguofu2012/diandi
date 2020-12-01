# coding=utf-8
# !/usr/bin/python

# from flask import url_for
import os
import uuid
import time
from datetime import datetime
from weixin.models.tbk_goods import TbkGoods, TbkBanner, TbkMenuConfig, \
        TbkHotWord
from weixin.models.category_model import Category
from weixin.models.tbk_material import get_project_by_id, get_material_by_id
from weixin.utils.tbk_api import generate_tpw, get_goods_info
from weixin.utils.tbk_client import TBK_CLIENT as tbk_client, SearchParams
from weixin.utils.image_utility import draw_tbk_share, get_url_from_path
from weixin.utils.httpclient import HttpClient
from weixin.utils.constants import TBK_PATH
from weixin.cache.tpw_cache import cache_coupon_info, get_cache_coupon,\
    save_goods_info, get_goods_info_by_id
from weixin.settings import LOGGER as LOG
from crawler.tbk_crawler.tbk_crawler import _ship_goods_supers
from weixin.views.xcx_data import create_qrcode


def get_project(_id):
    data = get_project_by_id(_id)
    return {'errcode': 0, 'data': data}


def get_material(_id):
    data = get_material_by_id(_id)
    return {'errcode': 0, 'data': data}


def get_tbk_hot_words():
    hot_word_obj = TbkHotWord(enabled=1)
    words = hot_word_obj.all_hot_words()
    return map(lambda x: x['word'], words)


def get_tbk_config(config_data):
    if not config_data.get("switch", 0):
        return {}
    banner = get_miniapp_banner()
    menu_config = get_menu_config()
    menu_config.update({'banner': banner})
    return menu_config


def get_miniapp_banner():
    banner_instance = TbkBanner()
    return banner_instance.get_banners()


def get_menu_config():
    menu_config = TbkMenuConfig()
    return menu_config.get_config_tabs()


def list_category(page=1, count=50):
    category_obj = Category()
    cats = category_obj.all_category(page, count)
    return map(_ship_db_category, cats)


def list_goods(cid=None, page=1, count=20):
    goods_obj = TbkGoods()
    cond = {'coupon_expire': 0}
    if cid:
        cond.update({'category_id': cid})
    goods = goods_obj.find_goods_by_cond(cond, page, count)
    goods_list = map(_ship_db_goods, goods)
    return {'goods': goods_list}


def delete_goods(goods_id):
    goods_obj = TbkGoods(num_id=goods_id)
    ret = goods_obj.delete()
    if ret.get("n") == 1:
        return True
    return False


def goods_detail(goods_id):
    goods = get_goods_info_by_id(goods_id)
    if not goods:
        goods_instance = TbkGoods(num_id=goods_id)
        goods = goods_instance.find_goods_by_id()
        if not goods:
            return False, u"找不到该商品"
    return True, _ship_db_goods(goods)


def _ship_db_category(category_data):
    cate_data = {}
    cate_data['id'] = category_data['id']
    cate_data['name'] = category_data['name']
    return cate_data


def _ship_db_goods(goods):
    ret_data = {}
    ret_data['id'] = goods['num_id']
    ret_data['title'] = goods['title']
    ret_data['is_tmall'] = goods['is_tmall']
    ret_data['coupon_start'] = goods['start']
    ret_data['coupon_end'] = goods['end']
    ret_data['images'] = goods.get('images', [])
    ret_data['sales'] = int(goods['sales'])
    ret_data['price'] = float(goods['price'])
    ret_data['price'] = round(ret_data['price'], 2)
    ret_data['coupon_amount'] = float(goods['coupon_amount'])
    ret_data['coupon_amount'] = round(ret_data['coupon_amount'], 2)
    ret_data['pic_url'] = goods['pic_url']
    ret_data['expire'] = goods.get('coupon_expire', 0)
    ret_data['coupon_remain'] = goods.get("coupon_remain", 0)
    ret_data['coupon_total'] = goods.get("coupon_total_count", 0)
    if ret_data['coupon_total'] == 0:
        ret_data['coupon_percent'] = 0
    else:
        ret_data['coupon_percent'] = int((
            ret_data['coupon_total'] - ret_data['coupon_remain']) /
            ret_data['coupon_total'] * 100)
    if ret_data['coupon_percent'] == 0:
        ret_data['coupon_percent'] = 1
    ret_data['coupon_percent'] += 20
    ret_data['coupon_fee'] = float(goods['price']) - \
        float(goods['coupon_amount'])
    ret_data['coupon_fee'] = round(ret_data['coupon_fee'], 2)
    com_rate = goods.get("commssion_rate", 0.01)
    ret_data['commssion_money'] = round(
            ret_data['coupon_fee'] * float(com_rate) * 0.2, 2)
    if ret_data['commssion_money'] == 0:
        ret_data['commssion_money'] = 0.01
    return ret_data


def _ship_coupon_goods(goods):
    ret_data = {}
    coupon_url = goods['coupon_share_url']
    title = goods['title']
    ret_data['coupon_url'] = coupon_url
    ret_data['num_iid'] = goods['num_id']
    tpw = generate_tpw(coupon_url, title, goods['pic_url'])
    ret_data['coupon_tpw'] = tpw
    return ret_data


def goods_tpw(goods_id):
    cache_key = goods_id
    data = get_cache_coupon(cache_key)
    if data:
        return {"errcode": 0, 'data': data}
    res = {'errcode': -1}
    goods = get_goods_info_by_id(goods_id)
    if not goods:
        goods_instance = TbkGoods(num_id=goods_id)
        goods = goods_instance.find_goods_by_id()
    if goods:
        msg = _ship_coupon_goods(goods)
        cache_coupon_info(cache_key, msg, 3600)
        res.update({'errcode': 0, 'data': msg})
    else:
        search_res = search_coupon_by_id(goods_id)
        if search_res.get("errcode") == 0:
            msg = search_res['data']
            cache_coupon_info(cache_key, msg, 3600)
            res.update({'errcode': 0, 'data': msg})
        else:
            res.update({'errmsg': u"找不到该商品"})
    # return succ, msg
    return res


def similar_goods(goods_id):
    goods = get_goods_info_by_id(goods_id)
    if not goods:
        goods_instance = TbkGoods(num_id=goods_id)
        goods = goods_instance.find_goods_by_id()
        if not goods:
            return True, []
    similar_goods_ids = goods.get("similar_goods", [])
    goods_obj = TbkGoods()
    if similar_goods_ids:
        cond = {'num_id': {'$in': similar_goods_ids}, 'coupon_expire': 0}
    else:
        cond = {"coupon_expire": 0}
    goods_list = goods_obj.find_goods_by_cond(
            cond, 1, 100).sort([('sales', -1)]).limit(20)
    result = []
    for goods in goods_list:
        tmp = _ship_db_goods(goods)
        if tmp['is_tmall']:
            tmp['is_tmall'] = 'inline'
        else:
            tmp['is_tmall'] = 'none'
        result.append(tmp)
    return True, result


def _super_search(sp, client):
    try_times = 3
    result = None
    while try_times > 0:
        try_times -= 1
        result = client.super_search(sp)
        if result.get("errcode") == 0:
            break
        else:
            time.sleep(0.1)
    return result


def super_search(params):
    keyword = params.get("keyword")
    if keyword is None:
        return False, u"搜索关键字不能为空"
    page = params.get("page", 1)
    count = params.get("count", 50)
    is_tmall = params.get("is_tmall")
    if isinstance(page, (unicode, str)) and not page.isdigit() or\
            (isinstance(count, (unicode, str)) and not count.isdigit()):
        return False, u"page非法"
    sp = SearchParams()
    sp.keyword = keyword
    sp.page = int(page)
    sp.count = int(count)
    sp.is_tmall = 'true' if is_tmall else 'false'
    result = []
    try:
        # result = tbk_client.super_search(sp)
        result = _super_search(sp, tbk_client)
        result = result['tbk_dg_material_optional_response'][
                'result_list']['map_data']
    except Exception as ex:
        LOG.error("super search ex: %s, word: %s", ex, keyword)
        return False, u"数据异常： %s" % ex
    goods_data = []
    for goods in result:
        tmp = _ship_goods_supers(goods)
        if not tmp:
            continue
        num_id = tmp['num_id']
        save_goods_info(num_id, tmp)
        tmp = _ship_db_goods(tmp)
        goods_data.append(tmp)
    return True, goods_data


def search_coupon_by_id(num_iid, TBK_REQ_CLIENT=None, fields_goods=False):
    if TBK_REQ_CLIENT:
        client = TBK_REQ_CLIENT
    else:
        client = tbk_client
    res = {'errcode': -1}
    goods_info = get_goods_info(num_iid)
    if not goods_info:
        res.update({'errmsg': u"商品不存在"})
        return res
    title = goods_info['title']
    page = 1
    count = 200
    sp = SearchParams()
    sp.keyword = title
    sp.page = int(page)
    sp.count = int(count)
    sp.is_tmall = 'false'
    sp.has_coupon = 'false'
    result = []
    try:
        # result = client.super_search(sp)
        result = _super_search(sp, client)
        result = result['tbk_dg_material_optional_response'][
                'result_list']['map_data']
    except Exception as ex:
        LOG.error("super search ex: %s, word: %s", ex, title, exc_info=True)
        res.update({'errmsg': u"exception: %s" % ex})
        return res
    coupon_share_url = ''
    for goods in result:
        goods = _ship_goods_supers(goods)
        search_id = goods.get("num_id")
        if not search_id:
            continue
        LOG.info(
                "title: %s, good: %s, coupon: %s", title, goods['title'],
                goods['coupon_amount'])
        if num_iid == goods['num_id']:
            coupon_share_url = goods['coupon_share_url']
            break
    if not coupon_share_url:
        res.update({'errmsg': u"获取失败，请稍后重试"})
        return res
    if fields_goods:
        data = goods
    else:
        tpw = generate_tpw(coupon_share_url, title, goods['pic_url'])
        data = {
                'coupon_tpw': tpw,
                'num_iid': num_iid,
                "coupon_url": coupon_share_url
                }
    res.update({'errcode': 0, 'data': data})
    return res


def share_tbk_image(goods_id, params=None):
    from mini_goods import miniapp_goods_detail
    # goods = get_goods_info_by_id(goods_id)
    # if not goods:
    #     goods_instance = TbkGoods(num_id=goods_id)
    #     goods = goods_instance.find_goods_by_id()
    #     if not goods:
    #         return False, u"找不到该商品"
    if params:
        mid = params.get("mid")
        data = miniapp_goods_detail(goods_id, mid)
    else:
        data = miniapp_goods_detail(goods_id)
    if data['errcode'] != 0:
        return False, data.get("errmsg", "")
    goods = data['data']
    scene = "id={}&t=1".format(goods_id)
    if params:
        user_config = params['user_config']
        qr_data = create_qrcode(
                scene,
                page='pages/goods/detail/index',
                appid=user_config['appid'],
                appsec=user_config['appsec'])
    else:
        qr_data = create_qrcode(scene)
    local_qr_path = qr_data['local_path']
    banner = goods['pic_url']
    client = HttpClient()
    data = client.get(banner)
    path = os.path.join(TBK_PATH, datetime.now().strftime("%Y-%m-%d"))
    if not os.path.exists(path):
        os.makedirs(path)
    banner_path = os.path.join(path, uuid.uuid4().hex)
    with open(banner_path, 'w') as _file:
        _file.write(data)
    sales = goods['sales']
    coupon_amount = goods['coupon_amount']
    coupon_fee = float(goods['price']) - float(coupon_amount)
    if sales < 10000:
        sales = str(sales)
    else:
        sales = str(round(float(sales) / 10000.0, 2)) + u'万'
    path = draw_tbk_share(
            local_qr_path, banner_path, goods['title'],
            goods['price'], round(coupon_fee, 2), sales)
    return True, get_url_from_path(path)
