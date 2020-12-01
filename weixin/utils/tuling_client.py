#!/usr/bin/python
# coding=utf-8

import random
from weixin.utils.httpclient import HttpClient
from weixin.settings import LOGGER


class TuringClient(object):

    API_KEY = ['14c218cb6cb23bb27b7dc89e18eb9689']
    _HTTP_CLIENT = None
    URL = 'http://openapi.tuling123.com/openapi/api/v2'
    DEFAULT_UID = '14c218cb6cb23bb27b7dc89e18eb9689'

    def __init__(self):
        self._HTTP_CLIENT = HttpClient()
        self.DEFAULT_REPLY = u"我还不太懂呢，我去学习啦:)"

    def _handle_result(self, resp):
        intent = resp.get("intent")
        if not intent:
            return self.DEFAULT_REPLY
        resp_code = intent.get("code")
        if resp_code in (5000, 6000):
            return self.DEFAULT_REPLY
        elif int(resp_code) / 1000 == 4:
            print("error resp: %s", resp)
            return self.DEFAULT_REPLY
        results = resp.get("results", [])
        return_msg = []
        for result in results:
            result_type = result.get('resultType', 'text')
            if result_type == 'text':
                return_msg.insert(0, result['values']['text'])
            elif result_type == 'url':
                return_msg.append(result['values']['url'])
            elif result_type == 'news':
                newses = result['values']['news']
                for news in newses:
                    detail_url = news['detailurl']
                    info = news['info']
                    tmp = info + '\n' + detail_url + '\n'
                    return_msg.append(tmp)
        return '\n'.join(return_msg)

    def query_text(self, content, uid=None, location=None):
        '''
        @parameter
        : param uid  --- userid
        : param location --- user location;{'city': '北京', 'province':'北京',
        'street': ''}
        '''
        if isinstance(content, unicode):
            content = content.encode("utf-8")
        req_data = {"reqType": 0}
        req_data['perception'] = {
            "inputText": {'text': content}}
        if location:
            req_data['perception'].update({'selfInfo': {'location': location}})
        req_data['userInfo'] = {
            'apiKey': random.choice(self.API_KEY),
            'userId': uid if uid else self.DEFAULT_UID}
        resp = self._HTTP_CLIENT.post(self.URL, json=req_data)
        LOGGER.info("turling query: %s, res: %s", content, resp)
        return self._handle_result(resp)


TURING_CLIENT = TuringClient()


if __name__ == '__main__':
    client = TuringClient()
    from datetime import datetime
    today = datetime.now()
    # ret = client.query_text(
    #         u"%s年%s月%s日阴历日期" % (today.year, today.month, today.day))
    ret = client.query_text("北京天气")
    print(ret)
