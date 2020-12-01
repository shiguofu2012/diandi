# coding=utf-8

import time
import json
from datetime import datetime
from wechat.api import WechatClient
from wechat.crypto.base import WeappCrypto
from weixin.utils.constants import TemplateId
from weixin.models.user_model import GridUser, NavDiandi, GridFormId
from weixin.models.goods_model import Goods
from weixin.models.grid_help import ShareInfo, ClickInfo
from weixin.cache.session import cache_session
from weixin.cache import lock_cache, data_cache
from weixin.settings import LOGGER as LOG, XCX_APPID_PAYED, XCX_APPSEC_PAYED


def pay_for_credit(openid, goods_id, count):
    user_instance = GridUser(openid=openid)
    goods_instance = Goods(id=goods_id)
    goods_data = goods_instance.find_by_id()
    if not goods_data:
        LOG.critial("id: %s payed not found", goods_id)
        return
    total_count = goods_data['count']
    add_credit_count = count * total_count
    ret = user_instance.increase_credit(add_credit_count)
    LOG.info(
            "openid: %s, goods_id: %d, count: %s, ret: %s",
            openid, goods_id, count, ret)
    if goods_id == 7:
        user_instance = GridUser(openid=openid)
        user_instance.update_user({'new_buy': 0})


def save_formid_grid(session_data, formid, appid=None):
    res = {"errcode": 0}
    if formid.find("mock") != -1:
        res.update({"data": "fake formid not save"})
        return res
    openid = session_data['openid']
    LOG.info("openid: %s, formid: %s", openid, formid)
    if appid is None:
        appid = XCX_APPID_PAYED
    data = {
            "openid": openid,
            "formid": formid,
            "created": int(time.time()),
            'appid': appid}
    formid_instance = GridFormId(**data)
    _id = formid_instance.save()
    res = {"errcode": 0, 'data': {'id': str(_id)}}
    return res


def jump_to_diandi_free(session_data):
    openid = session_data['openid']
    lock_key = "diandi_{}".format(openid)
    _lock = lock_cache.lock(lock_key)
    res = {'errcode': -1}
    if not _lock:
        res.update({"errmsg": u"操作频繁"})
        return res
    instance = NavDiandi(openid=openid, created=int(time.time()))
    if instance.find_one():
        lock_cache.unlock(lock_key)
        res.update({"errcode": 0})
        return res
    else:
        instance.save()
    lock_cache.unlock(lock_key)
    user_instance = GridUser(openid=openid)
    user = user_instance.find_by_openid()
    if not user:
        res.update({"errmsg": u"找不到用户记录"})
        return res
    add_free_credit(user)
    res.update({'errcode': 0, 'data': {"credit": user['credit'] + 10}})
    return res


def login_by_session(session_data, encrypted_data, padding):
    '''login by session id'''
    session_key = session_data['session_key']
    openid = session_data['openid']
    userinfo = {'openId': openid}
    if encrypted_data and padding:
        userinfo = decrypted_data(session_key, encrypted_data, padding)
        appid = userinfo.pop("watermark", {}).get("appid", '')
        userinfo.update({'appid': appid})
    userinfo = ship_userdata(userinfo)
    user_instance = GridUser(openid=openid)
    res = {"errcode": 0}
    lock_key = "uinfo_{}".format(openid)
    _lock = lock_cache.lock(lock_key)
    if not _lock:
        res.update({'errcode': -1, 'errmsg': u"操作频繁"})
        return res
    user_data = user_instance.find_by_openid()
    ret_data = {
        "unlockMissionCount": 1,
        "userCredit": 0,
        "nickName": '',
        "headImgUrl": '',
        "uid": '',
        "new_user": 1
        }
    if user_data:
        nickname = user_data.get("nickname", '')
        head_img = user_data.get("headimgurl")
        if userinfo:
            nickname = userinfo.get("nickname", '')
            head_img = userinfo.get("headimgurl", '')
            update_data = _compare_user(user_data, userinfo)
            if update_data:
                user_instance.update_user(update_data)
                LOG.info(
                        "update user:%s, data:%s",
                        user_instance.openid, update_data)
        lock_cache.unlock(lock_key)
        data = {
                "unlockMissionCount": user_data.get("level", 1),
                "userCredit": user_data.get("credit", 0),
                "nickName": nickname,
                "headImgUrl": head_img,
                "uid": user_data['id'],
                "new_user": user_data.get("new_buy", 1)}
        ret_data.update(data)
    else:
        user_instance = GridUser(**userinfo)
        user_instance.save_user()
        lock_cache.unlock(lock_key)
        user = user_instance.find_by_openid()
        ret_data.update({
            "uid": user['id'],
            "nickName": user['nickname'],
            "headImgUrl": user['headimgurl'],
            "new_user": user['new_buy'],
            "userCredit": user['credit'],
            "unlockMissionCount": user['level']})
    return ret_data


