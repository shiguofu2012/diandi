# coding=utf-8

import time
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField


class Share(ModelBase):

    __table__ = 'share_info'
    id = IntField("id")
    openid = StringField("openid")
    open_gid = StringField("open_gid")
    page = StringField("page")
    created = IntField("created", int(time.time() * 1000))
    times = IntField("times", 0)
    op = StringField("op")
    type = StringField("type", "group")

    def save(self):
        assert self.openid and self.open_gid
        self._data.pop('id', '')
        return self._save(self._data)

    def find_share_by_openid(self, page, count):
        assert self.openid
        condition = {'openid': self.openid, "type": self.type}
        return self._find(condition, page, count)

    def check_share_info(self):
        assert self.openid and self.open_gid and self.page
        condition = {
                'openid': self.openid,
                'open_gid': self.open_gid,
                'page': self.page,
                'op': self.op}
        return self._find_one(condition)

    def inc_times(self):
        assert self.id
        return self._increase(self.id, 'times')
