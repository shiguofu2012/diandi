# coding=utf-8
# !/usr/bin/python

import time
import os
import random
from datetime import datetime, timedelta
from weixin.models.author_model import Author
from weixin.models.poetry_model import Poetry, Sentence, SentenceDaily
from weixin.models.share_model import Share
from weixin.models.user_model import UserBrowseHistory, User
from weixin.models.search_keyword import SearchKeyword
from weixin.utils.timeutils import stamp2time
from weixin.utils.constants import PoetryOp, HEADIMG_TMP, BANNER_SAMP, \
    DIANDI_QR, SearchCat
from weixin.utils.image_utility import get_image_suffix, draw_poetry_share, \
    get_local_path_from_url, get_url_from_path, random_choose_banner
from weixin.utils.httpclient import HttpClient
from weixin.utils.decorator import perf_logging
from weixin.views.xcx_data import create_qrcode, check_img_risk, check_msg_risk
from weixin.views.wechat_api import send_miniapp
# from weixin.views.tbk_views import list_goods
from weixin.settings import TabId, XCX_APPID
from weixin.settings import LOG_TRACK as LOG, LOGGER

TAB_HANDLERS = {}


def register_tab(tab_name):
    def register(method):
        TAB_HANDLERS[tab_name] = method
    return register


def get_qrcode(openid, poetry_id, scene):
    user_history_obj = UserBrowseHistory(openid=openid, poetry_id=poetry_id)
    user_history = user_history_obj.check_browse()
    create = 1
    if user_history and user_history['qrcode']:
        qr_url = user_history['qrcode']
        local_path = get_local_path_from_url(qr_url)
        if os.path.exists(local_path):
            create = 0
    if create:
        qrcode_url_data = create_qrcode(scene)
        qr_url = qrcode_url_data['url']
        local_path = qrcode_url_data['local_path']
        user_history_obj.update_qrcode(qr_url)
    return local_path


def update_poetry(poetry_id, update_data):
    poetry_instance = Poetry(id=poetry_id)
    poetry_data = poetry_instance.find_poetry_by_id()
    if not poetry_data:
        return False, u"找不到记录"
    real_update_data = {}
    for key, value in update_data.items():
        old_value = poetry_data.get(key)
        if isinstance(value, unicode):
            value = value.encode("utf-8")
        if old_value != value:
            real_update_data[key] = value
    if not real_update_data:
        return True, "OK"
    ret = poetry_instance.update_poetry_by_id(real_update_data)
    LOGGER.info("id: %s, data: %s, ret: %s", poetry_id, real_update_data, ret)
    return True, "OK"


def get_headimg_path(headimg_url, openid):
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    dir_path = os.path.join(HEADIMG_TMP, date_str)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    commend_ret = os.popen("ls %s/%s* -t" % (dir_path, openid))
    exists_head = commend_ret.read()
    if exists_head:
        return exists_head.split('\n')[0]
    client = HttpClient()
    pic_content = client.get(headimg_url)
    suffix = get_image_suffix(pic_content)
    filename = openid + '.' + suffix
    abpath = os.path.join(dir_path, filename)
    with open(abpath, 'w') as head_file:
        head_file.write(pic_content)
    return abpath


