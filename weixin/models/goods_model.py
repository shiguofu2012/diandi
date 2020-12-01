# coding=utf-8

'''goods model'''
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField


class Goods(ModelBase):
    '''goods object'''
    __table__ = 'goods'

    id = IntField("id", None)
    name = StringField("name", None)
    description = StringField("description", None)
    price = IntField("price", None)
    feature = StringField("feature", None)
    sales = IntField("sales", None)
    enabled = IntField("enabled", None)
    count = IntField("count", 0)

    def find_by_id(self):
        """find goods by goods id"""
        assert self.id is not None
        return self._find_one({'id': self.id})

    def find_all(self):
        """get all goods"""
        return self._find({})
