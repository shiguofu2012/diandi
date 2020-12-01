# coding=utf-8

from weixin.models.user_model import UserBrowseHistory
from weixin.models.poetry_model import Poetry
from weixin.views.xcx_data import send_template_poetry
from weixin.settings import LOG_CRAWLER as LOG


def get_users(page, count):
    history_obj = UserBrowseHistory()
    return history_obj.get_sended_users(page, count)


def get_recommend_poetry(openid):
    history_obj = UserBrowseHistory()
    poetry_obj = Poetry()
    page = 1
    count = 50
    max_page = 20
    rec_poetry_data = None
    while True or page <= max_page:
        poetrys = poetry_obj.find_poetry({}, page, count, {'likes': -1})
        for poetry in poetrys:
            if not history_obj.is_browsed(openid, poetry['id']):
                rec_poetry_data = poetry
                break
        if rec_poetry_data:
            break
        page += 1
    return rec_poetry_data


def _do_send_template(user):
    poetry_data = get_recommend_poetry(user['openid'])
    # poetry_id = user.pop("poetry_id", 1)
    # poetry_obj = Poetry(id=poetry_id)
    # poetry_data = poetry_obj.find_poetry_by_id()
    if not poetry_data:
        LOG.error("recommend failed: %s", user['openid'])
        return
    res = None
    try:
        res = send_template_poetry(user, poetry_data)
    except Exception as ex:
        LOG.error("openid: %s, ex: %s", user['openid'], ex)
    if res is None:
        LOG.error("openid: %s, send failed", user['openid'])
    else:
        LOG.info("openid: %s, res: %s", user['openid'], res)


def do_send_all(user_list):
    for user in user_list:
        openid = user['openid']
        history_obj = UserBrowseHistory(openid=openid)
        today_record = history_obj.get_today_history()
        if today_record:
            continue
        _do_send_template(user)


def send_user():
    page = 1
    count = 100
    while True:
        user_list = get_users(page, count)
        if not user_list:
            break
        do_send_all(user_list)
        page += 1


if __name__ == '__main__':
    send_user()
