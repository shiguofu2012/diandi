# coding=utf-8
'''
order operation;
'''
import uuid
from weixin.settings import LOGGER
from weixin.models.goods_model import Goods
from weixin.models.order_model import Order, OrderDetail


def get_goods_msg(gid):
    '''
    get goods by goods id;
    '''
    goods_obj = Goods(id=gid)
    return goods_obj.find_by_id()


def gen_out_trade_no():
    '''generate order id'''
    return uuid.uuid4().hex


def place_order_by_gid(gid, count, user_openid, pay_type):
    '''
    place order by goods id and count;
    '''
    goods = get_goods_msg(gid)
    if not goods:
        LOGGER.info("gid: %s not found, user: %s", gid, user_openid)
        return {}, u"无效的gid"
    price = goods['price']
    desc = goods['description']
    total_fee = price * count
    order_obj = Order()
    order_obj.openid = user_openid
    order_obj.pay_type = pay_type
    order_obj.total_fee = total_fee
    order_obj.body = desc
    out_trade_no = gen_out_trade_no()
    order_obj.out_trade_no = out_trade_no

    order_detail_obj = OrderDetail()
    order_detail_obj.out_trade_no = out_trade_no
    order_detail_obj.goods_id = gid
    order_detail_obj.price = price
    order_detail_obj.count = count
    order_detail_obj.fee = total_fee
    # start transaction mysql

    order_succ, order_msg = order_obj.save(False)
    detail_succ, detail_msg = order_detail_obj.save(False)
    if not order_succ or not detail_succ:
        order_obj.rollback()
        if not order_succ:
            LOGGER.info(order_msg)
        if not detail_succ:
            LOGGER.info(detail_msg)
        return {}, []
    else:
        order_obj.commit()
        return order_obj, [order_detail_obj]


def place_order_by_goods(goods_list):
    pass
