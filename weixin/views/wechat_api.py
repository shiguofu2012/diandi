# coding=utf-8
"""jsapi config"""

import json
from wechat.api import WechatClient
from weixin.cache import wx_cache
from weixin.settings import APPID, APPSEC
from weixin.utils.utils import WECHAT_USR_SESSION as session_client
from weixin.settings import LOGGER

CLIENT = WechatClient(APPID, APPSEC, session=wx_cache)


def configJS(url):
    return CLIENT.jsapi.get_jsapi_data(url)


def long2short(url):
    '''
    long url to short url;
    '''
    resp = CLIENT.tools.short_url(url)
    if "errcode" in resp and resp['errcode'] != 0:
        return False, resp.get("errmsg", '')
    return True, resp.get('short_url')


def login(code):
    userinfo = code2userinfo(code)
    openid = userinfo['openid']
    session_key = session_client.generate_token(openid)
    return session_key


def code2userinfo(code):
    user_token_data = CLIENT.oauth.fetch_user_access_token(code)
    LOGGER.info(user_token_data)
    openid = user_token_data['openid']
    refresh_token = user_token_data['refresh_token']
    userdata = CLIENT.oauth.get_user_info(openid)
    userdata.update({"refresh_token": refresh_token})
    LOGGER.info(userdata)
    return userdata


def get_subscribe_userdata(openid):
    res = {"errcode": -1}
    try:
        userdata = CLIENT.user.get(openid)
        res.update({'errcode': 0, 'data': userdata})
    except Exception as ex:
        LOGGER.error("openid: %s, ex: %s", openid, ex, exc_info=True)
        res.update({"errmsg": ex})
    return res


def login_qrcode(union_id):
    '''带参数二维码关注后登陆'''
    default_expire = 86400
    data = {}
    data['expire_seconds'] = default_expire
    data['action_name'] = 'QR_STR_SCENE'
    data['action_info'] = {"scene": {'scene_str': union_id}}
    res = None
    try:
        res = CLIENT.qrcode.create(data)
    except Exception as ex:
        LOGGER.error("qrcode get ex: %s", ex, exc_info=True)
    ticket = res.get("ticket")
    if not ticket:
        LOGGER.info("create qrcode: %s, res:%s", union_id, res)
        return
    resp = CLIENT.qrcode.showqrcode(ticket)
    if 'errcode' in resp and resp['errcode'] != 0:
        LOGGER.info("union_id: %s error: %s", union_id, resp.get("errmsg", ''))
        return
    return resp.get("data", '')


def query_menu():
    menu_data = CLIENT.menu.query()
    return menu_data


def set_menu(data):
    return CLIENT.menu.create(data)


def send_miniapp(openid, appid, title, page, thumb_path):
    data = {}
    thumb_media_id = ''
    try:
        res = CLIENT.material.add_temp_material("image", thumb_path)
        thumb_media_id = res.get("media_id", '')
        if isinstance(thumb_media_id, unicode):
            thumb_media_id = thumb_media_id.encode("utf-8")
    except Exception as ex:
        LOGGER.error("upload tmp media error: %s", ex)
    data['touser'] = openid
    data['msgtype'] = 'miniprogrampage'
    data['miniprogrampage'] = {
            'title': title,
            'appid': appid,
            'pagepath': page,
            'thumb_media_id': thumb_media_id}
    ret = False
    try:
        data = json.dumps(data, ensure_ascii=False)
        res = CLIENT.kefu_msg.send(data)
        if 'errcode' in res and res['errcode'] == 0:
            ret = True
        else:
            LOGGER.error("openid: %s, error: %s", openid, res.get("errmsg"))
    except Exception as ex:
        LOGGER.info("openid: %s, ex: %s", openid, ex)
    return ret
