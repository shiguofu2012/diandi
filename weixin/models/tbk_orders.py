# coding=utf-8

from weixin.models import MONGO_DB
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField, ListField, FloatField
from weixin.settings import LOG_MODEL as LOG


class TbkOrder(ModelBase):
    __table__ = 'orders'
    __dbcon__ = MONGO_DB

    order_id = IntField("order_id")   # 订单id
    goods_id = IntField("goods_id")   # 商品id
    count = IntField("count")         # 商品个数
    creatd = StringField("created", '')  # 同步订单的时间
    goods_title = StringField("title", '')  # 商品标题
    order_status = StringField("order_status", '')  # 订单状态
    paid_fee = FloatField("paid_fee", 0)        # 实际支付金额
    expect_fee = FloatField("expect_fee", 0)  # 效果预估,
    income_fee = FloatField("income_fee", 0)  # 实际结算金额
    income_time = StringField("income_time", '')   # 结算时间
    comm_rate = FloatField("comm_rate", 0)    # 佣金比例
    created_time = StringField("created_time", '')  # 订单创建时间
    pid = StringField("pid", '')              # 订单所属的pid
    uid = StringField("uid", '')              # 订单属于哪个用户
    status = IntField("status", 0)    # 订单在本系统中的状态，如是否累加到用户结算
