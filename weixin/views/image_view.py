# coding=utf-8

import os
import random
from datetime import datetime
from weixin.utils.constants import BANNER_SAMP, DIANDI_QR
from weixin.models.user_model import User
from weixin.views.poetry import get_recommend_poetry
from weixin.views.do_config import get_lunar_date
from weixin.utils.image_utility import get_url_from_path, \
        re_construct_content, draw_morning_image, get_local_path_from_url
from weixin.views.xcx_data import check_msg_risk, check_img_risk
from weixin.settings import LOGGER as LOG


def recommend_one_poetry(openid):
    user_obj = User(openid=openid)
    user = user_obj.find_by_openid()
    if not user:
        return {'errcode': -1, 'errmsg': u"用户未授权，请点击‘我的->点击登录’"}
    poetry_data = get_recommend_poetry()
    author = poetry_data['author']
    title = poetry_data['title']
    poetry_id = poetry_data['id']
    content = poetry_data['content']
    content = re_construct_content(content, 22)
    if isinstance(content, unicode):
        content = content.encode("utf-8")
    banner = poetry_data['banner']
    if not banner:
        banner = random.choice(os.listdir(BANNER_SAMP))
        banner = os.path.join(BANNER_SAMP, banner)
        banner = get_url_from_path(banner)
    today = datetime.now()
    lunar_date = get_lunar_date()
    date_list = lunar_date.split("\n")
    lunar_date = ''.join(date_list[:2])
    recommend_poetry = {
            'nickname': user['nickname'],
            'head_img': user['headimgurl'],
            "id": poetry_id,
            'title': title,
            'content': content,
            'banner': banner,
            'date_str': today.strftime("%m-%d"),
            'lunar_date': lunar_date,
            'year': '{}年 {}'.format(today.year, date_list[2]),
            'msg': u'早安'.encode('utf-8'), 'author': author,
            'qrcode': DIANDI_QR}
    return {'errcode': 0, 'data': recommend_poetry}


def user_share_morning(session_data, banner, content):
    res = check_msg_risk(content)
    LOG.info('content: %s, risk: %s', content, res)
    if res.get('errcode') != 0:
        res['errmsg'] = u'文本包含敏感词汇，请修改后重新提交'
        return res
    banner = get_local_path_from_url(banner)
    res = check_img_risk(banner)
    LOG.info('banner: %s, risk: %s', banner, res)
    if res.get('errcode') != 0:
        res['errmsg'] = u'图片包含敏感信息，请更换后重新提交'
        return res
    local_path = draw_morning_image(banner, '', '', '', content, 21)
    return {'errcode': 0, 'data': {'url': get_url_from_path(local_path)}}
