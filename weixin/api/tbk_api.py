#!usr/bin/python
# coding=utf-8
'''
小程序版本的淘宝客API
'''

from weixin import app
from weixin.utils.decorator import exception_handler, json_response, \
    validate_params
from weixin.views.tbk_views import goods_detail, goods_tpw, similar_goods,\
    super_search, share_tbk_image, get_tbk_config, get_tbk_hot_words,\
    get_material, get_project
from weixin.views.mini_goods import get_goods_list, miniapp_goods_detail, \
    check_key_wrapper, get_key_status, miniapp_tpw, super_search_miniapp, \
    local_search, miniapp_login


@app.route('/service/api/v1/tbk/picture/generate', methods=['GET'])
@exception_handler
@validate_params({'key': None, 'session_id': 0})
@check_key_wrapper
@json_response
def share_image_gen_api(*args, **kwargs):
    '''
    生成分享图，为小程序做的，不需要登录状态
    二维码为小程序码
    appid/appsec 获取页面 二维码
    '''
    goods_id = kwargs.get("id")
    succ, url = share_tbk_image(goods_id, kwargs)
    data = {}
    if not succ:
        data = {'errcode': -1, 'msg': ''}
    else:
        data = {'errcode': 0, 'data': {'sta': 0, "pic_url": url}}
    return data


@app.route('/service/api/v1/tbk/shareinfo/get', methods=['GET'])
@exception_handler
@validate_params({'key': None, 'session_id': 0})
@check_key_wrapper
@json_response
def user_share_info(*args, **kwargs):
    '''
    兼容小程序的接口
    '''
    data = {'errcode': 0, 'data': {'sta': -1, 'msg': u"不是代理"}}
    return data


@app.route('/service/api/v1/tbk/login', methods=['POST'])
@exception_handler
@validate_params({'key': None})
@check_key_wrapper
@json_response
def user_login_api(*args, **kwargs):
    '''
    小程序的登录接口，返回session_id
    appid/appsec 通过code 获取openid,
    appid/appsec 通过key在表tbk_config 中获取,可以通用
    login 用户头像最好定时刷新
    '''
    return miniapp_login(kwargs)


@app.route('/service/api/v1/tbk/goods/list', methods=['GET'])
@exception_handler
@validate_params({'key': None})
@check_key_wrapper
@json_response
def list_goods_api(*args, **kwargs):
    '''
    for tbk miniapp,
    兼容网页版,不需要登录，只需要key
    新版网页可以使用
    '''
    return get_goods_list(kwargs)


@app.route('/service/api/v1/tbk/applet/info', methods=['GET'])
@exception_handler
@validate_params({'pro_id': None})
@json_response
def get_applet_info_api(*args, **kwargs):
    '''
    兼容小程序版本，获取壳子信息
    '''
    return get_project(kwargs['pro_id'])


@app.route('/service/api/v1/tbk/material/info', methods=['GET'])
@exception_handler
@validate_params({'mat_id': None})
@json_response
def get_material_info_api(*args, **kwargs):
    '''
    兼容小程序版本，获取壳子信息
    '''
    return get_material(kwargs['mat_id'])


@app.route('/service/api/v1/tbk/hotwords/list', methods=['GET'])
@exception_handler
@validate_params({'key': None})
@check_key_wrapper
@json_response
def hot_words_api(*args, **kwargs):
    '''
    for tbk miniapp hot words
    获取关键字列表，不需要登录状态，
    兼容网页版
    '''
    data = get_tbk_hot_words()
    return {'errcode': 0, 'data': data}


@app.route('/service/api/v1/tbk/miniapp/search/super', methods=['GET'])
@exception_handler
@validate_params({'key': None})
@check_key_wrapper
@json_response
def super_serach_miniapp_api(*args, **kwargs):
    '''
    超级搜索， 不需要登录状态
    新版用户可使用
    '''
    return super_search_miniapp(kwargs)


