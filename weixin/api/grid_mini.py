# coding=utf-8


import json
from flask import request, jsonify
from weixin import app
from weixin.cache.session import check_session
from weixin.utils.decorator import exception_handler
from weixin.views.grid_user import login_by_code, login_by_session, \
        share_group_info, get_goods_list, share_friend_info, \
        jump_to_diandi_free, save_formid_grid
from weixin.views.grid_poetry import level_data, validate_answer, hint_poetry


@app.route('/service/grid/api/v1/init', methods=['POST'])
@exception_handler
def grid_login_api():
    '''
    user login to get session_key to decrypt userdata
    诗词九宫格，进入后获取用户当前的闯关信息
    TODO： 拆分用户信息的获取与登录
    '''
    params = request.get_json()
    appid = params.get("appid")
    code = params.get("code")
    encrypted_data = params.get("encrypte")
    padding = params.get("iv")
    session_id = params.get("session_id")
    if session_id is None and not code:
        return jsonify({"sta": -1, "msg": u"缺少必要参数"})
    data = {}
    if session_id:
        session_data = check_session(session_id)
        if not session_data:
            return jsonify({'sta': 10000, "msg": u"invalid session"})
        data = login_by_session(
                session_data, encrypted_data, padding)
    elif code:
        data = login_by_code(code, encrypted_data, padding, appid=appid)
    if 'errmsg' in data:
        return jsonify({'sta': -1, 'msg': data['errmsg']})
    return jsonify({"sta": 0, "msg": "ok", "data": data})


@app.route('/service/grid/api/v1/poetry/<int:level>', methods=['GET'])
@exception_handler
def get_level_data(level):
    params = request.args
    session_id = params.get("session_id")
    if session_id is None:
        return jsonify({'sta': -1, 'msg': u"缺少必要参数"})
    session_data = check_session(session_id)
    if not session_data:
        return jsonify({'sta': 10000, 'msg': u"invalid session"})
    is_helper = params.get("is_help")
    res = level_data(level, is_helper, session_data)
    if res['errcode'] == 0:
        return jsonify({'sta': 0, 'msg': 'ok', 'data': res['data']})
    return jsonify({'sta': -1, 'msg': res.get("errmsg", '')})


@app.route('/service/grid/api/v1/poetry/validate', methods=['POST'])
@exception_handler
def validate_answer_api():
    params = request.data
    try:
        params = json.loads(params)
    except Exception:
        return jsonify({'sta': -1, 'msg': "data error"})
    session_id = params.get("session_id")
    level = params.get("level")
    answer = params.get("answer")
    if not session_id or not level or not answer:
        return jsonify({'sta': -1, 'msg': u"缺少必要参数"})
    session_data = check_session(session_id)
    if not session_data:
        return jsonify({'sta': 10000, 'msg': u"invalid session"})
    try:
        level = int(level)
    except Exception:
        return jsonify({'sta': -1, 'msg': u"参数格式错误"})
    res = validate_answer(params, session_data)
    if res['errcode'] == 0:
        return jsonify({'sta': 0, 'msg': 'ok', 'data': res['data']})
    return jsonify({'sta': -1, 'msg': res.get("errmsg", '')})


@app.route('/service/grid/api/v1/poetry/hint', methods=['POST'])
@exception_handler
def hint_poetry_api():
    params = request.data
    try:
        params = json.loads(params)
    except Exception:
        return jsonify({'sta': -1, 'msg': "data error"})
    session_id = params.get("session_id")
    level = params.get("level")
    is_helper = params.get("is_help")
    if session_id is None or not level:
        return jsonify({'sta': -1, 'msg': u"缺少必要参数"})
    session_data = check_session(session_id)
    if not session_data:
        return jsonify({'sta': 10000, 'msg': u"invalid session"})
    try:
        level = int(level)
    except Exception:
        return jsonify({'sta': -1, 'msg': u"参数格式错误"})
    res = hint_poetry(session_data, level, is_helper)
    if res['errcode'] == 0:
        return jsonify({'sta': 0, 'msg': 'ok', 'data': res['data']})
    return jsonify({'sta': res['errcode'], 'msg': res.get("errmsg", '')})


@app.route('/service/gird/api/v1/group/share', methods=['POST'])
@exception_handler
def grid_share_api():
    '''get weapp share infomation, openGId'''
    params = request.get_json()
    session_id = params.get("session_id")
    encrypted_data = params.get("encrypte")
    padding = params.get("iv")
    page = params.get("page")
    share = params.get('share', '')
    if not session_id:
        return jsonify({'sta': -1, 'msg': u"缺少必要参数"})
    session_data = check_session(session_id)
    if not session_data:
        return jsonify({'sta': 10000, 'msg': 'invalid session'})
    if encrypted_data and padding:
        data = share_group_info(
                session_data, encrypted_data, padding, page, share)
    else:
        data = share_friend_info(session_data, page, share)
    return jsonify({'sta': 0, 'msg': 'ok', 'data': data})


@app.route('/service/gird/api/v1/goods/get', methods=['GET'])
@exception_handler
def goods_list_api():
    params = request.args
    session_id = params.get("session_id")
    session_data = check_session(session_id)
    if not session_data:
        return jsonify({'sta': 10000, 'msg': 'invalid session'})
    res = get_goods_list(session_data)
    if res['errcode'] == 0:
        return jsonify({'sta': 0, 'msg': 'ok', 'data': res['data']})
    return jsonify({'sta': res['errcode'], 'msg': res.get("errmsg", '')})


@app.route('/service/gird/api/v1/credit/free', methods=['POST'])
@exception_handler
def free_credit_api():
    params = request.data
    try:
        params = json.loads(params)
    except Exception:
        pass
    session_id = params.get("session_id")
    session_data = check_session(session_id)
    if not session_data:
        return jsonify({'sta': 10000, 'msg': 'invalid session'})
    res = jump_to_diandi_free(session_data)
    if 'errcode' in res and res['errcode'] != 0:
        return jsonify({"sta": -1, 'msg': res.get("errmsg", '')})
    return jsonify({'sta': 0, 'msg': 'ok', 'data': res.get("data", {})})


@app.route('/service/grid/api/v1/formid/upload', methods=['POST'])
@exception_handler
def upload_formid_api_grid():
    params = request.get_json()
    session_id = params.get("session_id")
    form_id = params.get("form_id")
    if not session_id or not form_id:
        return jsonify({'sta': 0, 'msg': "no data found"})
    session_data = check_session(session_id)
    if not session_data:
        return jsonify({'sta': 10000, 'msg': 'invalid session'})
    res = save_formid_grid(session_data, form_id)
    return jsonify({'sta': 0, 'msg': "OK", "data": res.get("data", {})})
