# coding=utf-8


from flask import request
from weixin import app
from weixin.utils.decorator import exception_handler, json_response
from weixin.views.poetry import get_poetry_detail_web,\
        get_recommend_count, web_recommend, TAB_HANDLERS, search_poetry


@app.route('/service/api/web/v1/poetrys', methods=['GET'])
@exception_handler
@json_response
def get_web_poetrys_api():
    '''
    网页诗词列表的接口
    '''
    params = request.args
    page = params.get("page", 1)
    count = params.get("count", 20)
    author_id = params.get("author_id")
    page = int(page)
    count = int(count)
    if author_id:
        author_id = int(author_id)
    data = web_recommend(author_id, page, count)
    total = get_recommend_count(author_id)
    ret_data = {"total": total, 'poetry_data': data}
    return {'errcode': 0, 'data': ret_data}


@app.route('/service/api/web/v1/poetry/detail', methods=['GET'])
@exception_handler
@json_response
def get_web_poetry_detail_api():
    '''
    网页版本诗词的详情
    '''
    params = request.args
    poetry_id = params.get("poetry_id")
    errcode, data = get_poetry_detail_web(poetry_id)
    ret_data = {'errcode': 0}
    if not errcode:
        ret_data['errmsg'] = data
        ret_data['errcode'] = -1
    else:
        ret_data['data'] = data
    return ret_data


@app.route('/service/api/web/v1/poetry/authors', methods=['GET'])
@exception_handler
@json_response
def get_authors_list():
    '''
    网页版本使用作者列表，未使用
    '''
    params = request.args
    page = params.get("page", 1)
    count = params.get("count", 20)
    page = int(page)
    count = int(count)
    handler = TAB_HANDLERS['author']
    data = handler(page, count)
    return {'errcode': 0, 'data': data}


@app.route('/service/api/web/v1/poetrys/search', methods=['GET'])
@exception_handler
@json_response
def search_web_api():
    '''
    网页版本使用搜索，未使用
    '''
    params = request.args
    page = params.get('page', 1)
    count = params.get("count", 20)
    keyword = params.get("keyword", '')
    if not keyword:
        return {'errcode': -1, 'errmsg': 'param error'}
    page = int(page)
    count = int(count)
    data = search_poetry(
            {'openid': 'o0aoJ48G_Ynhq4SQjJ_1PfEA0UJg'}, keyword, page, count)
    return {'errcode': 0, 'data': data}