def login_by_code(code, encrypted_data, padding, appid=None):
    '''miniapp login by wx.login'''
    client = WechatClient(
            XCX_APPID_PAYED, XCX_APPSEC_PAYED, session=data_cache)
    session_data = client.weapp.fetch_user_session(code)
    session_id = cache_session(session_data, appid=XCX_APPID_PAYED)
    userdata = login_by_session(session_data, encrypted_data, padding)
    userdata.update({'session_id': session_id})
    return userdata


def _compare_user(old_data, new_data):
    LOG.debug("old: %s, new: %s", old_data, new_data)
    update_key = (
            "nickname", "country", "province", "headimgurl",
            "language", "sex", "city", "credit")
    update_data = {}
    for key in update_key:
        old_value = old_data.get(key)
        new_value = new_data.get(key)
        # if isinstance(new_value, unicode):
        #     new_value = new_value.encode("utf-8")
        # LOG.info("new type: %s", type(new_value))
        comp_value = new_value
        if isinstance(comp_value, unicode):
            comp_value = comp_value.encode("utf-8")
        if comp_value != old_value:
            update_data[key] = new_value
    return update_data


def ship_userdata(userdata):
    """
    map the wechat return userdata to local db userdata
    """
    user = {}
    user['nickname'] = userdata.get('nickName', '')
    user['openid'] = userdata['openId']
    user['country'] = userdata.get('country', '')
    user['province'] = userdata.get('province', '')
    user['headimgurl'] = userdata.get('avatarUrl', '')
    user['language'] = userdata.get('language', '')
    user['sex'] = userdata.get('gender', 0)
    user['created'] = int(time.time())
    # user['appid'] = userdata.get("appid", '')
    user['unionid'] = userdata.get("unionId", '')
    user['city'] = userdata.get("city", '')
    user['level'] = 1
    if userdata.get("nickName", ''):
        user['credit'] = 100
    else:
        user['credit'] = 0
    user['new_buy'] = 1
    return user


def decrypted_data(session_key, encrypted_data, padding):
    '''
    decrypt userdata from encrypted data
    and get userinfo
    '''
    crypto = WeappCrypto(session_key, padding)
    userdata = crypto.decrypt(encrypted_data)
    return userdata


def share_group_info(
        session_data,
        encrypted_data,
        padding,
        page_path,
        share_query):
    try:
        share_query = json.loads(share_query)
    except Exception:
        LOG.info("got unexcepted para: %s", share_query)
        share_query = {}
    session_key = session_data['session_key']
    openid = session_data['openid']
    share_data = decrypted_data(session_key, encrypted_data, padding)
    LOG.info(share_data)
    open_gid = share_data['openGId']
    uid = int(share_query.get("uid", -1))
    if uid == -1:
        return {}
    user_instance = GridUser(id=uid)
    shared_user = user_instance.find_by_uid()
    if not shared_user:
        LOG.error("share user not found: %s, click: %s", shared_user, openid)
        return {}
    shared_openid = shared_user.get("openid")
    if shared_openid == openid:
        return {}
    saved_share_data = {
            "uid": share_query.get("uid", -1),
            "type": share_query.get("type", ''),
            "level": share_query.get("id", -1),
            "page": page_path,
            "open_gid": open_gid}
    share_id = save_share_data(saved_share_data)
    click_info = {
            "openid": openid,
            "share_id": str(share_id),
            "created": int(time.time() * 1000),
            "update_time": int(time.time() * 1000),
            "times": 1}
    click_instance = ClickInfo(**click_info)
    # LOCK
    click_info = click_instance.find_click()
    if click_info:
        update_data = {'update_time': int(time.time() * 1000)}
        click_instance.increase_times()
        click_instance.update(update_data)
    else:
        click_instance.save()
        if share_query.get("type") == 'free':
            add_free_credit(shared_user, add_code=2)
    return {'open_gid': open_gid}


def add_free_credit(user_data, count=10, add_code=0):
    '''
    0 --- jump to diandi;
    1 --- invited friend to;
    2 --- invited group members;
    '''
    uid = user_data['id']
    openid = user_data['openid']
    today = datetime.now()
    key = "max_coin_{}_{}".format(uid, today.strftime("%Y-%m-%d"))
    expire = 86400
    if data_cache.inc(key, expire=expire) > 10:
        return 0
    user_instance = GridUser(id=uid)
    user_instance.increase_credit(count)
    # notify the user by template msg
    LOG.info("openid: %s, add 10", openid)


