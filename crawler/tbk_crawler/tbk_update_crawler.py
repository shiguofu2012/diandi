# coding=utf-8

import time
from multiprocessing.pool import ThreadPool
from weixin.models.tbk_goods import TbkGoods
from weixin.settings import LOG_CRAWLER as LOG
from weixin.utils.tbk_client import TBK_CRAWLER_CLIENT as client, SearchParams
from tbk_crawler import _ship_goods_supers


def _super_search(sp):
    try_times = 3
    result = None
    while try_times > 0:
        try_times -= 1
        result = client.super_search(sp)
        if result.get("errcode") == 0:
            break
        else:
            time.sleep(1)
    if result['errcode'] != 0:
        return []
    return result['tbk_dg_material_optional_response'][
                'result_list']['map_data']


def update_worker(goods_list, page):
    start = time.time()
    LOG.info("page: %s, start: %s", page, start)
    for goods in goods_list:
        now = time.time() * 1000
        update_time = goods.get("update_time")
        if update_time and now - update_time < 3600000:
            continue
        title = goods['title']
        _id = goods['num_id']
        sp = SearchParams()
        sp.page = 1
        sp.count = 100
        sp.keyword = title
        data = _super_search(sp)
        ok = 0
        for g in data:
            goods_data = _ship_goods_supers(g)
            if goods_data['num_id'] == _id:
                ok = 1
                goods_obj = TbkGoods(**goods_data)
                goods_obj.save()
                break
        if not ok:
            goods_obj = TbkGoods(num_id=_id)
            goods_obj.delete()
            LOG.info("delete id: %s", _id)
    del goods_list
    LOG.info("page: %s process ok: %s", page, time.time() - start)


def update_main():
    page = 20
    count = 2000
    more_data = True
    pool = ThreadPool(16)
    goods_obj = TbkGoods()
    last_id = ''
    while more_data:
        # more_data = False
        if last_id:
            cond = {'_id': {'$gt': last_id}}
        else:
            cond = {}
        goods_list = goods_obj.find_goods_by_cond(
                cond, page, count, ['title', 'num_id', 'update_time'])
        last_id = ''
        for goods in goods_list:
            last_id = goods['_id']
        if not last_id:
            print("done")
            break
        # goods_list = list(goods_list)
        # if len(goods_list) < count:
        #     more_data = False
        #     break
        # else:
        #     more_data = True
        LOG.info("page: %s ok", page)
        # pool.apply_async(update_worker, (goods_list, page))
        page += 1
    pool.close()
    pool.join()


update_main()
