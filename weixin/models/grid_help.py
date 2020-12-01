# coding=utf-8

import time
from weixin.models import MONGO_DB
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField
from weixin.settings import LOGGER as LOG


class ShareInfo(ModelBase):
    __table__ = 'share'
    __dbcon__ = MONGO_DB

    uid = IntField("uid", None)                     # share user uid
    type = StringField("type", None)
    page = IntField("page", None)
    level = IntField("level", None)
    open_gid = StringField("open_gid", None)
    # times = IntField("times", None)
    created = IntField("created", None)
    notify = IntField("notify", None)

    def save_share(self):
        assert self.uid and self.page and self.type
        save_data = {}
        save_data['uid'] = int(self.uid)
        save_data['type'] = self.type
        save_data['page'] = self.page
        save_data['level'] = int(self.level)
        save_data['open_gid'] = self.open_gid
        save_data['created'] = int(time.time() * 1000)
        save_data['notify'] = self.notify or 0
        return self._save(save_data)

    def find_one(self):
        condition = {}
        keys = ("uid", "type", "page", "level", "open_gid")
        for key in keys:
            value = getattr(self, key)
            if key in ['uid', 'level']:
                value = int(value)
            if value:
                condition.update({key: value})
        data = self._find_one(condition)
        return data

    def notify_user(self):
        assert self.uid and self.level
        condition = {'uid': self.uid, 'level': self.level, "type": "help"}
        return self._update_multi(condition, {'notify': 1}, multi=True)


class ClickInfo(ModelBase):
    __table__ = "click"
    __dbcon__ = MONGO_DB

    openid = IntField("openid", None)        # click share app uid
    share_id = StringField("share_id", None)   # which share he click
    created = IntField("created", None)
    update_time = IntField("update_time", None)
    times = IntField("times", 0)

    def save(self):
        assert self.openid and self.share_id
        data = {
                "openid": self.openid,
                "share_id": self.share_id,
                "created": self.created,
                "update_time": self.update_time,
                "times": self.times
                }
        return self._save(data)

    def find_click(self):
        assert self.openid and self.share_id
        condition = {"openid": self.openid, "share_id": self.share_id}
        return self._find_one(condition)

    def update(self, update_data):
        assert self.openid and self.share_id
        condition = {"openid": self.openid, "share_id": self.share_id}
        return self._update(condition, update_data)

    def increase_times(self):
        assert self.openid and self.share_id
        condition = {"openid": self.openid, "share_id": self.share_id}
        return self._increase_condition(condition, 'times')


class HelpInfo(ModelBase):
    __table__ = "helper"
    __dbcon__ = MONGO_DB

    uid = IntField("uid", None)   # be helped user uid
    openid = StringField("openid", '')
    level = IntField("level", None)
    created = IntField("created", None)

    def save(self):
        assert self.uid and self.openid and self.level
        data = {
                "uid": self.uid,
                "openid": self.openid,
                "level": self.level,
                "created": self.created}
        return self._save(data)

    def find_one(self):
        assert self.uid and self.openid and self.level
        condition = {
                "uid": self.uid, "openid": self.openid, "level": self.level}
        return self._find_one(condition)
