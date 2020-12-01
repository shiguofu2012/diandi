# coding=utf-8

from weixin.models.tbk_goods import TbkGoods
from weixin.cache.tpw_cache import all_cached_goods, get_goods_by_key
from weixin.settings import LOG_CRAWLER as LOG


def save_search_data():
    keys = all_cached_goods()
    for key in keys:
        goods_info = get_goods_by_key(key)
        if goods_info:
            _save(goods_info)


def _save(goods_info):
    goods_obj = TbkGoods(**goods_info)
    goods_obj.source = 'search'
    ret = goods_obj.save()
    LOG.info("save goods: %s, ret: %s", goods_info['num_id'], ret)


if __name__ == '__main__':
    save_search_data()
