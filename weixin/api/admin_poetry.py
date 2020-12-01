# coding=utf-8
'''
for admin page http://shiguofu.cn/#/listpoetry

poetry: list/detail
banner: list/detail/delete/add/update
管理后台没有做权限，简单的限制了ip的操作
'''


from weixin import app
from weixin.utils.decorator import exception_handler, validate_params, \
    json_response
from weixin.views.poetry import TAB_HANDLERS, update_poetry, \
    get_recommend_count
from weixin.views.admin import admin_banner_list, update_banner, \
    create_banner, delete_banner
from weixin.views.do_config import upload_image


@app.route('/service/admin/api/web/v1/poetrys', methods=['GET'])
@exception_handler
@validate_params({'session_id': 0})
@json_response
def get_poetrys_api(*args, **kwargs):
    '''
    管理后台的获取列表
    '''
    page = int(kwargs.get('page', 1))
    count = int(kwargs.get('count', 20))
    author_id = kwargs.get('author_id')
    if author_id:
        author_id = int(author_id)
    handlers = TAB_HANDLERS['recommend']
    data = handlers(page, count, author_id)
    total = get_recommend_count(author_id)
    ret_data = {'data': data, 'total': total}
    return {'errcode': 0, 'data': ret_data}


@app.route(
    '/service/admin/api/web/v1/poetrys/<int:poetry_id>', methods=['PUT'])
@exception_handler
@validate_params({'session_id': 0})
@json_response
def update_poetrys_api(*args, **kwargs):
    '''
    管理后台更新诗词的一些数据
    '''
    poetry_id = kwargs.pop('poetry_id')
    ret = {'errcode': 0}
    if not kwargs:
        return ret
    succ, errmsg = update_poetry(poetry_id, kwargs)
    if not succ:
        ret['errmsg'] = errmsg
        ret['errcode'] = -1
    return ret


@app.route('/service/admin/api/web/v1/banner', methods=['GET'])
@exception_handler
@validate_params()
@json_response
def admin_banner_api(*args, **kwargs):
    '''
    管理banner的设置
    '''
    page = int(kwargs.get('page', 1))
    count = int(kwargs.get('count', 20))
    data = admin_banner_list(page, count)
    return {'errcode': 0, 'data': data}


@app.route(
    '/service/admin/api/web/v1/banner/<int:banner_id>',
    methods=['POST']
)
@exception_handler
@validate_params()
@json_response
def update_banner_api(*args, **kwargs):
    '''
    管理banner的设置
    '''
    banner_id = kwargs.pop('banner_id')
    return update_banner(banner_id, kwargs)


@app.route('/service/admin/api/web/v1/banner', methods=['PUT'])
@exception_handler
@validate_params()
@json_response
def save_banner_api(*args, **kwargs):
    '''
    管理banner的设置
    '''
    return create_banner(kwargs)


@app.route(
    '/service/admin/api/web/v1/banner/<int:banner_id>',
    methods=['DELETE']
)
@exception_handler
@json_response
def delete_banner_api(banner_id):
    '''
    管理后台删除 banner
    '''
    return delete_banner(banner_id)



@app.route("/service/admin/api/v1/image/upload", methods=['POST'])
@exception_handler
@json_response
def upload_image_api():
    '''
    update image to qiniu cdn
    '''
    data = upload_image(None, request.files)
    return {'errcode': 0, 'data': data}
