# coding=utf-8

import time
import json
import os
import uuid
from datetime import datetime
from wechat.api import WechatClient
from wechat.crypto.base import WeappCrypto
from weixin.utils.httpclient import HttpClient
from weixin.cache.session import cache_session
from weixin.cache import lock_cache, data_cache
from weixin.settings import LOGGER, XCX_APPID, XCX_APPSEC
from weixin.models.share_model import Share
from weixin.models.user_model import User
from weixin.models.banner import FormId
from weixin.utils.constants import QRCODE_PATH
from weixin.utils.image_utility import get_image_suffix, get_url_from_path, \
        upload_file_to_server


def save_formid(session_data, formid):
    openid = session_data['openid']
    LOGGER.info("openid: %s, formid: %s", openid, formid)
    if formid.find('mock') != -1:
        return
    formid_obj = FormId(openid=openid, formid=formid)
    formid_obj.save()


def upload_pic(session_data, files):
    res = {'errcode': 0}
    result_dict = {}
    for filename, file_storage in files.items():
        if not check_image(file_storage):
            res['errcode'] = -1
            res['errmsg'] = u'图片包含敏感信息，请更换图片'
            return res
        file_storage.seek(0)
        url = upload_file_to_server(file_storage.read())
        LOGGER.info(
                "filename: %s, url: %s, type: %s",
                filename, url, file_storage.mimetype)
        result_dict[filename] = url
    res.update({'data': result_dict})
    return res


def check_image(sio):
    content = sio.read()
    filename = '/tmp/{}'.format(uuid.uuid4().hex)
    with open(filename, 'w') as _file:
        _file.write(content)
    res = check_img_risk(filename)
    LOGGER.info(res)
    if res.get('errcode') != 0:
        return False
    return True


def login_by_session(session_data, encrypted_data, padding):
    '''login by session id'''
    session_key = session_data['session_key']
    if encrypted_data and padding:
        data = decrypted_data(session_key, encrypted_data, padding)
    else:
        data = {
            "unlockMissionCount": 1,
            "userCredit": 0,
            "nickName": '',
            "headImgUrl": '',
            }
    return {'errcode': 0, 'data': data}


def login_by_code(code, encrypted_data, padding):
    ''''''
    client = WechatClient(XCX_APPID, XCX_APPSEC, session=data_cache)
    session_data = client.weapp.fetch_user_session(code)
    session_id = cache_session(session_data)
    userdata = login_by_session(session_data, encrypted_data, padding)
    userdata.update({'session_id': session_id})
    return {'errcode': 0, 'data': userdata}


def create_qrcode(
        scene, page="pages/detail/detail", width=100, is_hyaline=True,
        appid=XCX_APPID, appsec=XCX_APPSEC):
    client = WechatClient(appid, appsec, session=data_cache)
    resp = client.weapp.generate_qrcode(page, scene, width, is_hyaline)
    qr_content = resp.content
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    file_dir = os.path.join(QRCODE_PATH, date_str)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    suffix = get_image_suffix(qr_content)
    filename = uuid.uuid4().hex + '.' + suffix
    abpath = os.path.join(file_dir, filename)
    with open(abpath, "w") as qr_file:
        qr_file.write(qr_content)
    # url = QR_URI + date_str + '/' + filename
    url = get_url_from_path(abpath)
    return {'url': url, 'local_path': abpath}


def send_template_poetry(user_data, poetry_data):
    author_id = poetry_data['author_id']
    author = poetry_data['author']
    title = poetry_data['title']
    openid = user_data['openid']
    recited = user_data['recited']
    if not isinstance(author, unicode):
        author = unicode(author, 'utf-8')
    if not isinstance(title, unicode):
        title = unicode(title, 'utf-8')
    form_obj = FormId(openid=openid)
    form_record = form_obj.get_one_formid()
    if not form_record:
        LOGGER.info("openid: %s not found formid", openid)
        return {}
    template_id = 'tm5oAyq-YcBJhP2EOIAskBbGZp2Iyq0JVzfv0083e-Y'
    data = {}
    data['touser'] = openid
    data['template_id'] = template_id
    data['form_id'] = form_record['formid']
    data['page'] = '/pages/authorPoetry/authorPoetry?id=%s' % author_id
    keywords = {}
    keywords['keyword1'] = {'value': u'每日一学'.encode("utf-8")}
    keywords['keyword2'] = {'value': title.encode("utf-8")}
    keywords['keyword3'] = {'value': (u"%s诗词" % author).encode("utf-8")}
    keywords['keyword4'] = {'value': recited}
    keywords['keyword5'] = {'value': u"点击进去查看详情".encode("utf-8")}
    data['data'] = keywords
    LOGGER.info(data)
    client = WechatClient(XCX_APPID, XCX_APPSEC, session=data_cache)
    res = client.weapp.send_template_msg(data)
    return res


