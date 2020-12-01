# coding=utf-8

import random
import functools
import json
import hashlib
from weixin.cache import data_cache
from weixin.utils.weather import WEATHER_CLIENT as w_client
from weixin.utils.utils import unicode2utf
from weixin.settings import LOGGER as LOG
from weixin.models.poetry_model import Poetry
from weixin.models.author_model import Author


def cache_wrapper(func):

    @functools.wraps(func)
    def wrapper(params):
        key = params
        if isinstance(params, dict):
            key = json.dumps(params)
        elif isinstance(params, list):
            key = json.dumps(params)
        elif isinstance(params, unicode):
            key = params.encode("utf-8")
        key = hashlib.md5(key).hexdigest()
        cache_data = data_cache.get(key)
        if cache_data:
            data = json.loads(cache_data)
            data = unicode2utf(data)
            return data
        data = func(params)
        data_cache.set(key, json.dumps(data, ensure_ascii=False), 3600)
        return data
    return wrapper


@cache_wrapper
def query_poetry(query_dict):
    keyword = u','.join(query_dict.values())
    poetry_obj = Poetry(content=keyword)
    author_id = 1
    fields = [
            'id', 'title', 'author',
            'likes', 'author_id', 'content', 'dynasty']
    if 'name' in query_dict:
        poetry_list = poetry_obj.search_widget(
                1, 5, fields, sort={'likes': -1})
    elif 'content' in query_dict:
        poetry_list = poetry_obj.search_widget(
                1, 5, fields)
    elif 'author' in query_dict:
        author_obj = Author(name=keyword)
        author_data = author_obj.find_author_by_name()
        author_id = author_data['id']
        if author_data:
            poetry_obj.author_id = author_data['id']
            poetry_list = poetry_obj.find_poetry_by_author_id(1, 3)
        else:
            poetry_list = poetry_obj.search_widget(
                    1, 5, fields, sort={'likes': -1})
    else:
        poetry_list = poetry_obj.search_widget(
                1, 5, fields)
    title = ''
    desc = ''
    item_list = []
    LOG.info(len(poetry_list))
    poetry_list = list(poetry_list)
    poetry_list.sort(key=lambda x: x['likes'], reverse=True)
    for poetry in poetry_list:
        author = poetry['author']
        if not title:
            title = poetry['title']
            desc = poetry['dynasty'] + "·" + author
        content = poetry['content']
        pages = "/pages/detail/detail?id={}".format(poetry['id'])
        content = unicode(content, 'utf-8')
        content = content[:50].encode("utf-8")
        tmp = {'jump_url': pages, "content": content}
        if 'author' in query_dict:
            tmp.update({'title': poetry['title']})
        else:
            tmp.update({"jump_url": pages})
        item_list.append(tmp)
    data = {"errcode": 0, 'errmsg': "ok"}
    if 'author' in query_dict:
        LOG.info(author_id)
        data['jump_url'] = u"/pages/authorPoetry/authorPoetry?id="\
            u"{}".format(author_id).encode("utf-8")
    else:
        data['jump_url'] = u"/pages/search/search?keyword="\
            u"{}".format(keyword).encode("utf-8")
    data['title'] = title
    data['desc'] = desc
    data['item_list'] = item_list
    data['more_description'] = u"点击查看更多优美诗词".encode("utf-8")
    return data


def query_one_weather(city):
    weather_data = w_client.forecast_weather(city)
    if weather_data['errcode'] == 0:
        today_weather = _ship_one_weather(
                weather_data['data']['daily_forecast'])
        update = weather_data['data']['update']['loc']
        if isinstance(update, unicode):
            update += u"更新"
            update = update.encode("utf-8")
        else:
            update += u"更新".encode("utf-8")
        today_weather['update_time'] = update
        today_weather['jump_url'] = '/pages/detail/detail?id=1'
        return today_weather
    return {'err_code': -3, 'err_msg': "not found"}


def _ship_one_weather(daily_forecast):
    w_data = {}
    day_weather = daily_forecast[0]
    tmp_range = u"{}°~{}°".format(
            day_weather['tmp_min'], day_weather['tmp_max'])
    weather = day_weather['cond_txt_d']
    if isinstance(weather, unicode):
        weather = weather.encode("utf-8")
    if isinstance(tmp_range, unicode):
        tmp_range = tmp_range.encode("utf-8")
    cur_tmp = random.randint(
            int(day_weather['tmp_min']),
            int(day_weather['tmp_max']))
    wind = u"{} {}".format(day_weather['wind_dir'], day_weather['wind_sc'])
    wind = wind.encode("utf-8")
    w_data['temperature'] = cur_tmp
    w_data['condition'] = weather
    w_data['temperature_range'] = tmp_range
    w_data['wind_force'] = wind
    w_data['air_quality'] = u'67 优'.encode("utf-8")
    w_data['detail'] = u"今天天气良好，适宜出行".encode("utf-8")
    w_data['err_code'] = 0
    w_data['err_msg'] = 'ok'
    LOG.info(w_data)
    return w_data
