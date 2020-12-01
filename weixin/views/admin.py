# coding=utf-8

import time
from urlparse import urlparse
from urlparse import parse_qsl
from weixin.utils.constants import DETAIL_PAGE
from weixin.utils.timeutils import stamp2time
from weixin.settings import LOGGER as LOG
from weixin.models.banner import Banner


def admin_banner_list(page, count):
    banner_obj = Banner()
    banners = banner_obj.get_banner(None, page, count)
    total = banner_obj.count()
    for banner in banners:
        banner['created'] = stamp2time(banner['created'] / 1000)
        banner['enabled'] = True if banner['enabled'] else False
        banner['poetry_id'] = _parse_poetry_id(banner['page_path'])
    return {"data": banners, "total": total}


def _parse_poetry_id(page_path):
    parsed_ret = urlparse(page_path)
    ret = parse_qsl(parsed_ret.query)
    poetry_id = None
    for param in ret:
        if param[0] == 'id':
            poetry_id = param[1]
            break
    return poetry_id


def update_banner(banner_id, params):
    poetry_id = params.get("poetry_id")
    banner_image = params.get("banner_url")
    enabled = params.get("enabled")
    if poetry_id is None and banner_image is None and enabled is None:
        return {"errcode": 400, "errmsg": "params error"}
    update_data = {}
    if poetry_id is not None:
        update_data['page_path'] = DETAIL_PAGE.format(poetry_id)
    if banner_image is not None:
        update_data['banner_url'] = banner_image
    if enabled is not None:
        update_data['enabled'] = int(enabled)
    banner_obj = Banner(id=banner_id)
    banner = banner_obj.get_banner_by_id()
    if not banner:
        return {"errcode": 404, 'errmsg': "Not Found"}
    LOG.info("update id: %s, data: %s", banner_id, update_data)
    banner_obj.update_banner_by_id(update_data)
    return {'errcode': 0}


def create_banner(params):
    poetry_id = params.get("poetry_id")
    banner_image = params.get("banner_url")
    enabled = params.get("enabled")
    data = {
            "page_path": DETAIL_PAGE.format(poetry_id),
            "banner_url": banner_image,
            "enabled": int(enabled),
            "created": int(time.time() * 1000)}
    banner_obj = Banner()
    succ, msg = banner_obj.save_banner(data)
    if not succ:
        return {'errcode': -1, "errmsg": msg}
    return {'errcode': 0}


def delete_banner(banner_id):
    banner_obj = Banner(id=banner_id)
    banner_obj.delete_banner()
    return {'errcode': 0}
