# coding=utf-8


from flask import jsonify
from weixin import app
from weixin.utils.decorator import exception_handler
from weixin.views.userdata import get_login_code, user_profile, login_status


@app.route('/service/api/v1/login/qrcode', methods=['GET'])
@exception_handler
def login_qrcode_api():
    res = get_login_code()
    if res['errcode'] != 0:
        return jsonify({'sta': -1, 'msg': res.get("errmsg", '')})
    return jsonify({"sta": 0, 'msg': 'ok', 'data': res['data']})


@app.route('/service/api/v1/user/status/<uid>', methods=['GET'])
@exception_handler
def get_user_status_api(uid):
    res = login_status(uid)
    if res['errcode'] != 0:
        return jsonify({'sta': -1, 'msg': res.get("errmsg", '')})
    return jsonify({'sta': 0, 'msg': 'ok', 'data': res['data']})


@app.route('/service/api/v1/user/profile/<token>', methods=['GET'])
@exception_handler
def get_userdata_api(token):
    res = user_profile(token)
    if res['errcode'] != 0:
        return jsonify({'sta': -1, 'msg': res.get("errmsg")})
    return jsonify({'sta': 0, 'msg': 'ok', 'data': res['data']})
