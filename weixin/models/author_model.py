# coding=utf-8

'''poetry author model'''
import time
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField


class Author(ModelBase):
    '''author object'''
    __table__ = 'authors'

    id = StringField("id")
    name = StringField("name", None)
    description = StringField("description", None)
    headimg = StringField("headimg", None)
    total = IntField("total", 0)
    created = IntField("created", int(time.time() * 1000))
    dynasty = StringField('dynasty', None)
    poetry_link = StringField("poetry_link", '')

    def find_author_by_name(self):
        '''find author object by author name'''
        assert self.name
        cond = {'name': self.name}
        return self._find_one(cond)

    def find_author_by_id(self):
        assert self.id
        return self._find_one({'id': self.id})

    def save_author(self):
        '''save author data'''
        assert self.name and self.description and self.total is not None\
            and self.dynasty
        self._data.pop("id", '')
        return self._save(self._data)

    def find_authors(self, condition, page, count):
        return self._find(condition, page=page, count=count)
