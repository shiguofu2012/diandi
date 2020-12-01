# coding=utf-8

import time
from enum import Enum
from weixin.models import POETRY_DB
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField
from weixin.settings import LOG_MODEL as LOG


class Poetry(ModelBase):
    '''poetry object'''
    __table__ = 'poetry'

    id = IntField("id")
    title = StringField("title", None)
    content = StringField('content', None)
    created = IntField("created", int(time.time() * 1000))
    banner = StringField("banner", '')
    tags = StringField("tags", None)
    author_id = StringField("author_id", None)
    dynasty = StringField("dynasty")
    author = StringField("author")
    translate = StringField("translate")
    shangxi = StringField("shangxi")
    likes = IntField("likes")
    plink = StringField("plink")

    def save(self):
        self._data.pop("id", '')
        return self._save(self._data)

    def increase(self, count):
        assert self.id
        return self._increase(self.id, 'likes', count)

    def find_poetry(self, condition, page, count, sort=None):
        return self._find(condition, page=page, count=count, sort=sort)

    def count(self, condition):
        return self._count(condition)

    def find_poetry_by_id(self):
        assert self.id
        return self._find_one({'id': self.id})

    def find_poetry_by_title(self):
        assert self.title
        return self._find_one({'title': self.title})

    def find_poetry_by_author_id(self, page, count):
        assert self.author_id
        return self._find({'author_id': self.author_id}, page, count)

    def check_duplicate(self):
        assert self.title and self.author and self.content
        condition = {
            'title': self.title,
            'author': self.author,
            'content': self.content
        }
        return self._find_one(condition)

    def find_poetry_by_ids(self):
        assert self.id
        return self._find({'id': self.id})

    def search(self, page, count):
        assert self.author or self.content
        condition = {}
        # if self.author:
        #     condition.update({'author': self.author})
        # if self.content:
        condition.update({'content': self.content})
        # condition.update({'search_op': 'or'})
        fields = [
            'id', 'title', 'content', 'author',
            'dynasty', 'likes', 'banner']
        return self._search(condition, page, count, fields)

    def search_fulltext(self, page, count, fields=None):
        assert self.content
        return self._search_fulltext(self.content, page, count, fields)

    def search_widget(self, page, count, fields=[], sort=None):
        assert self.content
        return self._search_widget(self.content, page, count, fields, sort)

    def random_get(self, page, count):
        fields = [
            'id', 'title', 'content', 'banner', 'author', 'dynasty',
            'likes']
        return self._rand_get(fields, page, count)

    def update_poetry_by_id(self, update_data):
        assert self.id
        condition = {'id': self.id}
        return self._update(condition, update_data)


class SentenceType(Enum):
    POETRY = 0
    FAMOUS = 1


class Sentence(ModelBase):
    __table__ = 'sentence'

    id = IntField("id")
    # source title
    title = StringField("title", None)
    # the sentence
    content = StringField('content', None)
    created = IntField("created", int(time.time() * 1000))
    banner = StringField("banner", '')
    tags = StringField("tags", None)
    author_id = StringField("author_id", None)
    author = StringField("author")
    poetry_id = IntField("poetry_id")
    likes = IntField("likes", 0)
    type = IntField("type", SentenceType.POETRY.value)

    def find_by_content(self):
        assert self.content
        return self._find_one({'content': self.content})

    def find_by_id(self):
        assert self.id
        return self._find_one({'id': self.id})

    def save(self):
        ori_content = self.find_by_content()
        if ori_content:
            return ori_content['id']
        self._data.pop("id", '')
        LOG.debug("save centence: %s", self.content)
        return self._save(self._data)

    def find_sentence_by_cond(self, condition, page, count):
        return self._find(condition, page, count, sort={"likes": -1})

    def update_sentence_by_id(self, data):
        assert self.id
        condition = {'id': self.id}
        return self._update(condition, data)


class GridPoetry(ModelBase):
    '''poetry object'''
    __table__ = 'poetries'
    __dbcon__ = POETRY_DB

    answer = StringField("answer", '')
    author = StringField("author", '')
    dynasty = StringField("dynasty", '')
    enabled = IntField("enabled", 1)
    title = StringField("title", '')
    poetry = StringField("poetry", '')
    recited = IntField("recited", 1)
    level = IntField("level", 1)
    type = IntField("type", 1)

    def get_level_data(self):
        assert self.level
        cond = {
            'level': self.level,
            'enabled': self.enabled,
            'type': self.type}
        return self._find_one(cond)


class HintHistory(ModelBase):

    __table__ = 'hint_history'
    __dbcon__ = POETRY_DB

    word = StringField("word", '')
    index = IntField("index", None)
    openid = StringField("openid", '')
    level = IntField("level", None)
    created = IntField("created", 0)

    def get_hint_data(self):
        assert self.openid and self.level
        cond = {"openid": self.openid, 'level': self.level}
        return self._find_mongo(cond)

    def save_hint_data(self):
        data = {}
        LOG.info(self._data)
        assert self.word and self.index is not None and self.openid \
            and self.level
        data['word'] = self.word
        data['openid'] = self.openid
        data['level'] = self.level
        data['index'] = self.index
        data['created'] = int(time.time() * 1000)
        return self._save(data)


class SentenceDaily(ModelBase):
    __table__ = 'sentence_daily'

    id = IntField("id")
    # the English content
    content_en = StringField('content_en', None)
    content_cn = StringField('content_cn', None)
    note = StringField('note', None)
    created = IntField("created", int(time.time() * 1000))
    banner = StringField("banner", '')
    tags = StringField("tags", None)
    likes = IntField("likes", 0)
    type = IntField('type', None)
    voice_url = StringField('voice_url', None)
    date_str = StringField('date_str', '')

    def save_data(self):
        assert self.content_en or self.content_cn
        return self._save(self._data)

    def _build_cond(self):
        cond = {}
        if self.id:
            cond['id'] = self.id
        if self.date_str:
            cond['date_str'] = self.date_str
        if self.type:
            cond['type'] = self.type
        return cond

    def get_one_sentence(self):
        cond = self._build_cond()
        return self._find_one(cond)

    def list_sentences(self, condition, page=1, count=20, sort={'likes': -1}):
        cond = self._build_cond()
        if condition:
            cond.update(condition)
        return self._find(cond, page, count, sort=sort)
