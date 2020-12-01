# coding=utf-8
'''db model'''

import copy
import time
from weixin.utils.metaclass import FieldDescriptor
from weixin.models.fields import FieldBase, IntField
from weixin.models import MYSQL_DB as sqldb


class ModelMetaClass(type):
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

        table_name = attrs.get("__table__", None) or name
        db_conn = attrs.get("__dbcon__", None) or sqldb
        mcs = super(ModelMetaClass, mcs).__new__(mcs, name, bases, attrs)
        _fields = {}
        for attr_name, value in attrs.items():
            if isinstance(value, FieldBase):
                setattr(mcs, attr_name, FieldDescriptor(value))
                _fields[attr_name] = value
                _fields_map[attr_name] = value.name
        setattr(mcs, 'fields', _fields)
        setattr(mcs, 'fields_map', _fields_map)
        setattr(mcs, '__table__', table_name)
        setattr(mcs, '__dbcon__', db_conn)
        return mcs


class ModelBase(object):
    '''database object model base'''

    __metaclass__ = ModelMetaClass
    created = IntField("created", int(time.time() * 1000))

    def __init__(self, **kwargs):
        self._data = {}
        for key, value in self.fields.items():
            field_name = self.fields_map.get(key)
            real_value = kwargs.get(field_name)
            if real_value is None:
                self._data[key] = value.default
            else:
                self._data[key] = real_value

    def __repr__(self):
        _repr = "{klass}({name})".format(
            klass=self.__class__.__name__,
            name=repr(self._data)
            )
        return _repr

    def _find_one(self, condition):
        return self.__dbcon__.get_one(self.__table__, condition)

    def _find(self, condition, page=1, count=20, sort=None):
        return self.__dbcon__.get(
                self.__table__, condition, page, count, sort=sort)

    def _save(self, data, commit=True):
        return self.__dbcon__.insert(self.__table__, data, commit)

    def commit(self):
        return self.__dbcon__.commit()

    def rollback(self):
        return self.__dbcon__.return_error()

    def _update(self, condition, update_data):
        return self.__dbcon__.update(self.__table__, condition, update_data)

    def _update_multi(self, condition, update_data, multi=False):
        return self.__dbcon__.update(
                self.__table__, condition, update_data, multi=multi)

    def _increase(self, id, field, count=1):
        return self.__dbcon__.increase(
                self.__table__,
                {'id': id},
                field, count)

    def _increase_condition(self, condition, field, count=1):
        return self.__dbcon__.increase(self.__table__, condition, field, count)

    def _search(self, condition, page, count, fields=['*']):
        return self.__dbcon__.match_data(
                self.__table__,
                condition,
                fields,
                page, count)

    def _search_fulltext(self, keyword, page, count, fields):
        if not isinstance(keyword, unicode):
            keyword = unicode(keyword)
        return self.__dbcon__.search_poetry(keyword, page, count, fields)

    def _search_widget(self, keyword, page, count, fields, sort):
        if not isinstance(keyword, unicode):
            keyword = unicode(keyword)
        return self.__dbcon__.search_poetry_widget(
                keyword, page, count, fields, sort)

    def _rand_get(self, fields, page, count):
        return self.__dbcon__.random_get(
                self.__table__,
                fields,
                page,
                count
                )

    def _delete_(self, condition):
        return self.__dbcon__.delete(self.__table__, condition)

    def _delete(self, condition):
        return self.__dbcon__.remove(self.__table__, condition)

    def _find_mongo(self, condition, page=1, count=20, fields=[]):
        return self.__dbcon__.find(
                self.__table__, condition, fields, page, count)

    def _count(self, condition):
        return self.__dbcon__.count(self.__table__, condition)

    def _group_by(self, condition, group_by_fields, ret_fields, page, count):
        return self.__dbcon__.group_by(
                self.__table__, condition,
                group_by_fields, ret_fields, page, count)
