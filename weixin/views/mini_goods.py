# coding=utf-8

import time
from wechat.api import WechatClient
from functools import wraps
from datetime import datetime, timedelta
from weixin.cache import data_cache
from weixin.models.tbk_goods import TbkMenuConfig, TbkGoods, TbkConfig
from weixin.models.category_model import Category
from weixin.models.tbk_material import get_table_by_mid
from weixin.utils.decorator import exception_handler_method, perf_logging
from weixin.utils.tbk_client import TbkApi
from weixin.utils.tbk_client import TBK_CLIENT as tbk_client, SearchParams
from weixin.utils.metaclass import register_handler
from weixin.utils.lucene_searcher import SEARCHER_LUCENE as searcher
from weixin.cache.tpw_cache import get_cache_coupon, cache_coupon_info
from weixin.cache.tpw_cache import save_goods_info, get_goods_info_by_id
from weixin.cache.session import cache_session
from weixin.views.tbk_views import search_coupon_by_id, _super_search
from weixin.views.do_goods import find_goods_info
from crawler.tbk_crawler.tbk_crawler import _ship_goods_supers
from weixin.settings import LOGGER as LOG

MID_MAP = {}


class GoodsTab(object):

    @exception_handler_method
    def validate(self, params):
        self.parent_id = int(params.get("mid"))
        self.tbk_menu_obj = TbkMenuConfig()
        if not self.tbk_menu_obj.get_parent_tab(self.parent_id):
            return {'errcode': -2, 'errmsg': u"参数mid错误"}
        self.cid = params.get("cid")
        self.tid = params.get("tid")
        if self.cid:
            self.cid = int(self.cid)
        if self.tid:
            self.tid = int(self.tid)
        self.page = int(params.get("page", 1))
        self.count = int(params.get("count", 20))
        if self.do_validate():
            return {'errcode': 0}
        return {'errcode': -1, 'errmsg': u"参数错误"}

    def do_validate(self):
        return True

    def get_category_id(self):
        tbk_menu_obj = TbkMenuConfig()
        menu_data = tbk_menu_obj.get_one_menu(self.cid) or {}
        cat_ids = menu_data.get('category_id')
        cat_cond = {}
        if not cat_ids:
            return cat_cond
        cat_obj = Category()
        cat_data = cat_obj.find_category_by_ids(cat_ids)
        cat_list = []
        sub_list = []
        for cat in cat_data:
            _id = int(cat['id'])
            parent = cat.get("parent")
            if parent and parent != 0:
                sub_list.append(_id)
                cat_list.append(int(parent))
            else:
                cat_list.append(_id)
        if sub_list:
            sub_list = list(set(sub_list))
            if len(sub_list) == 1:
                cat_cond.update({'sub_category_id': sub_list[0]})
            else:
                cat_cond.update({'sub_category_id': {'$in': sub_list}})
        if cat_list:
            cat_list = list(set(cat_list))
            if len(cat_list) == 1:
                cat_cond.update({'category_id': cat_list[0]})
            else:
                cat_cond.update({'category_id': {'$in': cat_list}})
        # if isinstance(cat_ids, list):
        #     if len(cat_ids) > 1:
        #         cat_cond.update({'category_id': {'$in': cat_ids}})
        #     else:
        #         cat_cond.update({'category_id': cat_ids[0]})
        # else:
        #     cat_cond.update({'category_id': cat_ids})
        return cat_cond

    def get_sort_field(self):
        if self.tid:
            self.tid = int(self.tid)
        SORT_MAP = {
                1: [('created', -1)], 2: [('sales', -1)],
                3: [('coupon_fee', 1)], 5: [('created', -1)],
                6: [('sales', -1)], 7: [('coupon_fee', 1)],
                8: [('coupon_amount', -1)]}
        return SORT_MAP.get(self.tid)

    def build_condition(self):
        return {}

    @perf_logging
    def get_data(self, params):
        res = self.validate(params)
        if res['errcode'] != 0:
            return res
        cond = self.build_condition()
        sort = self.get_sort_field()
        LOG.info("cond: %s, sort: %s", cond, sort)
        goods_obj = TbkGoods()
        ret = goods_obj.find_goods_by_cond(
                cond, self.page, self.count)
        if sort:
            ret.sort(sort)
        return {'errcode': 0, 'data': ret}


@register_handler(199, MID_MAP)
class Jiuk9(GoodsTab):

    def do_validate(self):
        return True

    def get_data(self, params):
        table = 'jiukjiu'
        res = self.validate(params)
        if res['errcode'] != 0:
            return res
        goods_obj = TbkGoods()
        goods_obj.__table__ = table
        sort = self.get_sort_field()
        ret = goods_obj.find_goods_by_cond({}, self.page, self.count)
        if sort:
            ret.sort(sort)
        return {'errcode': 0, 'data': ret}


