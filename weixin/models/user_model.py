# coding=utf-8

'''user model'''
import time
from datetime import datetime
from weixin.models import MONGO_DB
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField
from weixin.utils.constants import PoetryOp


class GridFormId(ModelBase):

    __table__ = "formid"
    __dbcon__ = MONGO_DB

    appid = StringField("appid", '')
    openid = StringField("openid", '')
    formid = StringField("formid", '')
    created = IntField("created", 0)

    def save(self):
        assert self.openid and self.formid
        data = {
                "openid": self.openid,
                "formid": self.formid,
                "created": int(time.time() * 1000),
                "appid": self.appid,
                "enabled": 1}
        return self._save(data)

    def find_one(self):
        assert self.openid
        now = int(time.time() * 1000)
        start = (now - 7 * 86400 * 1000)
        condition = {
                "openid": self.openid,
                "created": {"$gte": start}, "enabled": 1}
        # LOCK
        record = self._find_one(condition)
        if record:
            self.disabled_form(record['_id'])
        return record

    def disabled_form(self, _id):
        condition = {"_id": _id}
        return self._update(condition, {'enabled': 0})


class NavDiandi(ModelBase):

    __table__ = 'diandi_user'
    __dbcon__ = MONGO_DB

    openid = StringField("openid", '')
    created = IntField("created", 0)

    def save(self):
        assert self.openid
        data = {"openid": self.openid, 'created': self.created}
        return self._save(data)

    def find_one(self):
        assert self.openid
        condition = {'openid': self.openid}
        return self._find_one(condition)


class User(ModelBase):
    '''user object'''
    __table__ = 'userinfo'

    id = IntField("id", 0)
    unionid = StringField("unionid", '')
    openid = StringField("openid", '')
    nickname = StringField("nickname", '')
    sex = IntField("sex", 0)
    headimgurl = StringField("headimgurl", '')
    language = StringField("language", 'zh_CN')
    country = StringField("country", '')
    province = StringField("province", '')
    city = StringField("city", '')
    created = IntField('created', int(time.time() * 1000))

    def find_by_openid(self):
        '''get user by user openid'''
        assert self.openid != ''
        return self._find_one({'openid': self.openid})

    def save_user(self):
        assert self.openid != ''
        self._data.pop("id", '')
        return self._save(self._data)

    def update_user(self, update_data):
        assert self.openid != '' and update_data
        condition = {'openid': self.openid}
        return self._update(condition, update_data)


class GridUser(User):

    credit = IntField("credit", 0)
    level = IntField("level", 1)
    new_buy = IntField("new_buy", 0)

    def answer_right(self):
        assert self.openid
        condition = {'openid': self.openid}
        return self._increase_condition(condition, 'level')

    def find_by_uid(self):
        assert self.id
        condition = {'id': self.id}
        return self._find_one(condition)

    def increase_credit(self, count):
        assert self.id or self.openid
        condition = {}
        if self.id:
            condition.update({'id': self.id})
        if self.openid:
            condition.update({'openid': self.openid})
        return self._increase_condition(condition, 'credit', count)


class MpUser(ModelBase):
    __table__ = 'userdata'
    __dbcon__ = MONGO_DB

    uid = StringField("uid", '')
    openid = StringField("openid", '')
    nickname = StringField("nickname", '')
    avatar = StringField("avatar", '')
    status = IntField("status", -1)
    login_time = IntField("login_time")

    def save_mpuser(self):
        assert self.uid and self.nickname and self.avatar and self.openid
        if self.get_user_by_openid():
            update_data = {
                    'nickname': self.nickname,
                    'avatar': self.avatar,
                    'status': self.status,
                    'uid': self.uid}
            if self.status == 0:
                update_data.update({'login_time': time.time()})
            cond = {'openid': self.openid}
            ret = self._update(cond, update_data)
        else:
            ret = self._save(self._data)
        return ret

    def get_user_by_uid(self):
        assert self.uid
        cond = {'uid': self.uid}
        return self._find_one(cond)

    def get_user_by_openid(self):
        assert self.openid
        cond = {'openid': self.openid}
        return self._find_one(cond)


class UserBrowseHistory(ModelBase):
    __table__ = 'user_history'

    id = IntField('id')
    openid = StringField("openid")
    poetry_id = IntField("poetry_id")
    created = IntField("created", int(time.time() * 1000))
    # 0 --- browse  1--- like -1 --- dislike
    operation = IntField("operation", PoetryOp.BROWSE.value)
    times = IntField("times", 1)
    qrcode = StringField("qrcode", '')

    def check_browse(self):
        assert self.openid and self.poetry_id
        condition = {'openid': self.openid, 'poetry_id': self.poetry_id}
        return self._find_one(condition)

    def save(self):
        self._data.pop("id", '')
        return self._save(self._data)

    def inc_times(self):
        assert self.id
        return self._increase(self.id, 'times')

    def user_operation(self, op_code):
        assert self.openid and self.poetry_id
        condition = {'openid': self.openid, 'poetry_id': self.poetry_id}
        update_data = {'operation': op_code}
        return self._update(condition, update_data)

    def get_user_history(self, page, count):
        assert self.openid
        condition = {'openid': self.openid}
        return self._find(condition, page, count, {'created': -1})

    def get_user_like(self, page, count):
        assert self.openid
        condition = {'openid': self.openid, 'operation': PoetryOp.LIKE.value}
        return self._find(condition, page, count, {'created': -1})

    def update_qrcode(self, qrcode_url):
        assert self.id or (self.openid and self.poetry_id)
        if self.id:
            condition = {'id': self.id}
        else:
            condition = {'openid': self.openid, 'poetry_id': self.poetry_id}
        update_data = {'qrcode': qrcode_url}
        return self._update(condition, update_data)

    def is_browsed(self, openid, poetry_id):
        cond = {'openid': openid, 'poetry_id': poetry_id}
        return self._find_one(cond)

    def get_today_history(self):
        today = datetime.now()
        today = datetime(today.year, today.month, today.day)
        stamp = time.mktime(today.timetuple()) * 1000
        cond = {'openid': self.openid, 'created': {'>=': stamp}}
        return self._find_one(cond)

    def get_sended_users(self, page, count):
        group_by_fields = ['openid']
        select_fields = ['openid', 'count(poetry_id) as recited', 'poetry_id']
        return self._group_by({}, group_by_fields, select_fields, page, count)
