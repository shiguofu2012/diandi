# coding=utf-8
'''weapp API'''

from flask import request
from weixin import app
from weixin.views.xcx_data import login_by_session, login_by_code, \
    decrypted_share_info, upload_pic, save_formid
from weixin.views.image_view import recommend_one_poetry, user_share_morning
from weixin.views.poetry import user_share_image
from weixin.utils.decorator import exception_handler, json_response, \
    validate_params


@app.route('/service/api/xcx/v1/user/login', methods=['POST'])
@exception_handler
@validate_params()
@json_response
def xcx_user_login(*args, **kwargs):
    '''
    user login to get session_key to decrypt userdata
    拆分登录与获取用户信息， 增加key参数，通用用户登录/用户信息获取
    TODO: 拆分，增加参数key，通用小程序登录与获取用户信息
    '''
    code = kwargs.get("code")
    encrypted_data = kwargs.get("encrypte")
    padding = kwargs.get("iv")
    session = kwargs.get("session")
    if not session and not code:
        return {"errcode": -1, "errmsg": u"缺少必要参数"}
    if code:
        data = login_by_code(code, encrypted_data, padding)
    elif session:
        data = login_by_session(session, encrypted_data, padding)
    return data


@app.route('/service/api/xcx/v1/group/share', methods=['POST'])
@exception_handler
@validate_params({'encrypte': '', 'iv': ''})
@json_response
def share_info(*args, **kwargs):
    '''
    get weapp share infomation, openGId,
    用户点击分享的小程序，可获取openGid
    TODO: 增加key，通过获取
    '''
    session = kwargs['session']
    encrypted_data = kwargs["encrypte"]
    padding = kwargs["iv"]
    page = kwargs.get("page")
    share = kwargs.get('share', 0)
    share = int(share)
    return decrypted_share_info(
        session, encrypted_data, padding, page, share)


@app.route('/service/api/v1/user/formid/upload', methods=['POST'])
@exception_handler
@validate_params({'form_id': ''})
@json_response
def upload_formid_api(session, form_id):
    '''
    formid 上传
    TODO： 增加key，通用上传formid
    '''
    save_formid(session, form_id)
    return {'errcode': 0}


@app.route('/service/api/v1/user/pic/upload', methods=['POST'])
@exception_handler
@validate_params()
@json_response
def upload_pic_api(*args, **kwargs):
    '''
    小程序用户主动上传图片
    '''
    session = kwargs['session']
    return upload_pic(session, request.files)


@app.route('/service/api/v1/image/share/poetry', methods=['GET'])
@exception_handler
@validate_params()
@json_response
def random_poetry_api(*args, **kwargs):
    '''
    小程序端生成图片，数据
    '''
    session = kwargs.get("session")
    if not session:
        return {'errcode': -1, 'errmsg': u"session不能为空"}
    openid = session['openid']
    return recommend_one_poetry(openid)


@app.route('/service/api/v1/image/share/poetry', methods=['POST'])
@exception_handler
@validate_params({'title': '', 'content': '', 'banner': ''})
@json_response
def share_poetry_api(*args, **kwargs):
    '''
    生成分享图片
    '''
    session = kwargs.get("session")
    if not session:
        return {'errcode': -1, 'errmsg': u"session 不能为空"}
    return user_share_image(session, kwargs)


@app.route('/service/api/v1/image/share/morning', methods=['POST'])
@exception_handler
@validate_params({'content': '', 'banner': ''})
@json_response
def share_morning_api(*args, **kwargs):
    '''
    生成早安分享图片
    '''
    session = kwargs.get("session")
    if not session:
        return {'errcode': -1, 'errmsg': u"session 不能为空"}
    if not kwargs['banner'].startswith(('http', 'https')):
        return {'errcode': -1, 'errmsg': u"请先上传图片"}
    return user_share_morning(session, kwargs['banner'], kwargs['content'])
