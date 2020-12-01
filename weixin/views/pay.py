# coding=utf-8
'''
pay relevent module;
'''

import uuid
import os
import qrcode
import time
from wechat.pay import WechatPay
from wechat.utils import xml_to_dict, pay_sign
from weixin.utils.constants import PayType, OrderStatus
from weixin.models.order_model import Order, OrderDetail
from weixin.models.goods_model import Goods
from weixin.views.order_op import place_order_by_gid
from weixin.views.grid_user import pay_for_credit
from weixin.cache.session import check_session
from weixin.settings import MCHID, CERT_PATH, KEY_PATH,\
        PAY_KEY, LOGGER as LOG, XCX_APPID_PAYED

NOTIFY_URL = 'http://service.shiguofu.cn/service/pay/api/wxpay/callback'
pay_client = WechatPay(XCX_APPID_PAYED, PAY_KEY, MCHID, CERT_PATH, KEY_PATH)


def check_order(session_id, order_id):
    session_data = check_session(session_id)
    res = {'errcode': -1}
    if not session_data:
        res.update({'errcode': 10000, 'errmsg': 'invalidate session'})
        return res
    order_instance = Order(out_trade_no=order_id)
    order_data = order_instance.find_one_order()
    if not order_data:
        res.update({'errmsg': u"数据错误，请重试"})
        return res
    status = order_data.get("status")
    if status != OrderStatus.OK.value:
        added_credit = 0
    else:
        added_credit = 0
        detail_instance = OrderDetail(out_trade_no=order_id)
        details = detail_instance.get_detail()
        for detail in details:
            goods_id = detail['goods_id']
            count = detail['count']
            g_instance = Goods(id=goods_id)
            goods_data = g_instance.find_by_id()
            if not goods_data:
                continue
            added_credit += (goods_data['count'] * count)
    res.update({
        'errcode': 0,
        'data': {'status': status, 'added_credit': added_credit}})
    return res


def wxpay_ok(data):
    res = xml_to_dict(data)
    LOG.info("wxpay pushed data:%s", res)
    out_trade_no = res['out_trade_no']
    sign = res.pop('sign', '')
    real_sign = pay_sign(res, PAY_KEY)
    update_data = {}
    if real_sign != sign:
        LOG.error(
                "id: %s, got unexcepted sign: %s, real: %s",
                out_trade_no, sign, real_sign)
        update_data.update({'status': OrderStatus.SIGNERROR.value})
        return
    ret_code = res['return_code']
    ret_msg = res.get('return_msg')
    if ret_code != 'SUCCESS':
        update_data.update({'status': OrderStatus.WXERROR.value})
        LOG.error("id: %s, msg: %s", out_trade_no, ret_msg)
        return
    if not _check_order(out_trade_no):
        update_data.update({'status': OrderStatus.ORDERERROR.value})
        LOG.error("id: %s, query error", out_trade_no)
        return
    transaction_id = res['transaction_id']
    update_data.update({
        "transaction_id": transaction_id,
        'update_time': int(time.time() * 1000),
        "status": OrderStatus.OK.value})
    order_instance = Order(out_trade_no=out_trade_no)
    order_instance.update(update_data)
    openid = res['openid']
    do_add_credit(openid, out_trade_no)


def do_add_credit(openid, out_trade_no):
    detail_instance = OrderDetail(out_trade_no=out_trade_no)
    details = detail_instance.get_detail()
    for detail in details:
        goods_id = detail['goods_id']
        count = detail['count']
        pay_for_credit(openid, goods_id, count)


def _check_order(out_trade_no):
    order_data = {}
    try:
        order_data = pay_client.order.query(out_trade_no)
    except Exception as ex:
        LOG.error("query order: %s, ex: %s", out_trade_no, ex)
    if order_data.get("trade_state") == 'SUCCESS':
        return True
    return False


def pay_goods_id(gid, count, session, pay_type):
    '''
    pay by the count and the id the goods;
    input:
    gid       ---   the id of the goods;
    count     ---   the count of the goods;
    session   ---   the login session of the user;
    pay_type  ---   payment type;
    '''
    user_session = check_session(session)
    if not user_session:
        return 10000, u'login expire'
    LOG.info(user_session)
    user_openid = user_session['openid']
    order_obj, data = place_order_by_gid(gid, count, user_openid, pay_type)
    if not order_obj:
        return -1, data
    total_fee = order_obj.total_fee
    out_trade_no = order_obj.out_trade_no
    desc = order_obj.body
    place_order_ret, ret_msg = unified_order(
            total_fee, pay_type, out_trade_no, user_openid, desc)
    if not place_order_ret:
        return -1, u'place order to wx error: %s' % ret_msg
    return 0, ret_msg


def pay_order(out_trade_no, session, pay_type):
    '''
    pay for an order that placed before;
    input:
    out_trade_no    ---  the id of the order;
    pay_type        ---  payment type;
    output:
    '''
    return 0, out_trade_no


def unified_order(fee, pay_type, out_trade_no, openid, desc=''):
    """unified order to wechat server"""
    req_data = {}
    req_data['body'] = desc
    req_data['out_trade_no'] = out_trade_no
    req_data['total_fee'] = str(fee)
    req_data['trade_type'] = pay_type
    req_data['notify_url'] = NOTIFY_URL
    req_data['spbill_create_ip'] = '127.0.0.1'
    if pay_type == PayType.miniapp.value:
        req_data['openid'] = openid
    elif pay_type == PayType.wx_qrcode.value:
        req_data['product_id'] = openid
    else:
        return False, u"不支持支付方式: %s" % pay_type
    ret_data = pay_client.order.create(data=req_data)
    if pay_type == PayType.miniapp.value:
        ret_msg = pay_client.order.get_jsapi_data(ret_data)
    elif pay_type == PayType.wx_qrcode.value:
        code_url = ret_data.get("code_url")
        ret_msg = {"qrcode_url": make_qr(code_url)}
    ret_msg.update({'order_id': out_trade_no})
    return True, ret_msg


def refund(out_trade_no, fee):
    req_data = {}
    req_data['out_trade_no'] = out_trade_no
    req_data['total_fee'] = str(fee)
    req_data['refund_fee'] = str(fee)
    req_data['out_refund_no'] = uuid.uuid4().hex
    res = pay_client.refund.refund(**req_data)
    return res


def make_qr(qrcode_weixin):
    '''
    generate pa qrcode by qrcod message;
    '''
    path = '/opt/webfront/qrcode'
    img = qrcode.make(qrcode_weixin)
    name = uuid.uuid4().hex + '.png'
    abpath = os.path.join(path, name)
    img.save(abpath)
    domain = 'http://www.shiguofu.cn/qrcode/' + name
    return domain
