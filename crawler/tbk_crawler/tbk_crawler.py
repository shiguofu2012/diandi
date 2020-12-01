#!/usr/bin/python
# coding=utf-8

import re
import copy
import argparse
import random
import time
from multiprocessing.pool import ThreadPool
from weixin.utils.tbk_client import TBK_CRAWLER_CLIENT as client, SearchParams
from weixin.utils.tbk_api import generate_tpw
from weixin.utils.lucene_searcher import SEARCHER_LUCENE as searcher
from weixin.models.tbk_goods import TbkGoods
from weixin.models.category_model import Category, SubCategory
from weixin.models.keywords import KeyWords
from weixin.settings import LOG_CRAWLER as LOG


TEXT_MSG = u"【产品】%s\n【原价】%s 元\n【券券】%s 元\n【券后价】%s 元\n【返利】%s 元\n"\
        u"【购买】复制这条信息，打开手机淘宝，%s\n"
COUPON_PATTERN = u"满(?P<coupon_start>\d+[\.\d+]*)元减"\
        u"(?P<coupon_amount>\d+[\.\d+]*)元"


def get_one_goods(cat=None):
    if cat is None:
        cat_obj = Category(recommend=1)
        cats = cat_obj.all_category()
        cat_list = []
        for cat in cats:
            cat_list.append(int(cat['id']))
        # cat_list = [1801, 16, 30, 50002766, 50006843, 122952001]
        cat_id = random.choice(cat_list)
    else:
        cat_id = cat
    start = time.time() - 8 * 86400
    cond = {
            "coupon_amount": {'$gt': 5},
            "created": {'$gt': start * 1000},
            "sales": {'$gt': 3000},
            'category_id': cat_id,
            "sended": {'$exists': False},
            "coupon_expire": 0
            }
    LOG.debug(cond)
    goods_obj = TbkGoods()
    goods = goods_obj.find_goods_by_cond(
            cond, 1, count=20)
    goods_list = list(goods)
    length = len(goods_list)
    if length == 0:
        return {}
    index = random.randint(0, length - 1)
    return goods_list[index]


def get_send_goods(cat_id=None):
    goods = get_one_goods(cat_id)
    if not goods:
        return
    title = goods['title']
    price = goods['price']
    coupon_amount = goods['coupon_amount']
    coupon_url = goods['coupon_share_url']
    pic_url = goods['pic_url']
    tpw = generate_tpw(coupon_url, title, pic_url)
    goods_obj = TbkGoods(num_id=goods['num_id'])
    goods_obj.update({"sended": 1})
    if not tpw:
        return
    new_price = round(float(float(price) - coupon_amount), 2)
    commssion_rate = goods['commssion_rate']
    commssion_fee = round(new_price * float(commssion_rate) * 0.2, 2)
    msg = TEXT_MSG % (title, price, coupon_amount, new_price, commssion_fee, tpw)
    return {'pic_url': pic_url, 'msg': msg, 'goods': goods}


