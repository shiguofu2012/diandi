# coding=utf-8

from weixin.models import MONGO_DB
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField


class Category(ModelBase):
    __table__ = 'category'
    __dbcon__ = MONGO_DB

    id = IntField("id", None)
    name = StringField("name", None)
    recommend = IntField("recommend", None)

    def find_category_by_ids(self, ids):
        if not isinstance(ids, list):
            ids = [ids]
        condition = {'id': {'$in': ids}}
        return self._find_mongo(condition)

    def all_category(self, page=1, count=50):
        condition = {}
        if self.recommend is not None:
            condition.update({'recommend': self.recommend})
        return self._find_mongo(condition, page, count)

    def find_category_by_id(self):
        assert self.id
        return self._find_one({"id": self.id})

    def save_category(self):
        data = {'id': self.id, 'name': self.name}
        if self.recommend:
            data.update({'recommend': 1})
        ori_data = self.find_category_by_id()
        if ori_data:
            return ori_data['_id']
        return self._save(data)


class SubCategory(ModelBase):
    __table__ = 'sub_category'
    __dbcon__ = MONGO_DB

    id = IntField("id", None)
    parent = IntField("parent")
    name = StringField("name", "")

    def find_one(self):
        assert self.id
        return self._find_one({'id': self.id})

    def save_category(self):
        assert self.id and self.parent is not None
        data = {'id': self.id, "name": self.name, 'parent': self.parent}
        ori_data = self.find_one()
        if ori_data:
            return ori_data['id']
        return self._save(data)
