#!/usr/bin/python
# coding=utf-8

import top.api
from weixin.settings import LOGGER as LOG, TBK_APPKEY, TBK_APPSEC, TBK_PID, \
    TBK_CRAWLER_APKEY, TBK_CRAWLER_APPSEC, TBK_CRAWLER_PID


class SearchParams(dict):

    default_params_key = {
        "keyword": '',  # keyword
        "page": 1,
        "count": 10,
        "platform": 2,  # 2 -- wireless  1 -- pc
        "is_overseas": 'false',  # is oversea goods
        "is_tmall": 'false',     # is tmall goods
        # "sort": 'total_sales_des',  # sort
        "sort": '',
        "has_coupon": 'true',    # has coupon or not
        "need_free_shipment": 'false',  # 是否包邮
        "cat": '50006843'
    }

    def __getattr__(self, key):
        if key not in self:
            if key in self.default_params_key:
                return self.default_params_key[key]
            return None
        else:
            return self[key]

    def __setattr__(self, key, value):
        self.default_params_key[key] = value

    def __repr__(self):
        return self.default_params_key


class TbkApi(object):

    def __init__(self, appid, appsec, pid):
        self.appid = appid
        self.appsec = appsec
        self.pid = pid
        pid_list = pid.split('_')
        self.adzone_id = pid_list[-1]
        self.site_id = pid_list[-2]

    def super_search(self, search_params):
        top.setDefaultAppInfo(self.appid, self.appsec)
        keyword = search_params.keyword
        client_req = top.api.TbkDgMaterialOptionalRequest()
        if keyword:
            if isinstance(keyword, unicode):
                keyword = keyword.encode("utf-8")
            client_req.q = keyword
        if not keyword:
            client_req.cat = search_params.cat
        client_req.page_no = search_params.page
        client_req.page_size = search_params.count
        client_req.platform = search_params.platform
        client_req.is_overseas = search_params.is_overseas
        client_req.is_tmall = search_params.is_tmall
        if search_params.sort:
            client_req.sort = search_params.sort
        client_req.has_coupon = search_params.has_coupon
        client_req.need_free_shipment = search_params.need_free_shipment
        client_req.adzone_id = self.adzone_id
        client_req.site_id = self.site_id
        res = {'errcode': -1}
        try:
            res = client_req.getResponse()
            res['errcode'] = 0
        except Exception as ex:
            LOG.error(
                "super search keyword: %s, ex: %s",
                keyword, ex,
                exc_info=True)
        return res

    def search_juhuasuan(self, keyword, page=1, count=20, is_post='false'):
        if isinstance(keyword, unicode):
            keyword = keyword.encode("utf-8")
        top.setDefaultAppInfo(self.appid, self.appsec)
        client_req = top.api.JuItemsSearchRequest()
        params_query = {}
        params_query['current_page'] = page
        params_query['page_size'] = count
        params_query['pid'] = self.pid
        params_query['postage'] = is_post
        params_query['word'] = keyword
        client_req.param_top_item_query = params_query
        res = None
        try:
            res = client_req.getResponse()
        except Exception as ex:
            LOG.error("ju search ex: %s", ex)
        return res

    def convert_tpw(self, coupon_url, text, logo_pic_url):
        if isinstance(text, unicode):
            text = text.encode("utf-8")
        if isinstance(coupon_url, unicode):
            coupon_url = coupon_url.encode("utf-8")
        if isinstance(logo_pic_url, unicode):
            logo_pic_url = logo_pic_url.encode("utf-8")
        top.setDefaultAppInfo(self.appid, self.appsec)
        client_req = top.api.TbkTpwdCreateRequest()
        client_req.text = text
        client_req.url = coupon_url
        client_req.logo = logo_pic_url
        res = None
        try:
            res = client_req.getResponse()
        except Exception as ex:
            LOG.error("convert tpw ex: %s", ex)
        return res

    def decrypt_tpw(self, tpw):
        top.setDefaultAppInfo(self.appid, self.appsec)
        client = top.api.TbkTpwQueryGetRequest()
        client.password_content = tpw
        client.adzone_id = self.adzone_id
        res = None
        try:
            res = client.getResponse()
        except Exception as ex:
            LOG.error("tpw: %s ex: %s", tpw, ex, exc_info=True)
        return res

    def tbk_goods_info(self, num_id, platform=2):
        top.setDefaultAppInfo(self.appid, self.appsec)
        if isinstance(num_id, list):
            num_id = ','.join(num_id)
        client_req = top.api.TbkItemInfoGetRequest()
        client_req.num_iids = str(num_id)
        client_req.platform = platform
        res = None
        try:
            res = client_req.getResponse()
        except Exception as ex:
            LOG.error("num_id: %s, ex: %s", num_id, ex)
        return res

    def tbk_goods_recommend(self, num_iid):
        top.setDefaultAppInfo(self.appid, self.appsec)
        client_req = top.api.TbkItemRecommendGetRequest()
        client_req.num_iid = str(num_iid)
        client_req.fields = 'num_iid,title,pict_url,small_images,'\
            'reserve_price,zk_final_price,user_type,item_url'
        client_req.count = 20
        res = None
        try:
            res = client_req.getResponse()
        except Exception as ex:
            LOG.error("num_id: %s, ex: %s", num_iid, ex)
        return res

    def dg_coupon_list(self, keyword, page, count):
        top.setDefaultAppInfo(self.appid, self.appsec)
        client_req = top.api.TbkDgItemCouponGetRequest()
        client_req.adzone_id = self.adzone_id
        client_req.platform = 2
        client_req.page_size = count
        client_req.page_no = page
        if isinstance(keyword, unicode):
            keyword = keyword.encode("utf-8")
        client_req.q = keyword
        res = None
        try:
            res = client_req.getResponse()
        except Exception as ex:
            LOG.error("keyword: %s, coupon list ex: %s", keyword, ex)
        return res


TBK_CLIENT = TbkApi(
    appid=TBK_APPKEY,
    appsec=TBK_APPSEC,
    pid=TBK_PID)
TBK_CRAWLER_CLIENT = TbkApi(
    appid=TBK_CRAWLER_APKEY,
    appsec=TBK_CRAWLER_APPSEC,
    pid=TBK_CRAWLER_PID)
