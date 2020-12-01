# coding=utf-8

'''
matche the goods tpw from taobao share message;
'''

import logging
import re
from weixin.utils.tbk_api import decrypt_tpw, get_goods_info
from weixin.utils.decorator import exception_handler_method
from weixin.utils.tbk_client import TbkApi, TBK_CRAWLER_CLIENT
from weixin.views.tbk_views import search_coupon_by_id

TPW_PATTERN = u"(复|復zんíゞ|椱ァ|復ず■淛)(\||\·)*(制|製)*这(条信息|段描述|句话)"\
    u"(?P<tpw>.*)后(到|咑|打开)"
_LOGGER = logging.getLogger("weixin")


@exception_handler_method
def find_goods_info(message, config_data=None):
    '''
    match the goods info from the message;
    '''
    if isinstance(message, unicode):
        message = message.encode('utf-8')
    goods_info = {}
    pattern = re.compile(TPW_PATTERN.encode('utf-8'))
    match = pattern.search(message)
    _LOGGER.info("msg: %s, match: %s", message, match)
    if match:
        tpw = match.group('tpw')
        _LOGGER.info("msg: %s, tpw: %s", message, tpw)
        goods_info = decrypt_tpw(tpw)
        num_iid = goods_info.get('id', '')
        if num_iid:
            if config_data is None:
                tbk_instance = TBK_CRAWLER_CLIENT
            else:
                tbk_instance = TbkApi(
                    appid=config_data['api_key'],
                    appsec=config_data['api_sec'], pid=config_data['pid'])
            search_data = search_coupon_by_id(num_iid, tbk_instance, True)
            _LOGGER.info("message: %s, goods_info: %s", message, search_data)
            if search_data['errcode'] == 0:
                goods_info = search_data['data']
                tpw_res = tbk_instance.convert_tpw(
                    goods_info['coupon_share_url'],
                    goods_info['title'],
                    goods_info['pic_url'])
                tbk_tpw_info = tpw_res.get('tbk_tpwd_create_response')
                if tbk_tpw_info:
                    data = tbk_tpw_info.get('data', {})
                    goods_info['tpw'] = data.get('model', '')
        else:
            goods_info.update({'errmsg': u"查找商品失败,待我修炼升级:)"})
    return goods_info


def get_goods_detail(num_iid):
    goods_info = get_goods_info(num_iid)
    _LOGGER.info("id: %s, detail: %s", num_iid, goods_info)
    if goods_info:
        pass
        # get_ret, msg = get_coupon_info(num_iid)
        # if get_ret:
        #     price = goods_info['price']
        #     coupon_amount = msg.get('couponAmount', 0)
        #     coupon_start = msg.get('couponStartFee', 0)
        #     title = goods_info['title']
        #     if price < coupon_start:
        #         coupon_amount = 0
        #     coupon_url = msg.get('coupon_url', '')
        #     tpw = generate_tpw(coupon_url.encode('utf-8'), title, goods_info['pic_url'].encode('utf-8'))
        #     goods_info.update({'tpw': tpw, "coupon_amount": coupon_amount, 'profit_rate': msg.get("commission_rate", 0)})
        # else:
        #     goods_info.update({'errmsg': msg})
    else:
        goods_info.update({'errmsg': u"商品查找失败:("})
    return goods_info
