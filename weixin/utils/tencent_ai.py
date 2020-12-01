# coding=utf-8

import base64
import hashlib
import os
import time
import uuid
from urllib import quote
from weixin.utils.httpclient import HttpClient
from wechat.utils import random_str


class TencentAIBase(object):

    def __init__(self, appid, appsec):
        self.appid = appid
        self.appsec = appsec
        self.http_client = HttpClient()
        self.base_url = 'https://api.ai.qq.com/fcgi-bin'

    def get_sign(self, data):
        data['app_id'] = self.appid
        data['time_stamp'] = int(time.time())
        data['nonce_str'] = random_str(16)
        sorted_list = sorted(data.keys())
        sign_str = u''
        for param in sorted_list:
            sign_str += u'{}={}&'.format(param, quote(str(data[param])))
        sign_str += u'app_key={}'.format(self.appsec)
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    def do_get(self, url, data):
        sign = self.get_sign(data)
        data['sign'] = sign
        url = self.base_url + url
        return self.http_client.get(url, params=data)

    def do_post(self, url, data):
        sign = self.get_sign(data)
        data['sign'] = sign
        url = self.base_url + url
        return self.http_client.post(url, data=data, data_fromat='str')


class VoiceGen(TencentAIBase):

    def __init__(self, appid, appsec, path='/tmp'):
        super(VoiceGen, self).__init__(appid, appsec)
        self.speaker = 5
        self.voice_path = path

    def request(self, text, speed=100):
        data = {}
        data['speaker'] = 5
        data['format'] = 3
        data['volume'] = 10
        data['speed'] = speed
        data['aht'] = 0
        data['apc'] = 58
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        data['text'] = text
        res = self.do_post('/aai/aai_tts', data)
        if res['ret'] != 0:
            return {'errmsg': res.get('msg', ''), 'errcode': res['ret']}
        data = res['data']
        voice_content = data['speech']
        abpath = self._save_voice(voice_content)
        return {'errcode': 0, 'data': {'path': abpath}}

    def _save_voice(self, content):
        content = base64.b64decode(content)
        filename = uuid.uuid4().hex + '.mp3'
        abpath = os.path.join(self.voice_path, filename)
        with open(abpath, 'w') as _file:
            _file.write(content)
        return abpath
