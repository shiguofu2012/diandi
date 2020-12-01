# coding=utf-8

"""
wechat app session data
"""

import uuid
from weixin.cache import session_cache


def check_session(session_id):
    """check the session data"""
    return session_cache.hget(session_id)


def cache_session(session_data, expire=7200, appid=None):
    """cache session id"""
    session_id = uuid.uuid4().hex
    if appid:
        session_id = "{}_{}".format(appid, session_id)
    session_cache.save_dict(session_id, session_data)
    if expire:
        session_cache.expire(session_id, int(expire))
    return session_id