def share_friend_info(session_data, page_path, share_query):
    try:
        share_query = json.loads(share_query)
    except Exception:
        LOG.info(
                "error: %s, session: %s, page: %s",
                share_query, session_data, page_path)
        return {}
    openid = session_data['openid']
    uid = int(share_query.get('uid', -1))
    user_instance = GridUser(id=uid)
    shared_user = user_instance.find_by_uid()
    if not shared_user:
        LOG.error("share user not found: %s, click: %s", shared_user, openid)
        return {}
    shared_openid = shared_user.get("openid")
    if shared_openid == openid:
        return {}
    saved_share_data = {
            "uid": share_query.get("uid", -1),
            "type": share_query.get("type", ''),
            "level": share_query.get("id", -1),
            "page": page_path,
            "open_gid": ''}
    share_id = save_share_data(saved_share_data)
    click_info = {
            "openid": openid,
            "share_id": str(share_id),
            "created": int(time.time() * 1000),
            "update_time": int(time.time() * 1000),
            "times": 1}
    click_instance = ClickInfo(**click_info)
    lock_key = "click_{}".format(share_query.get("uid"))
    _lock = lock_cache.lock(lock_key)
    if not _lock:
        return {}
    click_info = click_instance.find_click()
    if click_info:
        lock_cache.unlock(lock_key)
        update_data = {'update_time': int(time.time() * 1000)}
        click_instance.increase_times()
        click_instance.update(update_data)
    else:
        click_instance.save()
        lock_cache.unlock(lock_key)
        if share_query.get("type") == 'free':
            add_free_credit(share_query.get("uid"), add_code=1)
    return {}


def save_share_data(saved_share_data):
    share_instance = ShareInfo(**saved_share_data)
    uid = saved_share_data['uid']
    lock_key = "share_{}".format(uid)
    _lock = lock_cache.lock(lock_key)
    if not _lock:
        return {}
    share_data = share_instance.find_one()
    if share_data:
        lock_cache.unlock(lock_key)
        ret = str(share_data['_id'])
    else:
        ret = share_instance.save_share()
        lock_cache.unlock(lock_key)
    return ret


def get_goods_list(session_data):
    goods_instance = Goods()
    goods_list = goods_instance.find_all()
    res = {"errcode": 0}
    result = []
    for goods in goods_list:
        _id = goods['id']
        if _id == 7:
            break
        price = round(goods['price'] / 100.0, 2)
        count = goods['count']
        result.append({'id': _id, 'price': price, 'sum': count})
    res.update({'data': {"config": result, "sw": 1}})
    return res


def notify_helpok(helpered_data, level, helper_data):
    uid = helpered_data['id']
    share_instance = ShareInfo(uid=uid, type='help', level=level)
    share_data = share_instance.find_one()
    if not share_data:
        LOG.error(
                "uid: %s not share level: %s, helper: %s",
                uid, level, helper_data)
        return {"errcode": -1, 'errmsg': "not share"}
    notify = share_data.get("notify")
    if notify:
        return {'errcode': -1, 'errmsg': 'already help'}
    openid = helpered_data['openid']
    form_instance = GridFormId(openid=openid)
    lock_key = "forid_{}".format(openid)
    _lock = lock_cache.lock(lock_key)
    if not _lock:
        LOG.info("openid:%s notify error", openid)
        return {"errcode": -1, 'errmsg': u"lock error"}
    form_record = form_instance.find_one()
    lock_cache.unlock(lock_key)
    template_id = TemplateId.helper.value
    helper_openid = helper_data.get("openid")
    helper_name = u'匿名好友'.encode("utf-8")
    if helper_openid:
        user_instance = GridUser(openid=helper_openid)
        helper_user_info = user_instance.find_by_openid()
        if helper_user_info:
            helper_name = helper_user_info.get("nickname", '')
    helper_answer = helper_data.get("answer", u"")
    helper_time = helper_data.get("time", "") or \
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {}
    data['touser'] = openid
    data['template_id'] = template_id
    data['form_id'] = form_record['formid'].encode("utf-8")
    data['page'] = '/pages/mission/mission?id={}&type=helpok'.format(level)
    keywords = {}
    keywords['keyword1'] = {'value': helper_name}
    keywords['keyword2'] = {
            'value':
            u"好友在诗词九宫格帮你回答了{}关，快去看看吧".format(level).encode("utf-8")}
    keywords['keyword3'] = {
            'value': u"【{}】".format(helper_answer).encode("utf-8")}
    keywords['keyword4'] = {'value': helper_time}
    data['data'] = keywords
    client = WechatClient(
            XCX_APPID_PAYED, XCX_APPSEC_PAYED, session=data_cache)
    res = client.weapp.send_template_msg(data)
    if res.get("errcode") == 0:
        ret = share_instance.notify_user()
        LOG.info("notify ret: %s", ret)
    return res