def _ship_goods_supers(item):
    pattern = re.compile(COUPON_PATTERN)
    goods_data = {}
    try:
        coupon_share_url = item.get('coupon_share_url')
        if not coupon_share_url:
            coupon_share_url = item['url']
        if coupon_share_url and not coupon_share_url.startswith(('http', 'https')):
            coupon_share_url = 'https:' + coupon_share_url
        goods_data['category_id'] = item['level_one_category_id']
        goods_data['sub_category_id'] = item['category_id']
        goods_data['small_images'] = item.get("small_images", {}).get(
                "string", [])
        # goods_data['big_images'] = goods_data['small_images']
        goods_data['is_tmall'] = item['user_type']
        goods_data['coupon_id'] = item['coupon_id']
        goods_data['coupon_share_url'] = coupon_share_url
        goods_data['sales'] = int(item['volume'])
        goods_data['coupon_info'] = item['coupon_info']
        coupon_data = re.search(pattern, item['coupon_info'])
        if coupon_data:
            goods_data['coupon_start'] = float(
                    coupon_data.group("coupon_start"))
            goods_data['coupon_amount'] = float(
                    coupon_data.group("coupon_amount"))
        else:
            goods_data['coupon_start'] = 0
            goods_data['coupon_amount'] = 0
        goods_data['commssion_rate'] = float(
                float(item['commission_rate']) / 10000.0)
        goods_data['coupon_total_count'] = int(item['coupon_total_count'])
        goods_data['shop_id'] = item.get("seller_id", 0)
        goods_data['shop_title'] = item.get("nick", '')
        goods_data['category_name'] = item.get('level_one_category_name', '')
        # goods_data['sub_category_name'] = item.get('category_name')
        goods_data['end'] = item.get('coupon_end_time', '')
        goods_data['start'] = item.get('coupon_start_time', '')
        goods_data['price'] = round(float(item['zk_final_price']), 2)
        goods_data['coupon_fee'] = goods_data['price'] - goods_data['coupon_amount']
        goods_data['num_id'] = item['num_iid']
        goods_data['created'] = int(time.time() * 1000)
        goods_data['update_time'] = int(time.time() * 1000)
        goods_data['pic_url'] = item['pict_url']
        goods_data['title'] = item['title']
        goods_data['coupon_remain'] = int(item['coupon_remain_count'])
    except Exception as ex:
        LOG.error("crawler item: %s, error: %s", item, ex, exc_info=True)
        goods_data = {}
    if item.get("category_id"):
        goods_data.update({"sub_category_id": item.get("category_id")})
    if item.get("category_name"):
        goods_data.update({"sub_category_name": item.get("category_name")})
    return goods_data


def _crawler(**kwargs):
    keys = (
            "keyword", "page", "count", "platform", "is_overseas", "is_tmall",
            "sort", "has_coupon", "need_free_shipment", "cat")
    sp = SearchParams()
    for key in keys:
        if kwargs.get(key):
            sp[key] = kwargs[key]
    try:
        res = client.super_search(sp)
        return res['tbk_dg_material_optional_response'][
                'result_list']['map_data']
    except Exception as ex:
        LOG.error("ex: %s", ex, exc_info=True)


def _search_by_id(goods_id, title):
    goods_list = _crawler(keyword=title, page=1, count=100)
    if goods_list is None:
        return
    for goods in goods_list:
        num_iid = goods['num_iid']
        if num_iid == goods_id:
            return _ship_goods_supers(goods)


def update_goods(keyword, num_id, table):
    goods_info = _search_by_id(num_id, keyword)
    if goods_info:
        goods_instance = TbkGoods(**goods_info)
        goods_info.update({'table': table})
        searcher.update_index(goods_info)
        goods_instance.save()
    else:
        goods_instance = TbkGoods(num_id=num_id)
        goods_instance.disabled_goods_by_id()
        searcher.delete_index(num_id)


def crawler(keyword, page, count, cat_list=''):
    if cat_list and isinstance(cat_list, list):
        cat = ','.join(cat_list)
    else:
        cat = ''
    goods_list = _crawler(keyword=keyword, page=page, count=count, cat=cat)
    if goods_list is None:
        return []
    result = []
    for goods in goods_list:
        tmp = _ship_goods_supers(goods)
        if not tmp:
            continue
        tmp.update({'table': 'goods'})
        cat_obj = Category(id=tmp['category_id'], name=tmp['category_name'])
        cat_obj.save_category()
        if tmp.get("sub_category_id"):
            cat_obj = SubCategory(
                    id=tmp['sub_category_id'],
                    name=tmp.get('sub_category_name', ''),
                    parent=tmp['category_id'])
            cat_obj.save_category()
        source = keyword if keyword else 'crawler'
        tmp.update({'source': source})
        goods_instance = TbkGoods(**tmp)
        if goods_instance.check_save():
            goods_info = goods_instance.find_goods_by_id()
            if not goods_info:
                similar_ids = crawler_similar(tmp['num_id'])
                goods_instance.similar_goods = similar_ids
                result.append(tmp)
            ret = goods_instance.save()
            searcher.update_index(tmp)
            LOG.debug(ret)
    return result


