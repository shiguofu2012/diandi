# coding=utf-8

import os
import time
import uuid
import imghdr
from StringIO import StringIO
from datetime import datetime
from weixin.models.user_model import MpUser
from weixin.views.wechat_api import login_qrcode, get_subscribe_userdata
from weixin.utils.constants import TMP_PATH, STATIC_URI
from weixin.utils.utils import USER_SESSION as session_client
from weixin.settings import LOGGER as LOG


def get_login_code():
    res = {'errcode': -1}
    _id = uuid.uuid4().hex
    qr_data = login_qrcode(_id)
    if not qr_data:
        res.update({'errmsg': u"获取二维码出错"})
        return res
    url = _write(qr_data)
    res.update({"data": {'uid': _id, "url": url}, "errcode": 0})
    return res


def login_ok(event_data):
    user_openid = event_data.get('FromUserName')
    qr_scene = event_data.get('EventKey')
    if not user_openid or not qr_scene:
        LOG.error("got error data: %s", event_data)
        return
    uid = qr_scene.split('_')[-1]
    if not uid:
        LOG.error("qrscene error: %s", qr_scene)
        return
    res = get_subscribe_userdata(user_openid)
    if res['errcode'] != 0:
        LOG.error("get userinfo error: %s", res.get("errmsg"))
        nickname = ''
        avatar = ''
    else:
        userinfo = res['data']
        LOG.info(userinfo)
        nickname = userinfo.get("nickname", '')
        avatar = userinfo.get("headimgurl", '')
    user_obj = MpUser(
            uid=uid, nickname=nickname, avatar=avatar,
            openid=user_openid, status=0)
    user_obj.save_mpuser()
    return


def login_status(uid):
    user_obj = MpUser(uid=uid)
    res = {'errcode': 0}
    userdata = user_obj.get_user_by_uid()
    if not userdata:
        res.update({"data": {'status': -1}})
        return res
    status = userdata.get("status", -1)
    login_time = userdata.get("login_time")
    now = time.time()
    if login_time and (now - login_time) > 7200 * 4:
        status = -1
    res.update({"data": {'status': status}})
    if status == 0:
        token = session_client.generate_token(uid)
        res['data'].update({'token': token})
    return res


def user_profile(token):
    res = {'errcode': 0}
    uid = session_client.get_uid(token)
    if not uid:
        res.update({'errcode': 10000, 'errmsg': "invalid token"})
        return res
    user_obj = MpUser(uid=uid)
    userdata = user_obj.get_user_by_uid()
    ret_data = {}
    if not userdata:
        status = -1
        userdata = {}
    else:
        status = userdata['status']
    ret_data['status'] = status
    ret_data['nickname'] = userdata.get("nickname", '')
    ret_data['avatar'] = userdata.get("avatar", '')
    res.update({'data': ret_data})
    return res


def _write(image_data):
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    path = os.path.join(TMP_PATH, date_str)
    if not os.path.exists(path):
        os.makedirs(path)
    filename = uuid.uuid4().hex
    suffix = imghdr.what(StringIO(image_data))
    if suffix:
        filename = filename + '.' + suffix
    abpath = os.path.join(path, filename)
    with open(abpath, 'w') as _file:
        _file.write(image_data)
    req_path = abpath.split("static")[-1]
    return STATIC_URI + req_path
