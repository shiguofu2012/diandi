#!/usr/bin/python
# coding=utf-8


import time
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField


class Banner(ModelBase):
    '''poetry object'''
    __table__ = 'banner'

    id = IntField("id")
    page_path = StringField('page_path')
    created = IntField("created", int(time.time() * 1000))
    banner_url = StringField("banner_url", '')
    enabled = IntField("enabled", 0)
    appid = StringField("appid", '')

    def get_banner(self, enabled=1, page=1, count=50):
        condition = {}
        if enabled is not None:
            condition.update({"enabled": enabled})
        return self._find(condition, page=page, count=count)

    def count(self):
        return self._count({})

    def get_banner_by_id(self):
        assert self.id
        return self._find_one({"id": self.id})

    def update_banner_by_id(self, data):
        assert self.id
        cond = {"id": self.id}
        return self._update(cond, data)

    def save_banner(self, data):
        return self._save(data)

    def delete_banner(self):
        assert self.id
        cond = {"id": self.id}
        return self._delete_(cond)


class Tab(ModelBase):
    '''tab object'''
    __table__ = 'tab'

    id = IntField("id")
    created = IntField("created", int(time.time() * 1000))
    tab_icon = StringField("icon", '')
    enabled = IntField("enabled", 0)
    tab_name = StringField("name", '')
    tab_id = IntField("tab_id")

    def get_tab(self):
        condition = {'enabled': 1}
        return self._find(condition)


class FormId(ModelBase):
    '''user formid'''
    __table__ = 'formid'

    id = IntField("id")
    created = IntField("created", int(time.time() * 1000))
    openid = StringField("openid", '')
    enabled = IntField("enabled", 1)
    formid = StringField("formid", '')

    def save(self):
        assert self.openid and self.formid
        data = {}
        data['created'] = self.created
        data['openid'] = self.openid
        data['enabled'] = self.enabled
        data['formid'] = self.formid
        return self._save(data)

    def get_one_formid(self):
        assert self.openid
        condition = {'openid': self.openid, 'enabled': 1}
        record = self._find_one(condition)
        if not record:
            return None
        self.disabled_formid(record['id'])
        return record

    def disabled_formid(self, _id):
        condition = {'id': _id}
        return self._update(condition, {'enabled': 0})

    def get_sended_formids(self, page, count):
        condition = {'enabled': 1}
        group_by_fields = ['openid']
        ret_fields = ['openid', 'min(formid) as formid']
        return self._group_by(
                condition, group_by_fields, ret_fields, page, count)