def user_share_image(session_data, data):
    title = data['title']
    content = data['content']
    res = check_msg_risk(content)
    LOGGER.info('content: %s, risk: %s', content, res)
    if res.get('errcode') != 0:
        res['errmsg'] = u'内容包含敏感信息，请更改后重新提交'
        return res
    res = check_msg_risk(title)
    LOGGER.info('title: %s, risk: %s', title, res)
    if res.get('errcode') != 0:
        res['errmsg'] = u'标题内容包含敏感信息，请更改后重新提交'
        return res
    banner = data['banner']
    openid = session_data['openid']
    user_obj = User(openid=openid)
    user = user_obj.find_by_openid()
    if not user:
        msg = u"请到首页点击“我的->点击登录”后重新生成分享图"
        return {'errcode': -1, 'errmsg': msg}
    poetry_id = data.get('poetry_id')
    nickname = user['nickname']
    headimg_url = user['headimgurl']
    if not banner.startswith('http'):
        return {'errcode': -1, 'errmsg': u'请先上传图片'}
    banner_path = get_local_path_from_url(banner)
    res = check_img_risk(banner_path)
    LOGGER.info('image: %s risk: %s', banner_path, res)
    if res.get('errcode') != 0:
        res['errmsg'] = u'图片包含敏感信息，请更换后重试!'
        return res
    headimg_path = get_headimg_path(headimg_url, openid)
    if poetry_id:
        scene = "id={poetry_id}&uid={uid}".format(
                poetry_id=poetry_id,
                uid=user['id']
        )
        qrcode_path = get_qrcode(openid, poetry_id, scene)
    else:
        qrcode_path = DIANDI_QR
    share_pic_path = draw_poetry_share(
        nickname,
        headimg_path,
        qrcode_path,
        banner_path,
        title,
        content)
    url = get_url_from_path(share_pic_path)
    return {'errcode': 0, 'data': {'url': url}}


@perf_logging
def generate_share_pic(session_data, poetry_id, banner_url=None):
    start = time.time()
    openid = session_data['openid']
    user_obj = User(openid=openid)
    user = user_obj.find_by_openid()
    if not user:
        return False, u"请到首页点击“我的->点击登录”后重新生成分享图"
    poetry_obj = Poetry(id=poetry_id)
    poetry = poetry_obj.find_poetry_by_id()
    if not poetry:
        return False, u"找不到诗词"
    if banner_url.startswith('http'):
        return False, u'请先上传图片'
    if not banner_url:
        banner_path = random_choose_banner()
    else:
        banner_path = get_local_path_from_url(banner_url)
    res = check_img_risk(banner_path)
    LOGGER.info('check image res: %s', res)
    if res.get('errcode') != 0:
        return False, u'图片存在敏感信息，请更换后重新提交'
    LOGGER.info("read dbdata: %s", time.time() - start)
    scene = "id={poetry_id}&uid={uid}".format(
            poetry_id=poetry_id,
            uid=user['id'])
    headimg_url = user['headimgurl']
    qrcode_path = get_qrcode(openid, poetry_id, scene)
    LOGGER.info("get qrcode from wx: %s", time.time() - start)
    nickname = user['nickname']
    title = poetry['title']
    content = poetry['content']
    dynasty = poetry['dynasty']
    author_name = poetry['author']
    headimg_path = get_headimg_path(headimg_url, openid)
    LOGGER.info("here: %s", time.time() - start)
    share_pic_path = draw_poetry_share(
        nickname,
        headimg_path,
        qrcode_path,
        banner_path,
        title,
        content,
        dynasty,
        author_name)
    LOGGER.info("draw image: %s", time.time() - start)
    return True, get_url_from_path(share_pic_path)


def get_data(session_data, tab_id, page, count):
    LOG.info(
        "openid: %s, tab: %s, time: %s",
        session_data['openid'],
        tab_id,
        time.time())
    try:
        tab_id = int(tab_id)
    except ValueError:
        return False, u"tabid格式错误"
    tab_type = None
    try:
        tab_type = TabId(tab_id)
    except ValueError:
        return False, u"tabid非法"
    tab_name = tab_type.name.lower()
    tab_handler = TAB_HANDLERS.get(tab_name)
    if tab_handler is None:
        return False, u"未知的tab"
    # goods = list_goods(page=page, count=1)['goods']
    # if goods:
    #     goods_detail = goods[0]
    #     goods_detail['type'] = 1
    #     count -= 1
    tab_data = tab_handler(page, count)
    # if goods:
    #     index = random.randint(0, count)
    #     tab_data.insert(index, goods_detail)
    return True, tab_data


def search_init_data(session_data, page, count):
    LOG.info("user: %s init page: %s", session_data['openid'], page)
    if page == 0:
        page = 1
    poetry_obj = Poetry()
    poetry = poetry_obj.random_get(page, count)
    result = []
    for poetry_item in poetry:
        shiped_poetry = ship_poetry_list(poetry_item)
        result.append(shiped_poetry)
    return result


