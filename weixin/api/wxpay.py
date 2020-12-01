# coding=utf-8
'''
pay relevent API;
'''

from flask import request, jsonify

from weixin import app
from weixin.views.pay import pay_order, pay_goods_id, wxpay_ok, check_order
from weixin.utils.constants import PayType
from weixin.utils.decorator import exception_handler
from weixin.settings import LOGGER


@app.route("/service/api/pay/v1/order/status", methods=['GET'])
@exception_handler
def order_status_api():
    params = request.args
    session_id = params.get("session_id")
    order_id = params.get("order_id")
    if session_id is None or order_id is None:
        return jsonify({'sta': -1, 'msg': u"缺少必要参数"})
    res = check_order(session_id, order_id)
    if res['errcode'] == 0:
        return jsonify({'sta': 0, 'msg': 'ok', 'data': res['data']})
    return jsonify({'sta': res['errcode'], 'msg': res.get("errmsg", '')})


@app.route("/service/pay/api/wxpay/callback", methods=['POST'])
@exception_handler
def wxpay_callback():
    '''
    wx pay callback;
    '''
    params = request.data
    wxpay_ok(params)
    return "success"


@app.route("/service/api/v1/wxpay/pay")
@exception_handler
def wxpay():
    '''
    pay func;
    input
    '''
    params = request.args
    session_key = params.get("session_id")
    pay_type = params.get('pay_type', PayType.miniapp.value)
    gid = params.get("id")
    count = params.get("count", 1)
    out_trade_no = params.get("order_id")

    succeed = False
    msg = {}
    if out_trade_no:
        succeed, msg = pay_order(out_trade_no, session_key, pay_type)
    elif gid and count:
        succeed, msg = pay_goods_id(gid, count, session_key, pay_type)
    else:
        msg['errmsg'] = u'缺少必要参数'
    data = {'sta': succeed}
    if succeed == 0:
        data.update({'msg': 'OK', 'data': msg})
    else:
        data.update({'msg': msg})
    return jsonify(data)
