# coding=utf-8

import copy
from weixin.utils.metaclass import FieldDescriptor
from weixin.models.fields import FieldBase


class MetaClass(type):
    '''database model base metaclass'''

    def __new__(mcs, name, bases, attrs):
        _fields_map = {}
        for base in bases:
            for attr_name, value in base.__dict__.items():
                if attr_name in attrs:
                    continue
                if isinstance(value, FieldDescriptor):
                    attrs[attr_name] = copy.deepcopy(value.field)
                    _fields_map[attr_name] = value.attr_name

        mcs = super(MetaClass, mcs).__new__(mcs, name, bases, attrs)
        _fields = {}
        for attr_name, value in attrs.items():
            if isinstance(value, FieldBase):
                setattr(mcs, attr_name, FieldDescriptor(value))
                _fields[attr_name] = value
                _fields_map[attr_name] = value.name
        setattr(mcs, 'fields', _fields)
        setattr(mcs, 'fields_map', _fields_map)
        return mcs
