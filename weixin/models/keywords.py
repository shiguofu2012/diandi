# coding=utf-8

from weixin.models import MONGO_DB
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField


class KeyWords(ModelBase):

    __table__ = 'keywords'
    __dbcon__ = MONGO_DB

    category_id = IntField("category_id")
    enabled = IntField("enabled", 1)
    word = StringField("word", '')

    def get_keywords(self, condition, page, count):
        condition.update({'enabled': self.enabled})
        return self._find_mongo(condition, page, count)