def decrypted_share_info(
        session_data,
        encrypted_data,
        padding,
        page_path,
        is_share):
    session_key = session_data['session_key']
    crypto = WeappCrypto(session_key, padding)
    share_data = crypto.decrypt(encrypted_data)
    open_gid = share_data['openGId']
    openid = session_data['openid']
    share_info = {
            'open_gid': open_gid,
            'openid': openid,
            'page': page_path,
            'op': 'share' if is_share else 'click',
            'times': 1
            }
    share_obj = Share(**share_info)
    shared_info = share_obj.check_share_info()
    if not shared_info:
        share_obj.save()
    else:
        share_id = shared_info['id']
        share_obj.id = share_id
        share_obj.inc_times()
    data = {'open_gid': open_gid}
    return {'errcode': 0, 'data': data}


def decrypted_data(session_key, encrypted_data, padding):
    '''
    decrypt userdata from encrypted data
    and get userinfo
    '''
    crypto = WeappCrypto(session_key, padding)
    userdata = crypto.decrypt(encrypted_data)
    appid = userdata.pop("watermark", {}).get("appid", '')
    userdata.update({'appid': appid})
    user_data = ship_userdata(userdata)
    return user_data
    # _lock = lock_cache.lock(openid)
    # if _lock:
    #     user_obj = XcxUserObject(**saved_data)
    #     userinfo = user_obj.get_user_by_unionid()
    #     if not userinfo:
    #         ret = user_obj.save()
    #         LOG.debug("save user: %s, openid: %s", ret, openid)
    #         unlock_level = 1
    #         credit = 0
    #     else:
    #         unlock_level = userinfo.get("level", 1)
    #         credit = userinfo.get("credit", 0)
    #     lock_cache.unlock(_lock)
    #     mission_data = {
    #         "unlockMissionCount": unlock_level,
    #         "userCredit": credit,
    #         "nickName": userdata['nickName'],
    #         "headImgUrl": userdata['avatarUrl']
    #         }
    # else:
    #     LOG.info("openid: %s lock error", openid)
    #     mission_data = {
    #         "errmsg": u"操作频繁，请稍后再试"
    #         }
    # return mission_data


def ship_userdata(userdata):
    """
    map the wechat return userdata to local db userdata
    """
    user = {}
    user['nickname'] = userdata['nickName']
    user['openid'] = userdata['openId']
    user['country'] = userdata['country']
    user['province'] = userdata['province']
    user['headimgurl'] = userdata['avatarUrl']
    user['language'] = userdata['language']
    user['sex'] = userdata['gender']
    user['created'] = int(time.time())
    # user['appid'] = userdata.get("appid", '')
    user['unionid'] = userdata.get("unionId", '')
    user['city'] = userdata.get("city", '')
    user_obj = User(**user)
    _lock = lock_cache.lock(user_obj.openid)
    if _lock:
        old_user = user_obj.find_by_openid()
        if old_user:
            update_data = _compare(old_user, user)
            if update_data:
                user_obj.update_user(update_data)
        else:
            user_obj.save_user()
        lock_cache.unlock(_lock)
    else:
        pass
    return user


def _compare(old_user, new_user):
    update_keys = (
            "nickname", 'country', 'province', 'headimgurl',
            'language', 'sex', 'city')
    update_data = {}
    for key in update_keys:
        old_value = old_user.get(key)
        new_value = new_user.get(key)
        if old_value != new_value:
            update_data[key] = new_value
    return update_data


def check_msg_risk(content):
    client = WechatClient(XCX_APPID, XCX_APPSEC, session=data_cache)
    url = 'https://api.weixin.qq.com/wxa/msg_sec_check?'\
        'access_token={}'.format(client.access_token)
    _http = HttpClient()
    if isinstance(content, unicode):
        content = content.encode("utf-8")
    data = {'content': content}
    data = json.dumps(data, ensure_ascii=False)
    res = _http.post(url, data=data)
    return res


def check_img_risk(image_path):
    client = WechatClient(XCX_APPID, XCX_APPSEC, session=data_cache)
    url = 'https://api.weixin.qq.com/wxa/img_sec_check?'\
        'access_token={}'.format(client.access_token)
    media = {'media': open(image_path, 'rb')}
    _http = HttpClient()
    res = _http.post(url, files=media)
    return res;