@register_handler(200, MID_MAP)
class TopList(GoodsTab):

    def get_data(self, params):
        table = 'haitao'
        res = self.validate(params)
        if res['errcode'] != 0:
            return res
        goods_obj = TbkGoods()
        goods_obj.__table__ = table
        sort = self.get_sort_field()
        ret = goods_obj.find_goods_by_cond({}, self.page, self.count)
        if sort:
            ret.sort(sort)
        return {'errcode': 0, 'data': ret}


@register_handler(201, MID_MAP)
class Juhuasuan(GoodsTab):

    def get_data(self, params):
        table = 'juhuasuan'
        res = self.validate(params)
        if res['errcode'] != 0:
            return res
        goods_obj = TbkGoods()
        goods_obj.__table__ = table
        sort = self.get_sort_field()
        ret = goods_obj.find_goods_by_cond({}, self.page, self.count)
        if sort:
            ret.sort(sort)
        return {'errcode': 0, 'data': ret}


@register_handler(202, MID_MAP)
class HaiTao(GoodsTab):

    def get_data(self, params):
        table = 'haitao'
        res = self.validate(params)
        if res['errcode'] != 0:
            return res
        goods_obj = TbkGoods()
        goods_obj.__table__ = table
        sort = self.get_sort_field()
        ret = goods_obj.find_goods_by_cond({}, self.page, self.count)
        if sort:
            ret.sort(sort)
        return {'errcode': 0, 'data': ret}


@register_handler(210, MID_MAP)
class IFasion(GoodsTab):

    def do_validate(self):
        if self.cid is None or self.tid is None:
            return False
        self.cid = int(self.cid)
        self.tid = int(self.tid)
        return True

    def build_condition(self):
        today = datetime.now()
        start_day = today - timedelta(8)
        start = time.mktime(start_day.timetuple())
        cond = {
                "sales": {'$gte': 2000},
                'created': {'$gte': start * 1000},
                'coupon_amount': {'$gte': 5}
                }
        cat_cond = self.get_category_id()
        if cat_cond:
            cond.update(cat_cond)
        return cond


@register_handler(211, MID_MAP)
class Women(GoodsTab):

    def build_condition(self):
        today = datetime.now()
        start_day = today - timedelta(10)
        start = time.mktime(start_day.timetuple())
        cond = {
                "sales": {'$gte': 100},
                'created': {'$gte': start * 1000},
                'coupon_amount': {'$gte': 2}
                }
        cat_cond = self.get_category_id()
        if cat_cond:
            cond.update(cat_cond)
        return cond


@register_handler(212, MID_MAP)
class Home(GoodsTab):

    def build_condition(self):
        today = datetime.now()
        start_day = today - timedelta(8)
        start = time.mktime(start_day.timetuple())
        cond = {
                "sales": {'$gte': 2000},
                'created': {'$gte': start * 1000},
                'coupon_amount': {'$gte': 5}
                }
        cat_cond = self.get_category_id()
        if cat_cond:
            cond.update(cat_cond)
        return cond


@register_handler(213, MID_MAP)
class WomenBaby(GoodsTab):

    def build_condition(self):
        today = datetime.now()
        start_day = today - timedelta(8)
        start = time.mktime(start_day.timetuple())
        cond = {
                "sales": {'$gte': 2000},
                'created': {'$gte': start * 1000},
                'coupon_amount': {'$gte': 5}
                }
        cat_cond = self.get_category_id()
        if cat_cond:
            cond.update(cat_cond)
        return cond


@register_handler(90, MID_MAP)
class Default(GoodsTab):

    def do_validate(self):
        '''validate the sub menu id'''
        return True

    def build_condition(self):
        # cat_obj = Category(recommend=1)
        # cats = cat_obj.all_category()
        # cat_ids = map(lambda x: x['id'], cats)
        cat_cond = self.get_category_id()
        today = datetime.now()
        if self.tid is None:
            start = today - timedelta(3)
        else:
            start = today - timedelta(7)
        start = start.replace(hour=0, minute=0)
        start = time.mktime(start.timetuple()) * 1000
        cond = {
                'sales': {'$gte': 3000},
                "created": {'$gte': start},
                "coupon_amount": {'$gte': 5},
                }
        if cat_cond:
            cond.update(cat_cond)
        return cond


