# coding=utf-8
'''
receive wechat push message;
'''

from flask import request, abort
from weixin import app
from wechat.utils import check_signature
from weixin.views.message_handler import process_push_v2, process_miniapp_push
from weixin.utils.decorator import exception_handler, str_response, \
    validate_params
from weixin.settings import LOGGER


@app.route("/service/api/wechat/mp/<appid>/push", methods=['GET', 'POST'])
def validate(appid):
    '''
    validate API;
    receive wechat server push event or message;
    '''
    params = request.args
    signature = params.get('signature')
    timestamp = params.get("timestamp")
    nonce = params.get("nonce")
    try:
        check_signature(
            'z7mlt2o4fjwopky7uxzn8qn8usl78e9y',
            signature,
            timestamp,
            nonce
        )
    except Exception:
        abort(403)
    if request.method == 'GET':
        echostr = params.get("echostr")
        return echostr

    encrypt_type = params.get("encrypt_type", 'raw')
    if encrypt_type == 'raw':
        params = request.data
        ret_msg = process_push_v2(params, appid)
        return ret_msg.render()
    if encrypt_type == 'aes':
        body = request.data
        print body
        return ""
    return "unknow"


@app.route("/service/api/wechat/miniapp/<appid>/push", methods=['GET', 'POST'])
@exception_handler
@validate_params()
@str_response
def miniapp_message_receive(*args, **kwargs):
    token = 'diandishici'
    encoding_key = 'ssI29ef6wBsN55tDUBQRXp5P8MEdzGKDCRAJPxhkVG6'
    method = request.method.lower()
    if method == 'get':
        try:
            check_signature(
                token,
                kwargs['signature'],
                kwargs['timestamp'],
                kwargs['nonce'])
        except Exception:
            abort(403)
        return kwargs.get("echostr")
    elif method == 'post':
        data = request.data
        ret = process_miniapp_push(data, kwargs, encoding_key, token)
        LOGGER.info("msg_sign: %s, ret: %s", kwargs['signature'], ret)
        if ret.get("data"):
            return ret.get("data")
    return 'success'
