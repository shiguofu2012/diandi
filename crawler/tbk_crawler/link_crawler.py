# coding=utf-8

import re
import time
from urlparse import urlparse
import threadpool
from threadpool import ThreadPool
from weixin.models.tbk_material import get_links
from weixin.models.tbk_goods import TbkGoods
from weixin.utils.tbk_client import TBK_CRAWLER_CLIENT as tbk_client, \
        SearchParams
from weixin.utils.decorator import exception_handler_method
from weixin.utils.httpclient import HttpClient
from weixin.utils.tbk_api import get_goods_info
from weixin.utils.lucene_searcher import SEARCHER_LUCENE as searcher
from crawler.tbk_crawler.tbk_crawler import _ship_goods_supers
from weixin.settings import LOG_CRAWLER as LOG

PAGE_REGEX = ur"page=(?P<page>\d+)&?"


def get_next_page(link):
    pattern = re.compile(PAGE_REGEX)
    match = pattern.search(link)
    if match:
        page = match.group("page")
        try:
            page = int(page) + 1
            new_page = "page={}".format(page)
            link = pattern.sub(new_page, link)
        except Exception:
            pass
    return link


def _ship_goods(num_iid):
    ret_data = {}
    try:
        num_iid = int(num_iid)
    except Exception:
        return ret_data
    goods = get_goods_info(num_iid)
    if goods:
        title = goods['title']
        sp = SearchParams()
        sp.keyword = title
        sp.page = 1
        sp.count = 100
        sp.sort = 'total_sales_des'
        sp.has_coupon = 'false'
        result = tbk_client.super_search(sp)
        if result.get("errcode") != 0:
            return ret_data
        result = result['tbk_dg_material_optional_response'][
                'result_list']['map_data']
        for item in result:
            tmp = _ship_goods_supers(item)
            if tmp.get("num_id") == num_iid:
                ret_data = tmp
                break
    return ret_data


DATA_FIELD = {
        "public.immmmmm.com": {"res_data": "goods", "id": "tbid"},
        "xcx.67tui.com": {'res_data': "data", "id": "num_iid"}}


def crawler_one_page(link, table, mid):
    parse_ret = urlparse(link)
    domain = parse_ret.netloc
    config = DATA_FIELD.get(domain)
    if not config:
        LOG.info("domain: %s not config", domain)
        return
    res_data_field = config.get("res_data")
    id_field = config.get("id")
    start = time.time()
    client = HttpClient()
    res = client.get(link)
    goods_list = res.get(res_data_field, [])
    for goods in goods_list:
        num_id = goods.get(id_field)
        tmp = _ship_goods(num_id)
        if not tmp:
            continue
        tmp.update({'mid': mid})
        if isinstance(table, unicode):
            table = table.encode("utf-8")
        tmp.update({'table': table})
        searcher.update_index(tmp)
        goods_obj = TbkGoods(**tmp)
        goods_obj.__table__ = table
        goods_obj.save()
    LOG.info("link: %s takes: %s", link, time.time() - start)


@exception_handler_method
def crawler_link(link, table, mid):
    total_page = 30
    pool = ThreadPool(10)
    for i in range(total_page):
        params = {'link': link, 'table': table, 'mid': mid}
        req = threadpool.makeRequests(crawler_one_page, [(None, params)])
        pool.putRequest(req[0])
        # crawler_one_page(link)
        next_link = get_next_page(link)
        if next_link and next_link == link:
            break
        link = next_link
    pool.wait()


def main():
    page = 1
    links = get_links(page, 100)
    count = 1
    for link in links:
        if count == 1:
            count += 1
            continue
        url = link.get("link")
        table = link.get("table")
        mid = link.get("mid")
        if not url or not table or not mid:
            continue
        crawler_link(url, table, mid)


if __name__ == '__main__':
    main()
