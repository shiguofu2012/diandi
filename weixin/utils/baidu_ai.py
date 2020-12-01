# coding=utf-8

import os
import uuid
from weixin.utils.httpclient import HttpClient
from weixin.cache import wx_cache


class BaiduAIBase(object):

    def __init__(self, appid, appsec):
        self.appid = appid
        self.appsec = appsec
        self.http_client = HttpClient()
        self.base_url = 'http://tsn.baidu.com'

    @property
    def token_key(self):
        return 'bdtoken_{}'.format(self.appid)

    def refresh_new_token(self):
        token_url = 'https://openapi.baidu.com/oauth/2.0/token'
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.appid,
            'client_secret': self.appsec
        }
        res = self.do_get(token_url, params)
        if 'error' in res:
            raise Exception('get token {} error {}'.format(token_url, res.get(
                'error_description', '')))
        token = res['access_token']
        expire = res.get('expires_in', 3600)
        wx_cache.set(self.token_key, token)
        wx_cache.expire(self.token_key, int(expire))
        return token

    @property
    def access_token(self):
        token = wx_cache.get(self.token_key)
        if token:
            return token
        return self.refresh_new_token()

    def do_get(self, url, data):
        if not url.startswith(('http', 'https')):
            url = self.base_url + url
        return self.http_client.get(url, params=data)

    def do_post(self, url, data):
        if not url.startswith(('http', 'https')):
            url = self.base_url + url
        return self.http_client.post(url, data=data, data_fromat='str')


class BaiduVoiceGen(BaiduAIBase):

    def __init__(self, appid, appsec, path='/tmp'):
        super(BaiduVoiceGen, self).__init__(appid, appsec)
        self.speaker = 5
        self.voice_path = path

    def request(self, text, speed=5):
        data = {}
        data['tok'] = self.access_token
        data['cuid'] = '123'
        data['ctp'] = 1
        data['lan'] = 'zh'
        data['spd'] = speed
        data['pit'] = 5
        data['vol'] = 5
        data['per'] = 0
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        data['tex'] = text
        res = self.do_post('/text2audio', data)
        if isinstance(res, dict) and res['ret'] != 0:
            return {'errmsg': res.get('msg', ''), 'errcode': res['ret']}
        abpath = self._save_voice(res)
        return {'errcode': 0, 'data': {'path': abpath}}

    def _save_voice(self, content):
        filename = uuid.uuid4().hex + '.mp3'
        abpath = os.path.join(self.voice_path, filename)
        with open(abpath, 'w') as _file:
            _file.write(content)
        return abpath
