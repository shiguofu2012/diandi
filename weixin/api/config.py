#!/usr/bin/python
# coding=utf-8

from flask import request, jsonify, make_response
from weixin import app
from weixin.utils.decorator import exception_handler, json_response
from weixin.views.wechat_api import configJS, login, long2short


@app.route("/service/api/wechat/long2short")
@exception_handler
@json_response
def long2short_api():
    '''
    long url to short url;
    需要公众号appid认证过的，否则调用失败
    '''
    params = request.args
    url = params.get('long_url')
    if not url:
        return {'errcode': -1, 'errmsg': u'缺少参数'}
    ret, msg = long2short(url)
    ret_data = {'errcode': 0}
    if ret:
        ret_data['data'] = {'short_url': msg}
    else:
        ret_data['errcode'] = -1
        ret_data['errmsg'] = msg
    return ret_data


@app.route("/service/api/v1/user/login")
@exception_handler
@json_response
def user_login():
    '''
    user login by oauth API;
    认证的微信公众号，登录授权
    code   ---   wx redirect code;
    state  ---   own define params;
    '''
    params = request.args
    code = params.get("code")
    # state = params.get("state")
    session_key = login(code)
    if session_key:
        return {'errcode': 0, 'data': {'session_key': session_key}}
    return {'errcode': -1, 'errmsg': 'login failed'}


@app.route("/service/api/wechat/jssdk/sign")
@exception_handler
@json_response
def jsapi_sign():
    '''
    call jssdk sign;
    jssdk 调用签名，传给客户端使用
    '''
    params = request.args
    url = params.get('url', '')
    if not url:
        return {'errcode': -1, 'errmsg': u'缺少参数url'}
    data = configJS(url)
    return {'errcode': 0, 'data': data}


@app.errorhandler(404)
def not_found(error):
    return make_response(
        jsonify({"sta": -1, 'msg': 'Not found by 404 handler'}), 404)
