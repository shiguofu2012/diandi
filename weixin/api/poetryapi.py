# coding=utf-8
# !/usr/bin/python
'''
点滴诗词的大部分接口，获取诗词列表/诗词/搜索等
'''
from flask import request
from weixin import app
from weixin.views.poetry import get_data, get_poetry_detail, get_author_data, \
    get_share_data, search_poetry, search_init_data, user_history, \
    user_operation, generate_share_pic, get_search_data, search_by_cat, \
    everyday_sentence, get_every_by_id, recommend_everyday
from weixin.views.do_config import get_ip_info, do_get_banner, do_get_tab
from weixin.utils.decorator import exception_handler, json_response, \
    validate_params


@app.route("/service/api/v1/config/get", methods=['GET'])
@exception_handler
@json_response
def get_config_data():
    '''
    ip地址信息/阴历日期/banner/tab菜单列表，集合到一个接口
    '''
    ip = request.remote_addr
    banners = do_get_banner()
    tabs = do_get_tab()
    ip_info = get_ip_info(ip)
    data = {'banners': banners, 'ip_info': ip_info, 'tab_list': tabs}
    return {'errcode': 0, 'data': data}


@app.route('/service/api/v1/ip/info', methods=['GET'])
@exception_handler
@json_response
def get_ipinfo_api():
    '''
    点滴诗词获取阴历日期，及ip对应的天气情况
    '''
    ip = request.remote_addr
    data = get_ip_info(ip)
    return {'errcode': 0, 'data': data}


@app.route("/service/api/v1/banner/get", methods=['GET'])
@exception_handler
@json_response
def get_banner_api():
    '''
    diandi shici banner;
    '''
    banners = do_get_banner()
    return {'errcode': 0, 'data': banners}


@app.route('/service/api/v1/poetry/poetry/get', methods=['GET'])
@exception_handler
@validate_params()
@json_response
def get_poetry_api(*args, **kwargs):
    '''
    获取诗词列表,进入小程序就获取列表，支持小程序

    Params:
        session_id  -- 小程序的登录session_id,通过login接口获取
        tab_id      -- 诗词的tab列表，0--推荐，1--诗词，2--名句，3--作者,4--古籍，5--每日一句
        page        -- 分页
        count       -- 分页
    '''
    session_data = kwargs['session']
    tab_id = kwargs.get('tab_id', 0)
    page = kwargs.get('page', 1)
    count = kwargs.get('count', 20)
    page = int(page)
    count = int(count)
    succ, poetry = get_data(session_data, tab_id, page, count)
    ret = {'errcode': 0}
    if not succ:
        ret['errcode'] = -1
        ret['errmsg'] = poetry
    else:
        ret['data'] = poetry
    return ret


@app.route('/service/api/v1/poetry/detail/get', methods=['GET'])
@exception_handler
@validate_params({'poetry_id': int, 'session_id': 1})
@json_response
def get_poetry_detail_api(*args, **kwargs):
    '''
    获取诗词详情
    '''
    from_uid = kwargs.get("from_uid")
    poetry_id = kwargs['poetry_id']
    session_data = kwargs['session']
    succ, data = get_poetry_detail(session_data, poetry_id, from_uid)
    ret_data = {'errcode': 0}
    if not succ:
        ret_data['errcode'] = -1
        ret_data['errmsg'] = data
    else:
        ret_data['data'] = data
    return ret_data


@app.route('/service/api/v1/poetry/author/get', methods=['GET'])
@exception_handler
@validate_params({'author_id': int, 'session_id': 1})
@json_response
def get_author_api(*args, **kwargs):
    '''
    获取作者列表
    '''
    author_id = kwargs['author_id']
    session_data = kwargs['session']
    page = int(kwargs.get('page', 1))
    count = int(kwargs.get('count', 20))
    data = get_author_data(session_data, author_id, page, count)
    return {'errcode': 0, 'data': data}


@app.route('/service/api/v1/poetry/share/get', methods=['GET'])
@exception_handler
@validate_params({'session_id': 1})
@json_response
def get_share_api(*args, **kwargs):
    '''
    分享诗词到群的历史记录
    '''
    session_data = kwargs['session']
    page = int(kwargs.get('page', 1))
    count = int(kwargs.get('count', 20))
    share_data = get_share_data(session_data, page, count)
    return {'errcode': 0, 'data': share_data}


@app.route('/service/api/v1/poetry/search', methods=['POST'])
@exception_handler
@validate_params({'session_id': 1})
@json_response
def search_poetry_api(*args, **kwargs):
    '''
    诗词关键字搜索接口
    '''
    session_data = kwargs['session']
    page = int(kwargs.get('page', 1))
    count = int(kwargs.get('count', 20))
    keyword = kwargs.get('keyword', '')
    search_init = kwargs.get('init', 0)
    if not keyword and not search_init:
        return {'errcode': -1, 'errmsg': u'缺少必要参数'}
    if search_init:
        poetry_data = search_init_data(session_data, page, count)
    else:
        poetry_data = search_poetry(session_data, keyword, page, count)
    return {'errcode': 0, 'data': poetry_data}


