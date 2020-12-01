# coding=utf-8

from weixin.handler import MetaClass
from weixin.models.fields import StringField, IntField


class ModelBase(object):

    __metaclass__ = MetaClass

    _data = {}

    def __init__(self, **kwargs):
        for key, value in self.fields.items():
            field_name = self.fields_map.get(key)
            real_value = kwargs.get(field_name)
            if real_value is None:
                self._data[field_name] = value.default
            else:
                self._data[field_name] = real_value


class BaseVisitor(ModelBase):

    uid = StringField("uid")
    nickname = StringField("nickname")
    headimg = StringField("headimg")


class BaseChannel(ModelBase):

    cid = StringField("id")
    name = StringField("name", '')


class BaseMessage(ModelBase):

    msg_id = StringField("MsgId")
    msg_type = StringField("MsgType")
    create_time = StringField("CreateTime")


class TextMessage(BaseMessage):

    content = StringField("content")


class ImageMessage(BaseMessage):

    content = StringField("content")
    height = StringField("height")
    width = StringField("width")


class BaseMessageHandler(object):

    def __init__(self, visitor, channel, message):
        self.visitor = visitor
        self.channel = channel
        self.message = message