def check_key_wrapper(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        if '__error__' in kwargs:
            return func(*args, **kwargs)
        key = kwargs.get('key')
        config_obj = TbkConfig(key=key)
        config_data = config_obj.get_config_data()
        if not config_data:
            kwargs['__error__'] = {'errcode': -1, 'errmsg': u"key配置错误"}
        else:
            now = time.time()
            end = config_data.get('end')
            if now > end:
                kwargs['__error__'] = {
                        'errcode': -1,
                        'errmsg': u"已经到期，请及时续费"}
            else:
                kwargs['user_config'] = config_data
        return func(*args, **kwargs)

    return wrapper


def miniapp_tpw(kwargs):
    goods_id = kwargs['id']
    config_data = kwargs['user_config']
    api_key = config_data.get('api_key')
    api_sec = config_data.get('api_sec')
    pid = config_data.get("pid")
    if not api_key or not api_sec:
        return {'errcode': -1, 'errmsg': u"数据错误"}
    api_key = int(api_key)
    cache_key = '{}_{}'.format(api_key, goods_id)
    cached_tpw = get_cache_coupon(cache_key)
    if cached_tpw:
        return {'errcode': 0, 'data': cached_tpw}
    api_sec = api_sec.encode('utf-8') if isinstance(api_sec, unicode) else \
        api_sec
    pid = pid.encode("utf-8") if isinstance(pid, unicode) else pid
    client = TbkApi(api_key, api_sec, pid)
    res = search_coupon_by_id(goods_id, client)
    if res['errcode'] == 0:
        tpw_data = res['data']
        cache_coupon_info(cache_key, tpw_data, 3600)
    return res


def get_key_status(config_data):
    status = config_data.get("switch", 0)
    data = {'status': status}
    now = time.time()
    proxy_end = config_data.get("proxy_end")
    if proxy_end and now < proxy_end:
        data.update({'proxy_status': 1})
    else:
        data.update({'proxy_status': 0})
    return data


def _ship_miniapp(goods):
    '''
    tbk miniapp ship fields
    '''
    ret_data = {}
    ret_data['id'] = goods['num_id']
    ret_data['title'] = goods['title']
    ret_data['tmall'] = goods['is_tmall']
    ret_data['coupon_start'] = goods['start']
    ret_data['coupon_end'] = goods['end']
    ret_data['small_images'] = goods['small_images']
    ret_data['images'] = goods['small_images']
    ret_data['sales'] = int(goods['sales'])
    ret_data['price'] = float(goods['price'])
    ret_data['price'] = round(ret_data['price'], 2)
    ret_data['coupon_amount'] = float(goods['coupon_amount'])
    ret_data['coupon_amount'] = round(ret_data['coupon_amount'], 2)
    ret_data['coupon_price'] = round(float(goods['price']) - float(goods['coupon_amount']), 2)
    ret_data['pic_url'] = goods['pic_url']
    if goods.get("mid"):
        ret_data['mid'] = goods['mid']
    return ret_data


def _ship_miniapp_detail(goods):
    ret_data = {}
    ret_data['id'] = goods['num_id']
    ret_data['title'] = goods['title']
    ret_data['tmall'] = goods['is_tmall']
    ret_data['small_images'] = goods['small_images']
    ret_data['images'] = goods['small_images']
    ret_data['sales'] = int(goods['sales'])
    ret_data['price'] = float(goods['price'])
    ret_data['price'] = round(ret_data['price'], 2)
    ret_data['coupon_amount'] = float(goods['coupon_amount'])
    ret_data['coupon_amount'] = round(ret_data['coupon_amount'], 2)
    ret_data['coupon_price'] = float(goods['price']) - \
        float(goods['coupon_amount'])
    ret_data['coupon_price'] = round(ret_data['coupon_price'], 2)
    ret_data['pic_url'] = goods.get("pic_url", "")
    ret_data['shop_info'] = {}
    return ret_data


@exception_handler_method
def miniapp_goods_detail(gid, mid):
    res = {'errcode': -1}
    gid = int(gid)
    goods = get_goods_info_by_id(gid)
    if goods:
        data = _ship_miniapp_detail(goods)
        res.update({'errcode': 0, 'data': data})
        return res
    goods_obj = TbkGoods(num_id=gid)
    if mid and mid.isdigit():
        table = get_table_by_mid(mid)
        if table:
            goods_obj.__table__ = table
    goods = goods_obj.find_goods_by_id()
    if not goods:
        res.update({'errmsg': u"找不到商品"})
        return res
    data = _ship_miniapp_detail(goods)
    res.update({'errcode': 0, 'data': data})
    return res


@exception_handler_method
def get_goods_list(params):
    res = {'errcode': -1}
    tid = params.get("mid")
    if not tid:
        res.update({"errmsg": "参数错误"})
        return res
    tid = int(tid)
    handler_class = MID_MAP.get(tid)
    if handler_class is None:
        handler_class = MID_MAP[90]
    handle_res = handler_class().get_data(params)
    if handle_res['errcode'] != 0:
        return handle_res
    data = handle_res['data']
    data = map(_ship_miniapp, data)
    res.update({'errcode': 0, 'data': data})
    return res


@exception_handler_method
def local_search(params):
    keyword = params.get("keyword")
    page = int(params.get("page", 1))
    count = int(params.get("count", 20))
    sort = int(params.get('tid', 1))
    if isinstance(keyword, unicode):
        keyword = keyword.encode("utf-8")
    share_text_info = find_goods_info(keyword)
    if share_text_info:
        num_id = share_text_info['num_id']
        save_goods_info(num_id, share_text_info)
        tmp = _ship_miniapp(share_text_info)
        return {'errcode': 0, 'data': [tmp]}
    data = []
    sort_dict = {}
    if sort == 8:
        sort_dict.update({'coupon_amount': -1})
    elif sort == 6:
        sort_dict.update({'sales': -1})
    elif sort == 7:
        sort_dict.update({'coupon_fee': 1})
    elif sort == 9:
        super_params = {
                'keyword': keyword,
                'page': page,
                'count': count,
                'yq': 0,
                'tid': 0}
        return super_search_miniapp(super_params)
    data = searcher.search(keyword, sort_dict, page=page, count=count)
    # ids = map(lambda x: int(x['id']), data)
    # LOG.info("data: %s", data)
    LOG.info('keyword: %s, ret: %s', keyword, len(data))
    table_dict = {}
    ordered_id = []
    for item in data:
        table = item.get("table", 'goods')
        table_dict.setdefault(table, [])
        table_dict[table].append(int(item['id']))
        ordered_id.append(int(item['id']))
    goods_obj = TbkGoods()
    data_dict = {}
    for table, ids in table_dict.items():
        goods_obj.__table__ = table
        cond = {'num_id': {'$in': ids}}
        goods_list = goods_obj.find_goods_by_cond(cond, 1, count=100)
        for goods in goods_list:
            if goods.get('num_id') is None:
                LOG.info(goods['_id'])
                continue
            tmp = _ship_miniapp(goods)
            data_dict[goods['num_id']] = tmp
    result = []
    for _id in ordered_id:
        tmp = data_dict.get(_id)
        if not tmp:
            continue
        result.append(tmp)
    return {'errcode': 0, 'data': result}


@exception_handler_method
def super_search_miniapp(params):
    res = {'errcode': -1}
    keyword = params.get("keyword")
    if keyword is None:
        res.update({'errmsg': u"搜索关键字不能为空"})
        return res
    page = params.get("page", 1)
    count = params.get("count", 50)
    is_tmall = params.get("is_tmall")
    tid = params.get("tid")
    yq = params.get("yq")
    if isinstance(page, (unicode, str)) and not page.isdigit() or\
            (isinstance(count, (unicode, str)) and not count.isdigit()):
        res.update({'errmsg': u"page非法"})
        return res
    yq = int(yq)
    tid = int(tid)
    sp = SearchParams()
    sp.keyword = keyword
    sp.page = int(page)
    sp.count = int(count)
    sp.is_tmall = 'true' if is_tmall else 'false'
    sp.has_coupon = 'true' if yq else 'false'
    if tid == 5:
        sp.sort = 'tk_total_sales_des'
    elif tid == 6:
        sp.sort = 'total_sales_des'
    result = []
    try:
        # result = tbk_client.super_search(sp)
        result = _super_search(sp, tbk_client)
        result = result['tbk_dg_material_optional_response'][
                'result_list']['map_data']
    except Exception as ex:
        LOG.error("super search ex: %s, word: %s", ex, keyword)
        res.update({'errmsg': u"数据异常： %s" % ex})
        return res
    goods_data = []
    for goods in result:
        tmp = _ship_goods_supers(goods)
        if not tmp:
            continue
        num_id = tmp['num_id']
        save_goods_info(num_id, tmp)
        tmp = _ship_miniapp(tmp)
        goods_data.append(tmp)
    res.update({'errcode': 0, 'data': goods_data})
    return res


def miniapp_login(params):
    """
    {'session_id': session_id, "invited_code": inv_code}}
    """
    res = {'errcode': 0}
    code = params['code']
    config_data = params['user_config']
    appid = config_data['appid']
    appsec = config_data['appsec']
    client = WechatClient(appid, appsec, session=data_cache)
    session_data = client.weapp.fetch_user_session(code)
    session_id = cache_session(session_data)
    data = {'session_id': session_id, 'invited_code': ''}
    res.update({'data': data})
    return res


@exception_handler_method
def share_text_goods(share_message):
    pass
