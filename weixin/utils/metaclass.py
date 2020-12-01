# coding=utf-8

import copy


class ObjectDict(dict):

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


class FieldDescriptor(object):

    def __init__(self, field):
        self.field = field
        self.attr_name = field.name

    def __get__(self, instance, instance_type=None):
        if instance is not None:
            value = instance._data.get(self.attr_name)
            if value is None:
                value = copy.deepcopy(self.field.default)
                instance._data[self.attr_name] = value
            if isinstance(value, dict):
                value = ObjectDict(value)
            return value
        return self.field

    def __set__(self, instance, value):
        instance._data[self.attr_name] = value


def register_handler(msg_type, factory):
    def wrapper(cls):
        factory[msg_type] = cls
    return wrapper