@app.route('/service/api/v1/tbk/miniapp/search/local', methods=['GET'])
@exception_handler
@validate_params({'key': None})
@check_key_wrapper
@json_response
def local_serach_miniapp_api(*args, **kwargs):
    '''
    本地搜索，不需要登录状态，
    新版网页可用
    '''
    return local_search(kwargs)


@app.route('/service/api/v1/tbk/goods/config', methods=['GET'])
@exception_handler
@validate_params({'key': None})
@check_key_wrapper
@json_response
def goods_config(*args, **kwargs):
    '''
    for tbk miniapp menu&banner config
    获取配置信息，不需要登录状态，
    新版网页兼容可以使用
    '''
    data = get_tbk_config(kwargs['user_config'])
    return {'errcode': 0, 'data': data}


@app.route('/service/api/v1/tbk/goods/miniapp/detail', methods=['GET'])
@exception_handler
@validate_params({'key': None, 'id': int, 'session_id': 0})
@check_key_wrapper
@json_response
def goods_detail_miniapp_api(*args, **kwargs):
    '''
    tbk miniapp detail
    商品详细信息，不需要登录状态，
    新版网页版本可用
    '''
    gid = kwargs['id']
    mid = kwargs.get("mid")
    return miniapp_goods_detail(gid, mid)


@app.route('/service/api/v1/tbk/switch/get', methods=['GET'])
@exception_handler
@validate_params({'key': None})
@check_key_wrapper
@json_response
def get_tbk_switch_api(*args, **kwargs):
    '''
    for tbk miniapp switch
    小程序获取开关状态
    '''
    # data = {'proxy_status': 0, 'status': 1}
    data = get_key_status(kwargs['user_config'])
    return {'errcode': 0, 'data': data}


@app.route('/service/api/v1/tbk/goods/miniapp/tpw/get', methods=['GET'])
@exception_handler
@validate_params({'key': None, 'id': int, 'session_id': 0})
@check_key_wrapper
@json_response
def get_miniapp_tpw_api(*args, **kwargs):
    return miniapp_tpw(kwargs)


@app.route('/service/api/v1/tbk/goods/tpw/get', methods=['GET'])
@exception_handler
@validate_params({'id': int, 'session_id': 0})
@json_response
def goods_tpw_api(*args, **kwargs):
    '''
    get tpw api, give id, if not exists then search and get the tpw
    第一版本简单的淘客详情页面, 没有key固定的数据,获取
    '''
    return goods_tpw(kwargs['id'])


@app.route('/service/api/v1/tbk/goods/similar/get', methods=['GET'])
@validate_params({'id': int, 'session_id': 0})
@exception_handler
@json_response
def goods_similar_api(*args, **kwargs):
    '''
    similiar goods recommend for webpage;
    maybe add it for miniapp
    第一版本简单的淘客详情页面, 没有key固定的数据,获取
    目前可用,新版网页可以使用，带了参数key
    '''
    succ, data = similar_goods(kwargs['id'])
    if succ:
        return {'errcode': 0, 'data': data}
    return {'errcode': -1, 'errmsg': data}


@app.route('/service/api/v1/tbk/goods/search/super', methods=['GET'])
@exception_handler
@validate_params({'keyword': 1})
@json_response
def super_search_api(*args, **kwargs):
    '''
    web page super search,
    第一版本简单淘客网页的搜索
    '''
    search_ret, data = super_search(kwargs)
    if search_ret:
        return {'errcode': 0, 'data': data}
    return {'errcode': -1, 'errmsg': data}


@app.route('/service/api/v1/tbk/goods/detail', methods=['GET'])
@exception_handler
@validate_params({'id': int, 'session_id': 0})
@json_response
def goods_detail_api(*args, **kwargs):
    '''
    web page detail,
    第一版本简单的详情
    '''
    succ, detail = goods_detail(kwargs['id'])
    if succ:
        return {'errcode': 0, 'data': detail}
    return {'errcode': -1, 'errmsg': detail}