# coding=utf-8

import json
import functools
import time
import base64
from PIL import Image
from StringIO import StringIO
from wechat.utils import dict_to_xml, random_str, WechatSigner
from wechat.crypto.base import PrpCrypto
from weixin.handler.base_handler import ModelBase, BaseChannel, TextMessage, \
        ImageMessage
from weixin.utils.metaclass import register_handler
from weixin.utils.httpclient import HttpClient
from weixin.utils.image_utility import upload_file_to_server
from weixin.models.fields import StringField
from weixin.views.widget_service import query_one_weather, query_poetry
from weixin.settings import AESKEY, TOKEN, LOGGER as LOG, XCX_APPID


SUPPORT_MESSAGE_TYPE = {}
MESSAGE_HANDLER = {}


class MiniappRaw(object):

    def __init__(self, raw_data):
        self._data = raw_data

    def get_user_instance(self):
        return MiniVisitor(**self._data)

    def get_channel_instance(self):
        return MiniChannel(**self._data)

    def get_message_instance(self):
        msg_class = SUPPORT_MESSAGE_TYPE.get(self._data['MsgType'])
        msg_instance = msg_class(**self._data)
        return msg_instance

    def event_handler(self):
        msg_type = self._data['MsgType']
        if msg_type != 'event':
            return {'errcode': -1, 'errmsg': "not event"}
        handler = MiniappEventHandler(
                self.get_message_instance(),
                self.get_user_instance(),
                self.get_channel_instance()
                )
        res = handler.process()
        return {'errcode': 0, 'errmsg': 'ok', 'data': res}


class MiniChannel(BaseChannel):

    cid = StringField("Appid")
    user_name = StringField("ToUserName")


class MiniVisitor(ModelBase):

    uid = StringField("FromUserName")
    nickname = StringField("NickName", '')
    headimg = StringField("Headimg", '')
    session_from = StringField("SessionFrom", '')


class BaseMiniMessage(ModelBase):

    def __init__(self, **kwargs):
        super(BaseMiniMessage, self).__init__(**kwargs)

    msg_id = StringField("MsgId")
    msg_type = StringField("MsgType")
    create_time = StringField("CreateTime")

    def get_common_data(self):
        return {
                "MsgId": self.msg_id,
                "MsgTyep": self.msg_type,
                "CreateTime": self.create_time
                }


@register_handler('text', SUPPORT_MESSAGE_TYPE)
class Text(BaseMiniMessage):

    content = StringField("Content")


@register_handler('image', SUPPORT_MESSAGE_TYPE)
class MiniImage(BaseMiniMessage):

    pic_url = StringField('PicUrl')
    media_id = StringField("MediaId", '')


class UnknowMessage(BaseMiniMessage):

    msg_type = 'text'
    content = u'不支持消息类型'


@register_handler("event", SUPPORT_MESSAGE_TYPE)
class Event(BaseMiniMessage):

    event_type = StringField("Event")
    cache_key = StringField("CacheKey")
    query = StringField("Query")
    scene = StringField("Scene")


class MiniappMessageHandler(object):

    def __init__(self, mini_message_instance, visitor, channel):
        self.message_instance = mini_message_instance
        self.visitor = visitor
        self.channel = channel

    def handler(self):
        extra_data = self.process()
        if extra_data is None:
            return
        common_data = self.message_instance.get_common_data()
        common_data.update(extra_data)
        return self.get_msg_instance(common_data)

    def process(self):
        return {}


@register_handler("text", MESSAGE_HANDLER)
class MiniappTextHandler(MiniappMessageHandler):

    def process(self):
        return {'content': self.message_instance.content}

    def get_msg_instance(self, msg_data):
        return TextMessage(**msg_data)


@register_handler("image", MESSAGE_HANDLER)
class MiniappImageHandler(MiniappMessageHandler):

    def process(self):
        return self.get_image_data()

    def get_image_data(self):
        url = self.message_instance.pic_url
        client = HttpClient()
        image_data = client.get(url)
        height, width = self.get_image_size(image_data)
        url = upload_file_to_server(image_data)
        return {'content': url, 'height': height, 'width': width}

    def get_image_size(self, image_data):
        sio = StringIO(image_data)
        image_file = Image.open(sio)
        return image_file.size

    def get_msg_instance(self, msg_data):
        return ImageMessage(**msg_data)


# @register_handler("event", MESSAGE_HANDLER)
class MiniappEventHandler(MiniappMessageHandler):

    def process(self):
        LOG.info(self.message_instance.msg_id)
        event_type = self.message_instance.event_type
        handler = MESSAGE_HANDLER.get(event_type)
        LOG.info("type: %s, handler: %s", event_type, handler)
        if handler:
            return handler(
                    self.message_instance,
                    self.visitor, self.channel).process()
        return

    @staticmethod
    def format_answer(func):
        @functools.wraps(func)
        def wrapper(self):
            answer = func(self)
            if not answer:
                return answer
            wechat_data = {
                    "ToUserName": self.visitor.uid,
                    "FromUserName": self.channel.user_name,
                    "CreateTime": int(time.time()),
                    "MsgType": "widget_data",
                    "Content": answer
                    }
            xml_data = dict_to_xml(wechat_data)
            aes_key = base64.b64decode(AESKEY + '=')
            cliper = PrpCrypto(aes_key, aes_key[:16])
            encrypted_msg = cliper.encrypt(xml_data, XCX_APPID)
            signer = WechatSigner()
            nonce = random_str(8)
            timestamp = str(int(time.time()))
            signer.add_data(encrypted_msg, nonce, timestamp, TOKEN)
            data = {
                    'Encrypt': encrypted_msg,
                    'MsgSignature': signer.signature,
                    'TimeStamp': timestamp,
                    'Nonce': nonce}
            return dict_to_xml(data)
        return wrapper


@register_handler("wxa_widget_data", MESSAGE_HANDLER)
class MiniappWidgetHandler(MiniappEventHandler):

    @MiniappEventHandler.format_answer
    def process(self):
        query = self.message_instance.query
        if isinstance(query, unicode):
            query = query.encode("utf-8")
        json_query = json.loads(query)
        query_type = json_query['type']
        slot_list = json_query['slot_list']
        lifespan = 800
        if query_type == 2:
            city = ''
            for slot in slot_list:
                key = slot['key']
                value = slot['value']
                if key == 'city':
                    city = value
                elif key == 'district':
                    city = value
            answer = query_one_weather(city)
        elif query_type == 43:
            query_dict = {}
            for slot in slot_list:
                key = slot['key']
                value = slot['value']
                query_dict[key] = value
            answer = query_poetry(query_dict)
            lifespan = 3600
        elif query_type == 15014:
            keyword = slot_list[0].get('value', '')
            answer = query_poetry({'author': keyword})
            lifespan = 3600
        else:
            return
        answer = json.dumps(answer, ensure_ascii=False)
        query = json.dumps(query, ensure_ascii=False)
        ret_data = {
                'lifespan': lifespan,
                'query': query, 'scene': 1, 'data': answer}
        return json.dumps(ret_data, ensure_ascii=False)
