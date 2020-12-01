# coding=utf-8

import re
import random
import time
from weixin.models.poetry_model import GridPoetry
from weixin.models.user_model import GridUser
from weixin.models.poetry_model import HintHistory
from weixin.models.grid_help import HelpInfo
from weixin.cache import lock_cache
from weixin.settings import LOGGER as LOG
from weixin.views.grid_user import notify_helpok

HANZI_PATTERN = ur"[\u4E00-\u9FA5]+"


def level_data(level, is_helper, session_data):
    openid = session_data['openid']
    user_instance = GridUser(openid=openid)
    res = {}
    is_helper = int(is_helper)
    if not is_helper:
        user = user_instance.find_by_openid()
        if not user:
            res.update({'errcode': -1, 'errmsg': u"找不到用户记录"})
            return res
        max_level = user.get("level", 1)
        level = int(level)
        if level > max_level:
            res.update({'errcode': -1, 'errmsg': u"还未解锁"})
            return res
    grid_instance = GridPoetry(level=level)
    poetry_data = grid_instance.get_level_data()
    if not poetry_data:
        res.update({'errcode': -1, 'errmsg': u"好厉害，你已经通关了"})
        return res
    data = ship_level_data(poetry_data)
    hint_instance = HintHistory(openid=openid, level=level)
    hints_data = hint_instance.get_hint_data()
    hinted_data = map(
            lambda x: {"index": x['index'], "word": x['word']}, hints_data)
    data['hint_data'] = hinted_data
    res.update({'errcode': 0, "data": data})
    return res


def validate_answer(params, session_data):
    level = params['level']
    answer = params['answer']
    is_helper = params.get("is_help")
    res = {'errcode': 0}
    openid = session_data['openid']
    grid_instance = GridPoetry(level=level)
    poetry_data = grid_instance.get_level_data()
    if not poetry_data:
        res.update({'errcode': -1, 'errmsg': u"好厉害，你已经通关了"})
        return res
    right_answer = poetry_data['answer']
    if right_answer == answer:
        if not is_helper:
            user_answer_right(openid, poetry_data)
        else:
            uid = params.get("uid")
            help_ok(uid, openid, level, right_answer)
        ret_data = answer_right_data(poetry_data)
        res.update({'data': ret_data})
    else:
        res.update({'data': {'right': 0}})
    return res


def help_ok(uid, openid, level, right_answer):
    '''user with openid help the user with uid'''
    help_data = {
            "openid": openid,
            "uid": uid,
            "created": int(time.time() * 1000),
            "level": level}
    helper_instance = HelpInfo(**help_data)
    helper_record = helper_instance.find_one()
    if not helper_record:
        helper_instance.save()
    LOG.info("openid: %s help uid: %s answer level: %s", openid, uid, level)
    helpered_obj = GridUser(id=uid)
    user = helpered_obj.find_by_uid()
    helper_data = {'answer': right_answer, "openid": openid}
    ret = notify_helpok(user, level, helper_data)
    LOG.info("notify: %s ret: %s, level: %s", openid, ret, level)


def hint_poetry(session_data, level, is_help=None):
    openid = session_data['openid']
    user_instance = GridUser(openid=openid)
    res = {'errcode': -1}
    lock_key = "credit_{}".format(openid)
    _lock = lock_cache.lock(lock_key)
    if not _lock:
        res.update({'errmsg': u"请求太频繁，稍后再试"})
        return res
    user_data = user_instance.find_by_openid()
    if not is_help:
        user_level = user_data.get("level", 1)
        if user_level < level:
            lock_cache.unlock(lock_key)
            res.update({'errmsg': u"关卡未解锁"})
            return res
    if user_data.get("credit", 0) < 10:
        lock_cache.unlock(lock_key)
        res.update({'errmsg': u"金币不足，获取金币?", 'errcode': -8})
        return res
    user_instance.increase_credit(-10)
    left = user_data.get("credit") - 10
    lock_cache.unlock(lock_key)
    grid_instance = GridPoetry(level=level)
    poetry_data = grid_instance.get_level_data()
    if not poetry_data:
        res.update({'errmsg': u"好厉害，你已经通关了"})
        return res
    answer = poetry_data['answer']
    hint_instance = HintHistory(openid=openid, level=level)
    hints_data = hint_instance.get_hint_data()
    hinted_index = map(lambda x: x['index'], hints_data)
    if len(hinted_index) == len(answer):
        res.update({'errmsg': u"已经提示完了，您还没看出答案？"})
        return res
    hint_index = -1
    while hint_index < 0 or hint_index in hinted_index:
        hint_index = random.randint(0, len(answer) - 1)
    hint_word = answer[hint_index]
    data = {
            "index": hint_index,
            'word': hint_word,
            "openid": openid,
            "level": level,
            "user_credit": left}
    hint_instance = HintHistory(**data)
    hint_instance.save_hint_data()
    res.update({'errcode': 0, 'data': data})
    return res


def user_answer_right(openid, poetry_data):
    user_instance = GridUser(openid=openid)
    user_data = user_instance.find_by_openid()
    user_level = user_data.get("level", 1)
    if user_level <= poetry_data['level']:
        user_instance.answer_right()


def answer_right_data(poetry_data):
    ret_data = {}
    dynasty = poetry_data['dynasty']
    author = poetry_data['author']
    title = poetry_data['title']
    answer = poetry_data['answer']
    content = poetry_data['poetry']
    content = u"。".join(content.split(u"。")[:4])
    content = content.replace(u"。", "\n")
    content = content.replace(answer, u"{}".format(answer))
    ret_data['poetry_id'] = poetry_data.get("poetry_id", '')
    ret_data['right'] = 1
    ret_data['title'] = title
    ret_data['author'] = u"{}·{}".format(dynasty, author)
    ret_data['poetry'] = content
    ret_data['level'] = poetry_data['level']
    return ret_data


def ship_level_data(poetry_data):
    ret_data = {}
    answer = poetry_data['answer']
    content = poetry_data['poetry']
    answer_count = len(answer)
    level_riddle = rand_mix(answer, content)
    ret_data['riddle'] = level_riddle
    ret_data['answer_count'] = answer_count
    ret_data['level'] = poetry_data['level']
    return ret_data


def rand_mix(answer, content):
    '''rand mix error data'''
    content = content.replace(answer, '')
    pattern = re.compile(HANZI_PATTERN)
    all_hanzi = pattern.findall(content)
    all_hanzi = ''.join(all_hanzi)
    mix_count = 9 - len(answer)
    if mix_count > 0:
        for index in range(mix_count):
            mix_hanzi = random.choice(all_hanzi)
            answer += mix_hanzi
    answer = list(answer)
    random.shuffle(answer)
    answer = ''.join(answer)
    return answer
