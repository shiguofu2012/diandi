# coding=utf-8
# !/usr/bin/python
'''
real action of wechat push message;
'''

import base64
import xmltodict
from wechat.messages.events import EVENTS_TYPE
from wechat.messages.replies import TextReply, EmptyReply
from wechat.messages.message import MESSAGE_TYPES, UnknownMessage
from wechat.crypto.base import PrpCrypto
from wechat.utils import WechatSigner
from weixin.handler.mini_handler import MiniappRaw
from weixin.views.do_goods import find_goods_info
from weixin.views.poetry import send_random_poetry
from weixin.views.userdata import login_ok
from weixin.settings import LOGGER
from weixin.utils.hust_mp_constant import GOODS_INFO, DEFAULT_MSG, \
    SUBSCRIBE_MSG, UNSUBSCRIBE_MSG, MY_MSG, GOODS_NOT_EXISTS


MESSAGE_HANDLER = {}


def register_handler(message_type):
    '''register decorater'''
    def register(cls):
        '''register message type to MESSAGE_HANDLER'''
        MESSAGE_HANDLER[message_type] = cls
        return cls
    return register


@register_handler("text")
class TextHandler(object):
    '''handler user send text content'''
    def __init__(self, message_type):
        self.message_type = message_type

    @property
    def reply(self):
        '''text handler'''
        content = self.message_type.content
        goods_info = find_goods_info(content)
        if goods_info:
            price = goods_info.get('price', 0)
            coupon_amount = goods_info.get('coupon_amount', 0)
            title = goods_info.get('title', '')
            fan = (price - coupon_amount) * int(float(
                    goods_info.get("profit_rate", 0))) / 100.0 * 20 / 100.0
            fan = round(int(fan * 100) / 100.0, 2)
            tpw = goods_info.get('tpw')
            succ_goods = price is not None and coupon_amount is not None \
                and tpw is not None
            if succ_goods:
                msg = GOODS_INFO % (title, price, coupon_amount, fan, tpw)
                return TextReply(message=self.message_type, content=msg)
            return TextReply(message=self.message_type, content=GOODS_NOT_EXISTS)
        return TextReply(
            message=self.message_type,
            content=DEFAULT_MSG)


@register_handler("image")
class ImageHandler(object):
    '''handler image message'''
    def __init__(self, message_type):
        self.message_type = message_type

    @property
    def reply(self):
        '''reply content'''
        print self.message_type.media_id
        return TextReply(message=self.message_type, content=SUBSCRIBE_MSG)


@register_handler("voice")
class VoiceHandler(object):
    '''handler voice pushed message'''
    def __init__(self, message_type):
        self.message_type = message_type

    @property
    def reply(self):
        '''voice reply content'''
        return TextReply(message=self.message_type, content=u"带我听来")


@register_handler("video")
class VideoHandler(object):
    '''handler video pushed message'''
    def __init__(self, message_type):
        self.message_type = message_type

    @property
    def reply(self):
        '''reply conent'''
        print self.message_type.media_id
        print self.message_type.thumb_media_id
        return TextReply(message=self.message_type, content=u'还有视频')


@register_handler("subscribe")
class SubscribeHandler(object):
    '''handle user subscribe message'''
    def __init__(self, event_obj):
        self.event_obj = event_obj

    @property
    def reply(self):
        '''reply content'''
        if self.event_obj.key:
            login_ok(self.event_obj._data)
        return TextReply(message=self.event_obj, content=SUBSCRIBE_MSG)


@register_handler("unsubscribe")
class UnsubscribeHandler(object):
    '''handle unsubscribe message'''
    def __init__(self, event_obj):
        self.event_obj = event_obj

    @property
    def reply(self):
        '''reply content'''
        return TextReply(message=self.event_obj, content=UNSUBSCRIBE_MSG)


@register_handler('event')
class EventHandler(object):
    '''mp event pushed'''
    def __init__(self, event_obj):
        self.event_obj = event_obj

    @property
    def reply(self):
        '''reply conent'''
        event = self.event_obj.event.lower()
        event_instance = EVENTS_TYPE.get(event)
        if event_instance is not None:
            # event_obj = event_handler(self.event_obj)
            event_msg_handler = MESSAGE_HANDLER.get(event)
            event_instance = event_instance(self.event_obj._data)
            if event_msg_handler:
                return event_msg_handler(event_instance).reply
        return EmptyReply(message=self.event_obj)


@register_handler("scan")
class ScanHandler(object):
    '''handle scan event'''
    def __init__(self, event_obj):
        self.event_obj = event_obj

    @property
    def reply(self):
        '''reply conent'''
        temp_key = self.event_obj.scene_id
        if temp_key:
            login_ok(self.event_obj._data)
        return EmptyReply(message=self.event_obj)
        # return TextReply(message=self.event_obj, content=ret_msg)


@register_handler("click")
class ClickHandler(object):
    '''handle click event'''
    def __init__(self, event_obj):
        self.event_obj = event_obj

    @property
    def reply(self):
        '''reply content'''
        event_key = self.event_obj.key
        LOGGER.info(event_key)
        if event_key == 'we':
            return TextReply(message=self.event_obj, content=MY_MSG)
        elif event_key == 'randomPoetry':
            ret = send_random_poetry(self.event_obj.source)
            LOGGER.info("send openid: %s, ret: %s", self.event_obj.source, ret)
        return EmptyReply(message=self.event_obj)


def process_push_v2(xml_data, appid):
    """
    reply message passive and return message;
    """
    if not xml_data:
        return
    message = xmltodict.parse(xml_data)['xml']
    message_type = message['MsgType'].lower()
    message_class = MESSAGE_TYPES.get(message_type, UnknownMessage)
    message_obj = message_class(message)
    ret = EmptyReply(message=message_obj)
    LOGGER.info(message_obj)
    message_handler_class = MESSAGE_HANDLER.get(message_obj.type)
    if message_handler_class is None:
        LOGGER.info("type: %s not found handler", message_obj.type)
    else:
        msg_handler_obj = message_handler_class(message_obj)
        ret = msg_handler_obj.reply
    return ret


def check_miniapp_sign(token, timestamp, nonce, signature):
    signer = WechatSigner()
    signer.add_data(token, timestamp, nonce)
    if signer.signature != signature:
        return False
    return True


def process_miniapp_push(xml_data, args, encoding_key, token):
    appid = args['appid']
    timestamp = args['timestamp']
    nonce = args['nonce']
    signature = args['signature']
    if not check_miniapp_sign(token, timestamp, nonce, signature):
        return {'errcode': -1, 'errmsg': "sign error"}
    message = xmltodict.parse(xml_data)['xml']
    LOGGER.info(message)
    encrypted_msg = message.get('Encrypt')
    if encrypted_msg:
        aes_key = base64.b64decode(encoding_key + '=')
        cliper = PrpCrypto(aes_key, aes_key[:16])
        decrypted_msg = cliper.decrypt(encrypted_msg, appid)
        data = xmltodict.parse(decrypted_msg)['xml']
    else:
        data = message
    handler = MiniappRaw(data)
    res = handler.event_handler()
    if res['errcode'] == 0 and res.get("data"):
        return res
    return {'errcode': 0, 'errmsg': 'ok'}
