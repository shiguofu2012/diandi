#!/usr/bin/python
# coding=utf-8
import time
from datetime import datetime, timedelta
from weixin.utils.httpclient import HttpClient
from weixin.models.poetry_model import SentenceDaily
from weixin.settings import LOGGER as LOG

URL = 'http://open.iciba.com/dsapi/?date={}'


def get_sentence(date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    url = URL.format(date_str)
    client = HttpClient()
    res = client.get(url)
    data = ship_kingdata(res)
    data['date_str'] = date_str
    return data


def ship_kingdata(data):
    ret = {}
    now = int(time.time() * 1000)
    ret['content_en'] = data['content']
    ret['content_cn'] = data['note']
    ret['note'] = data['translation']
    ret['created'] = now
    ret['banner'] = data['picture2']
    ret['tags'] = ''
    ret['voice_url'] = data['tts']
    if data['tags']:
        tag_list = map(lambda x: x['name'] if x['name'] else '', data['tags'])
        tag_list = filter(lambda x: x, tag_list)
        ret['tags'] = ''.join(tag_list)
    ret['likes'] = int(data['love'])
    ret['type'] = 1
    return ret


def crawler(date_str=None):
    if date_str is None:
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
    sen_instance = SentenceDaily(**{'date_str': date_str, 'type': 1})
    if sen_instance.get_one_sentence():
        LOG.info('date: %s already exists', date_str)
        return
    sen_data = get_sentence(date_str)
    sen_instance = SentenceDaily(**sen_data)
    succ, ret = sen_instance.save_data()
    if succ:
        LOG.info('save sentence: %s, ret: %s', date_str, ret)
    else:
        LOG.error('save sentence: %s, error: %s', date_str, ret)


def init():
    days = 100
    today = datetime.now()
    for i in range(days):
        crawler(today.strftime('%Y-%m-%d'))
        today = today - timedelta(1)


if __name__ == '__main__':
    # init()
    crawler()