@app.route('/service/api/v1/user/history', methods=['GET'])
@exception_handler
@validate_params({'session_id': 1, 'type': int})
@json_response
def user_history_api(*args, **kwargs):
    '''
    用户历史数据，喜欢的数据
    '''
    session_data = kwargs['session']
    _type = kwargs['type']
    page = int(kwargs.get('page', 1))
    count = int(kwargs.get('count', 20))
    history_list = user_history(session_data, _type, page, count)
    return {'errcode': 0, 'data': history_list}


@app.route('/service/api/v1/user/poetry/operation', methods=['POST'])
@exception_handler
@validate_params({'poetry_id': int, 'operation': 1, 'session_id': 1})
@json_response
def user_poetry_operation_api(*args, **kwargs):
    '''
    用户喜欢或者不喜欢某个诗词
    '''
    session_data = kwargs['session']
    poetry_id = kwargs['poetry_id']
    _type = kwargs['operation']
    succ, msg = user_operation(session_data, poetry_id, _type)
    ret_data = {'errcode': 0}
    if succ:
        return ret_data
    ret_data['errcode'] = -1
    ret_data['errmsg'] = msg
    return ret_data


@app.route('/service/api/v1/user/poetry/share/generate', methods=['GET'])
@exception_handler
@validate_params({'poetry_id': int, 'session_id': 1})
@json_response
def user_share_pic_api(*args, **kwargs):
    '''
    生成诗词分享图
    bug: 头像需要定期更新
    '''
    session_data = kwargs['session']
    poetry_id = kwargs['poetry_id']
    banner_url = kwargs.get('banner_url')
    succ, share_pic_url = generate_share_pic(
        session_data, poetry_id, banner_url)
    ret_data = {'errcode': 0}
    if succ:
        ret_data['data'] = {'share_pic_url': share_pic_url}
    else:
        ret_data['errcode'] = -1
        ret_data['errmsg'] = share_pic_url
    return ret_data


@app.route('/service/api/v1/user/poetry/search/hot', methods=['GET'])
@exception_handler
@validate_params({})
@json_response
def search_word_example_api(*args, **kwargs):
    '''
    诗词搜索接口的热门作者
    '''
    result = get_search_data()
    return {'errcode': 0, 'data': result}


@app.route('/service/api/v1/poetry/example/search', methods=['GET'])
@exception_handler
@validate_params()
@json_response
def search_hot_word_api(*args, **kwargs):
    '''
    热门搜索，根据热门搜索例子的id/sub_id
    '''
    page = int(kwargs.get('page', 1))
    count = int(kwargs.get('count', 20))
    cat_id = int(kwargs.get('id', 1))
    sub_id = int(kwargs.get('sub_id', 1))
    data = search_by_cat(cat_id, sub_id, page, count)
    return {'errcode': 0, 'data': data}


@app.route('/service/api/v1/sentence/everyday', methods=['GET'])
@exception_handler
@validate_params({'session_id': 1})
@json_response
def everyday_data_api(*args, **kwargs):
    '''
    每日一句，根据日期或者id 获取相应个数的句子

    Parameters:
        | date_str  | string | 句子对应的日期 |
        | id        | string | 句子的id |
        | count     | int | 句子的个数 |
        | index     | index | 当count不为0时，对应的id/date_str的位置 0 ~ 4 |

    Return：
        count == 1
        返回单个句子的object
        count > 1
        返回句子的列表
    '''
    date_str = kwargs.get('date_str')
    _id = kwargs.get('id')
    if not _id and not date_str:
        return {'errcode': -1, 'errmsg': u'缺少必要参数'}
    session_data = kwargs['session']
    count = int(kwargs.get('count', 1))
    index = int(kwargs.get('index', 2))
    if _id is not None:
        result = get_every_by_id(session_data, int(_id), count, index)
    else:
        result = everyday_sentence(session_data, date_str)
    return {'errcode': 0, 'data': result}


@app.route('/service/api/v1/sentence/everyday/recommend', methods=['GET'])
@exception_handler
@validate_params({'session_id': 1})
@json_response
def recommend_everyday_api(*args, **kwargs):
    '''
    每日一句 推荐阅读最多的4句
    '''
    session = kwargs['session']
    count = int(kwargs.get('count', 4))
    page = int(kwargs.get('page', 1))
    exclude = kwargs.get('exclude', '')
    result = recommend_everyday(session, exclude, page, count)
    return {'errcode': 0, 'data': result}
