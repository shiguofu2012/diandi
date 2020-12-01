#!/usr/bin/python
# coding=utf-8

import time
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField


class SearchKeyword(ModelBase):
    '''poetry object'''
    __table__ = 'search_keyword'

    id = IntField("id")
    keyword = StringField("keyword")
    created = IntField("created", int(time.time() * 1000))
    openid = StringField("openid", '')
    times = IntField('times', 0)

    def save(self):
        self._data.pop("id", '')
        return self._save(self._data)

    def check_search(self):
        assert self.keyword and self.openid
        condition = {
                "keyword": self.keyword,
                'openid': self.openid
                }
        return self._find_one(condition)

    def inc_times(self):
        assert self.id
        return self._increase(self.id, 'times')