@perf_logging
def search_poetry(session_data, keyword, page, count):
    openid = session_data['openid']
    search_keyword_obj = SearchKeyword(openid=openid, keyword=keyword)
    search_word_record = search_keyword_obj.check_search()
    if search_word_record:
        search_keyword_obj.id = search_word_record['id']
        search_keyword_obj.inc_times()
    else:
        search_keyword_obj.save()
    search_obj = Poetry(content=keyword)
    start = time.time()
    data = search_obj.search_fulltext(page, count)
    LOG.info("search:%s takes: %s", keyword, time.time() - start)
    result = []
    for poetry_item in data:
        shiped_poetry = ship_poetry_list(poetry_item)
        result.append(shiped_poetry)
    return result


def user_history(session_data, _type, page, count):
    openid = session_data['openid']
    user_history_obj = UserBrowseHistory(openid=openid)
    if _type == PoetryOp.BROWSE.value:
        history_records = user_history_obj.get_user_history(page, count)
    elif _type == PoetryOp.LIKE.value:
        user_history_obj.operation = PoetryOp.LIKE.value
        history_records = user_history_obj.get_user_like(page, count)
    else:
        return []
    history_info = {}
    for record in history_records:
        poetry_id = record['poetry_id']
        created = record['created']
        times = record['times']
        history_info[poetry_id] = {
            'created': stamp2time(created / 1000),
            'times': times
        }
    if not history_info:
        return []
    poetry_obj = Poetry(id=history_info.keys())
    poetrys = poetry_obj.find_poetry_by_ids()
    result = []
    for poetry in poetrys:
        tmp = ship_poetry_list(poetry)
        poetry_id = poetry['id']
        browser_info = history_info.get(poetry_id)
        if browser_info:
            tmp.update(browser_info)
        result.append(tmp)
    return result


def get_share_data(session_data, page, count):
    openid = session_data['openid']
    share_obj = Share(openid=openid)
    share_info = share_obj.find_share_by_openid(page, count)
    result = []
    for share in share_info:
        page = share['page']
        create = share['created']
        gid = share['open_gid']
        time_str = stamp2time(create)
        tmp = {
            'page': page,
            'time': time_str,
            'open_gid': gid
        }
        result.append(tmp)
    return result


def user_operation(session_data, poetry_id, operation):
    openid = session_data['openid']
    try:
        poetry_id = int(poetry_id)
        operation = int(operation)
    except ValueError:
        return False, u"参数格式错误"
    operation_obj = None
    try:
        operation_obj = PoetryOp(operation)
    except ValueError:
        return False, u"无效的操作类型"
    user_history_obj = UserBrowseHistory(
        openid=openid,
        poetry_id=poetry_id,
        operation=operation_obj.value)
    history_record = user_history_obj.check_browse()
    if history_record:
        user_history_obj.user_operation(user_history_obj.operation)
    else:
        user_history_obj.save()
    poetry_op = Poetry(id=poetry_id)
    if operation_obj.value == PoetryOp.LIKE.value:
        inc_count = 1
    elif operation_obj.value == PoetryOp.DISLIKE.value:
        inc_count = 0
    else:
        inc_count = 0
    poetry_op.increase(inc_count)
    return True, 'OK'


def get_author_data(session_data, author_id, page, count):
    author_obj = Author(id=author_id)
    author = author_obj.find_author_by_id()
    if not author:
        LOG.error("not found author, id: %s", author_id)
        return {}
    poetry_obj = Poetry(author_id=author_id)
    author_headimg = author['headimg']
    author_name = author['name']
    author_desc = author['description']
    total = author['total']
    poetrys = poetry_obj.find_poetry_by_author_id(page, count)
    result = []
    for poetry in poetrys:
        tmp_data = ship_poetry_list(poetry)
        result.append(tmp_data)
    author_info = {
        'author_name': author_name,
        'author_headimg': author_headimg,
        'author_desc': author_desc,
        'author_total': total,
        'author_id': author_id}
    return {'poetry_list': result, 'author_info': author_info}


