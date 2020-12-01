#$coding=utf-8


class FieldBase(object):

    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def __repr__(self):
        _repr = "{klass}({name})".format(
            klass=self.__class__.__name__,
            name=repr(self.name)
            )
        return _repr


class StringField(FieldBase):

    def __init__(self, name, default=''):
        super(StringField, self).__init__(name, default)


class IntField(FieldBase):

    def __init__(self, name, default=0):
        super(IntField, self).__init__(name, default)


class ListField(FieldBase):

    def __init__(self, name, default=[]):
        super(ListField, self).__init__(name, default)


class DictField(FieldBase):

    def __init__(self, name, default={}):
        super(DictField, self).__init__(name, default)


class FloatField(FieldBase):

    def __init__(self, name, default=0):
        super(FloatField, self).__init__(name, default)