def crawler_similar(goods_id):
    res = client.tbk_goods_recommend(goods_id) or {}
    response = res['tbk_item_recommend_get_response']
    if response.get("results") is None:
        return
    goods_list = response['results'].get('n_tbk_item', [])
    similar_ids = []
    for goods in goods_list:
        num_iid = goods['num_iid']
        title = goods['title']
        similar_goods = _search_by_id(num_iid, title)
        if similar_goods is None:
            continue
        similar_ids.append(num_iid)
        similar_goods.update({'source': 'similar'})
        goods_instance = TbkGoods(**similar_goods)
        goods_instance.save()
    loop_ids = copy.deepcopy(similar_ids)
    for num_iid in loop_ids:
        goods_instance = TbkGoods(num_id=num_iid)
        goods_info = goods_instance.find_goods_by_id()
        if goods_info:
            ori_similar_ids = goods_info.get("similar_goods", [])
            if ori_similar_ids is not None:
                similar_ids.extend(ori_similar_ids)
        goods_instance.update({'similar_goods': list(set(similar_ids))})
        similar_ids = copy.deepcopy(loop_ids)
    return similar_ids


def update_similar():
    page = 6
    count = 100
    have_data = True
    goods_obj = TbkGoods()
    while have_data:
        have_data = False
        goods_list = goods_obj.find_goods_by_cond({}, page, count)
        for goods in goods_list:
            have_data = True
            if goods.get('similar_goods'):
                continue
            _id = goods['num_id']
            similar_ids = crawler_similar(_id)
            if similar_ids is None:
                continue
            goods_instance = TbkGoods(num_id=_id)
            goods_instance.update({'similar_goods': similar_ids})
        page += 1
        print page


def update_by_category():
    cat_obj = Category()
    cats = cat_obj.all_category()
    for cat in cats:
        cat_id = int(cat['id'])
        crawler(u"", 1, 100, [str(cat_id)])


def update_one_by_one(table):
    page = 1
    count = 1000
    have_data = True
    update_count = 0
    goods_obj = TbkGoods()
    goods_obj.__table__ = table
    LOG.info(table)
    while have_data:
        have_data = False
        goods_list = goods_obj.find_goods_by_cond(
                {}, page, count)
        now = int(time.time() * 1000)
        for goods in goods_list:
            have_data = True
            update_time = goods.get('update_time')
            if update_time and now - update_time < 3600000:
                continue
            update_goods(goods['title'], goods['num_id'], table)
        page += 1
        LOG.info("page: %s" % page)
    print(update_count)


def crawler_worker(keyword):
    total_page = 10
    count = 0
    start = time.time()
    for i in range(total_page):
        saved_list = crawler(keyword, i + 1, 100)
        count += len(saved_list)
    LOG.info(
            "keyword: %s, crawler: %s, takes: %s",
            keyword, count, time.time() - start)


def crawler_main():
    keywords_obj = KeyWords()
    page = 1
    count = 100
    pool = ThreadPool(15)
    have_more = True
    while have_more:
        have_more = False
        words = keywords_obj.get_keywords({}, page, count)
        for word in words:
            have_more = True
            pool.apply_async(crawler_worker, (word['word'], ))
        page += 1
    pool.close()
    pool.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--type',
            '-t', type=str, required=True, help='the type of the timed')
    parser.add_argument(
            '--keyword',
            '-k', type=str, required=False, help='crawler words')
    args = parser.parse_args()
    start = time.time()
    type_ = args.type
    if type_ == 'update':
        LOG.info("update start: %s", start)
        # update_by_category()
        tables = ['haitao', 'jiukjiu', 'juhuasuan', 'xiaoliangbang', 'goods']
        pool = ThreadPool(len(tables))
        for table in tables:
            pool.apply_async(update_one_by_one, (table, ))
        pool.close()
        pool.join()
        # update_one_by_one()
        LOG.info("update takes: %ss", time.time() - start)
    elif type_ == 'crawler':
        LOG.info("crawler start: %s", start)
        crawler_main()
        LOG.info("crawler takes: %s", time.time() - start)
    elif type_ == 'word':
        if args.keyword:
            crawler_worker(args.keyword)
        else:
            print("keyword not found")
    else:
        update_by_category()
