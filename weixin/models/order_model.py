# coding=utf-8

'''user model'''
import time
from enum import Enum
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField


class OrderStatus(Enum):
    '''order status'''
    NOTPAYED = 0
    EXPIRE = 7
    OK = 8


class Order(ModelBase):
    '''order object'''
    __table__ = 'orders'

    out_trade_no = StringField("out_trade_no", None)
    openid = StringField("openid", None)
    pay_type = StringField("pay_type", '')
    client_ip = StringField("client_ip", '')
    transaction_id = StringField("transaction_id", '')
    status = IntField("status", OrderStatus.NOTPAYED.value)
    total_fee = IntField("total_fee")
    body = StringField("body", '')
    update_time = IntField('update_time', int(time.time() * 1000))

    def save(self, commit=True):
        '''save order obj'''
        assert self.out_trade_no is not None and self.openid is not None \
            and self.total_fee is not None
        return self._save(self._data, commit)

    def update(self, update_data):
        assert self.out_trade_no
        condition = {'out_trade_no': self.out_trade_no}
        return self._update(condition, update_data)

    def find_one_order(self):
        assert self.out_trade_no
        condition = {'out_trade_no': self.out_trade_no}
        return self._find_one(condition)


class OrderDetail(ModelBase):
    '''order detail object'''
    __table__ = 'order_detail'
    __dbcon__ = None

    order_detail_id = IntField("order_detail_id")
    out_trade_no = StringField("out_trade_no")
    goods_id = IntField("goods_id")
    price = IntField("price")
    count = IntField("count")
    fee = IntField("fee")

    def save(self, commit=True):
        '''save order detail'''
        assert self.out_trade_no is not None and self.price is not None and \
            self.count is not None and self.fee is not None
        if self.order_detail_id is None:
            self._data.pop('order_detail_id')
        return self._save(self._data, commit)

    def get_detail(self):
        assert self.out_trade_no
        condition = {'out_trade_no': self.out_trade_no}
        return self._find(condition)