@register_tab("author")
def get_authors(page, count):
    author_obj = Author()
    authors = author_obj.find_authors({}, page, count)
    ret_data = []
    for author in authors:
        desc = author['description']
        _id = author['id']
        headimg = author['headimg']
        total = author['total']
        dynasty = author['dynasty']
        name = author['name']
        tmp = {
            'desc': desc,
            'author_id': _id,
            'headimg': headimg,
            'total': total,
            'dynasty': dynasty,
            'name': name
        }
        ret_data.append(tmp)
    return ret_data


@register_tab('sen_daily')
def get_daily_sentence(page, count):
    sen_ins = SentenceDaily()
    data = sen_ins.list_sentences({}, page, count)
    result = []
    for sen in data:
        result.append(ship_list_sentence(sen))
    return result


def ship_list_sentence(sen_data):
    ret = {}
    ret['id'] = sen_data['id']
    ret['banner'] = sen_data['banner']
    ret['likes'] = sen_data['likes']
    ret['content'] = sen_data['content_en']
    ret['translate'] = sen_data['content_cn']
    ret['note'] = sen_data['note']
    return ret


@register_tab("recommend")
def get_recommend(page, count, author_id=None):
    condition = {}
    if author_id:
        condition.update({'author_id': author_id})
    poetry_obj = Poetry()
    poetries = poetry_obj.find_poetry(condition, page, count, {'likes': -1})
    ret_data = []
    for poetry in poetries:
        tmp_data = ship_poetry_list(poetry)
        ret_data.append(tmp_data)
    return ret_data


def web_recommend(author_id=None, page=1, count=20):
    handler = TAB_HANDLERS['recommend']
    poetry_list = handler(page, count, author_id)
    return poetry_list


def get_recommend_count(author_id=None):
    condition = {}
    if author_id:
        condition.update({'author_id': author_id})
    poetry_obj = Poetry()
    return poetry_obj.count(condition)


@register_tab("poetry")
def get_poetry(page, count):
    poetry_obj = Poetry()
    poetries = poetry_obj.find_poetry({}, page, count)
    ret_data = []
    for poetry in poetries:
        tmp_data = ship_poetry_list(poetry)
        ret_data.append(tmp_data)
    return ret_data


@register_tab("famous")
def get_famous(page, count):
    sent_obj = Sentence()
    sents = sent_obj.find_sentence_by_cond({}, page, count)
    result = []
    authors = []
    for sentence in sents:
        authors.append(sentence['author_id'])
        sentence_data = ship_sentence(sentence)
        result.append(sentence_data)

    author_obj = Author()
    author_map = {}
    authors = author_obj.find_authors({"id": authors}, 1, count)
    for author in authors:
        author_id = author['id']
        author_map[author_id] = author
    for sentence_data in result:
        author_id = sentence_data.pop("author_id", '')
        sentence_data['author'] = ''
        sentence_data['dynasty'] = ''
        author_info = author_map.get(author_id)
        if author_info:
            sentence_data['author'] = author_info['name']
            sentence_data['dynasty'] = author_info['dynasty']
    return result


@register_tab("ancient")
def get_ancient(page, count):
    return []


def get_poetry_detail_web(poetry_id, u_data=None):
    try:
        poetry_id = int(poetry_id)
    except ValueError:
        return False, u"poetry id格式错误"
    poetry_obj = Poetry(id=poetry_id)
    poetry = poetry_obj.find_poetry_by_id()
    if not poetry:
        return False, u"找不到诗词记录"
    ret_data = {}
    ret_data['id'] = poetry['id']
    ret_data['title'] = poetry['title']
    ret_data['dynasty'] = poetry['dynasty']
    ret_data['author'] = poetry['author']
    ret_data['content'] = poetry['content'].replace("\n", "<br/>")
    ret_data['keywords'] = poetry['tags'].split('&')
    ret_data['translate'] = poetry['translate'].replace("\n", "<br/>")
    ret_data['banner'] = poetry['banner']
    ret_data['author_id'] = poetry['author_id']
    ret_data['appreciation'] = poetry['shangxi'].replace("\n", "<br/>")
    ret_data['likes'] = poetry['likes']
    return True, ret_data


def get_poetry_detail(session_data, poetry_id, from_uid=None):
    LOG.info(
        "openid: %s, poetry_id: %s, time: %s",
        session_data['openid'],
        poetry_id, time.time())
    try:
        poetry_id = int(poetry_id)
    except ValueError:
        return False, u"poetry id格式错误"
    poetry_obj = Poetry(id=poetry_id)
    poetry = poetry_obj.find_poetry_by_id()
    if not poetry:
        return False, u"找不到诗词记录"
    openid = session_data['openid']
    user_history = UserBrowseHistory(openid=openid, poetry_id=poetry_id)
    history_record = user_history.check_browse()
    ret_data = {}
    if history_record:
        user_history.id = history_record['id']
        user_history.inc_times()
        if history_record['operation'] == PoetryOp.LIKE.value:
            ret_data['like'] = 1
        elif history_record['operation'] == PoetryOp.DISLIKE.value:
            ret_data['dislike'] = 1
    else:
        user_history.save()
    ret_data['id'] = poetry['id']
    ret_data['title'] = poetry['title']
    ret_data['dynasty'] = poetry['dynasty']
    ret_data['author'] = poetry['author']
    ret_data['content'] = poetry['content']
    ret_data['keywords'] = poetry['tags'].split('&')
    ret_data['translate'] = poetry['translate']
    ret_data['banner'] = poetry['banner']
    ret_data['author_id'] = poetry['author_id']
    ret_data['appreciation'] = poetry['shangxi']
    ret_data['likes'] = poetry['likes']
    ret_data['audio_url'] = poetry.get('voice_url', '')
    return True, ret_data


def ship_sentence(sentence):
    title = sentence['title']
    content = sentence['content']
    likes = sentence['likes']
    banner = sentence['banner']
    poetry_id = sentence['poetry_id']
    author_id = sentence['author_id']
    sentence_data = {
        "title": title,
        'content': content,
        'likes': likes,
        'poetry_id': poetry_id,
        'banner': banner,
        'author_id': author_id,
        'id': sentence['id']
    }
    return sentence_data


def ship_poetry_list(poetry):
    poetry_data = {}
    title = poetry['title']
    content = poetry['content']
    author = poetry['author']
    likes = poetry['likes']
    dynasty = poetry['dynasty']
    poetry_id = poetry['id']
    if not isinstance(content, unicode):
        content = unicode(content, 'utf-8')[:40]
        content = content.encode("utf-8")
    poetry_data = {
        'title': title,
        'content': content,
        'author': author,
        'likes': likes,
        'dynasty': dynasty,
        'poetry_id': poetry_id,
        'banner': poetry['banner']
    }
    return poetry_data


def get_recommend_poetry():
    poetry_instance = Poetry()
    condition = {'likes': {">=": 500}}
    pages = 54
    count = 10
    page = random.randint(1, pages - 1)
    poetries = poetry_instance.find_poetry(condition, page, count)
    total = len(poetries)
    if total == 0:
        poetry_instance.id = 1
        return poetry_instance.find_poetry_by_id()
    index = random.randint(0, total - 1)
    return poetries[index]


def send_random_poetry(openid):
    poetry_data = get_recommend_poetry()
    if not poetry_data:
        return None
    author = poetry_data['author']
    title = poetry_data['title']
    poetry_id = poetry_data['id']
    banner = poetry_data['banner']
    if not banner:
        banner = random.choice(os.listdir(BANNER_SAMP))
        banner = os.path.join(BANNER_SAMP, banner)
    appid = XCX_APPID
    page = "pages/detail/detail?id={}".format(poetry_id)
    title = title + '-' + author
    return send_miniapp(openid, appid, title, page, banner)


def get_search_data():
    handlers = {
        'author': search_example_author
    }
    result = []
    for item in SearchCat:
        name = item.name
        handler = handlers.get(name)
        if handler and callable(handler):
            result.append(handler(12))
    return result


def search_by_cat(cat_id, sub_id, page, count):
    search_enum = SearchCat(cat_id)
    handlers = {'author': search_author}
    return handlers.get(search_enum.name)(sub_id, page, count)


def search_author(author_id, page, count):
    poetry_instance = Poetry(author_id=author_id)
    cond = {'author_id': author_id}
    poetry_data = poetry_instance.find_poetry(cond, page, count)
    result = []
    for poetry in poetry_data:
        result.append(ship_poetry_list(poetry))
    return result


def search_example_author(count):
    # random_start = random.randint(101, 1000)
    # cond = {'total': {'>=': random_start}}
    author_instance = Author()
    authors = author_instance.find_authors({}, 1, count)
    data = {'id': 1, 'name': u'作者'}
    data_list = []
    for author in authors:
        data_list.append({
            'author_name': author['name'],
            'author_id': author['id'],
            'total': author['total']})
    data['data'] = data_list
    return data


def everyday_sentence(session_data, date_str):
    if not date_str:
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
    sen_instance = SentenceDaily(date_str=date_str, type=1)
    sen_data = sen_instance.get_one_sentence()
    ret_data = {}
    if sen_data:
        ret_data = ship_every_detail(sen_data)
    return ret_data


def ship_every_list(sen_data):
    ret_data = {}
    ret_data['banner'] = sen_data['banner']
    ret_data['likes'] = sen_data['likes']
    ret_data['date_str'] = sen_data['date_str']
    ret_data['content'] = sen_data['content_en']
    ret_data['id'] = sen_data['id']
    return ret_data


def ship_every_detail(sen_data):
    ret_data = {}
    ret_data['banner'] = sen_data['banner']
    ret_data['content'] = sen_data['content_en']
    ret_data['translate'] = sen_data['content_cn']
    ret_data['date_str'] = sen_data['date_str']
    ret_data['voice_url'] = sen_data['voice_url']
    ret_data['note'] = sen_data['note']
    ret_data['likes'] = sen_data['likes']
    ret_data['id'] = sen_data['id']
    return ret_data


def get_every_by_id(session_data, id, count, index=2):
    sen_instance = SentenceDaily(id=id)
    sen_data = sen_instance.get_one_sentence()
    ret_data = {}
    if sen_data:
        ret_data = ship_every_detail(sen_data)
    else:
        if count > 1:
            ret_data = []
        else:
            ret_data = {}
    if count > 1:
        date_str = ret_data.get('date_str')
        date_list = get_candicate_dates(date_str, count, index)
        sen_instance = SentenceDaily()
        sentences = sen_instance.list_sentences({'date_str': date_list})
        result = []
        for sen in sentences:
            date_list.remove(sen['date_str'])
            result.append(ship_every_detail(sen))
        if len(date_list) != 0:
            for date_str in date_list:
                result.append({'date_str': date_str, 'disabled': True})
        result.sort(key=lambda x: x['date_str'])
        return result
    return ret_data


def get_candicate_dates(date_str, count=5, index_cur=2):
    current = datetime.strptime(date_str, '%Y-%m-%d')
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    date_list = []
    after_count = count - index_cur - 1
    for index in range(after_count):
        tmp = current + timedelta(index + 1)
        if (tmp - today).days > 0:
            break
        else:
            count -= 1
            date_list.insert(0, tmp.strftime('%Y-%m-%d'))
    for index in range(count):
        tmp = current - timedelta(index)
        date_list.append(tmp.strftime('%Y-%m-%d'))
    return date_list


def recommend_everyday(session_data, exclude_ids, page, count):
    '''
    推荐句子

    Parameters:
        session_data -- 用户session，
        exclude_ids  -- 不需要的id，多个以逗号隔开
        page         -- 页码
        count        -- 每页个数
    '''
    sen_instance = SentenceDaily()
    exclude_ids = exclude_ids.split(',')
    exclude_ids = filter(lambda x: True if x else False, exclude_ids)
    if exclude_ids:
        exclude_ids = map(lambda x: int(x), exclude_ids)
        sentences = sen_instance.list_sentences(
            {'id': {'$nin': exclude_ids}}, page, count)
    else:
        sentences = sen_instance.list_sentences({}, page, count)
    result = []
    for sentence in sentences:
        tmp = ship_every_list(sentence)
        if tmp['id'] in exclude_ids:
            continue
        result.append(tmp)
    return result
