# coding=utf-8

import time
from weixin.models import MONGO_DB
from weixin.models.base_model import ModelBase
from weixin.models.fields import IntField, StringField, ListField, FloatField
from weixin.utils.lucene_searcher import SEARCHER_LUCENE as searcher
from weixin.settings import LOG_MODEL as LOG


class TbkHotWord(ModelBase):

    __table__ = 'hot_words'
    __dbcon__ = MONGO_DB

    word = StringField("word")
    enabled = IntField("enabled", None)

    def all_hot_words(self):
        cond = {
                'enabled': 1 if self.enabled else 0
                }
        return self._find_mongo(cond)


class TbkConfig(ModelBase):
    __table__ = 'tbk_config'
    __dbcon__ = MONGO_DB

    key = StringField("key")
    start = IntField("start")
    end = IntField("end")
    desc = StringField("desc")
    switch = IntField("switch")
    proxy_end = IntField("proxy_end")
    phone = StringField("phone", '')
    api_key = IntField("api_key")
    api_sec = StringField("api_sec")
    pid = StringField("pid")

    def get_config_data(self):
        assert self.key
        cond = {'key': self.key}
        return self._find_one(cond)


class TbkMenuConfig(ModelBase):
    __table__ = 'tabs'
    __dbcon__ = MONGO_DB

    id = IntField("id")
    name = StringField("name")
    enabled = IntField("enabled")
    icon = StringField("icon")
    parent = IntField("parent")
    type = StringField("type")
    sort_tabs = ListField("sort_tabs")

    def get_parent_tab(self, parent_id=None, enabled=1):
        cond = {'enabled': enabled, 'parent': 0}
        if parent_id:
            cond.update({'_id': parent_id})
        return self._find_mongo(cond)

    def get_one_menu(self, mid):
        cond = {'_id': mid}
        return self._find_one(cond)

    def get_sort_tabs(self):
        sort_tabs = self.__dbcon__.find("sort_tabs", {}, count=100)
        sort_tab_dict = {}
        for tab in sort_tabs:
            _id = tab['_id']
            name = tab['name']
            sort_tab_dict[_id] = {'id': _id, "name": name}
        return sort_tab_dict

    def get_cond_tabs(self):
        cond_tabs = self.__dbcon__.find("cond_tabs", {})
        cond_tab_dict = {}
        for tab in cond_tabs:
            _id = tab['_id']
            name = tab['name']
            params = tab['params']
            tmp = {'id': _id, 'name': name, 'params': params}
            cond_tab_dict[_id] = tmp
        return cond_tab_dict

    def _ship_sort_tab(self, sort_ids, sort_tab_dict):
        data = []
        for sort_id in sort_ids:
            sort_config = sort_tab_dict.get(sort_id)
            if not sort_config:
                continue
            data.append(sort_config)
        return data

    def get_sub_menu(self, parent=None):
        if parent:
            cond = {'parent': parent}
        else:
            cond = {'parent': {'$ne': 0}}
        cond.update({'enabled': 1})
        cats = self._find_mongo(cond, count=100)
        result_dict = {}
        for cat in cats:
            parent = cat['parent']
            tmp = {'id': cat['_id'], 'name': cat['name'], 'icon': cat['icon']}
            result_dict.setdefault(parent, [])
            result_dict[parent].append(tmp)
        return result_dict

    def get_config_tabs(self, enabled=1):
        result = {}
        sort_tab_dict = self.get_sort_tabs()
        cond_tab_dict = self.get_cond_tabs()
        parent_tabs = self.get_parent_tab()
        sub_cat = self.get_sub_menu()
        for tab in parent_tabs:
            _type = tab.get("type", '')
            if not _type:
                continue
            result.setdefault(_type, [])
            tmp = {"name": tab['name'], 'id': tab['_id'], 'icon': tab['icon']}
            sort_tab = self._ship_sort_tab(tab.get('sort_tabs', []), sort_tab_dict)
            cond_tab = self._ship_sort_tab(
                    tab.get("cond_tabs", []),
                    cond_tab_dict)
            _id = tab['_id']
            cats = sub_cat.get(_id, [])
            result[_type].append({
                'parent': tmp, 'tabs': sort_tab, 'cats': cats,
                'condition': cond_tab})
        for _type, data in result.items():
            data.sort(key=lambda x: x['parent']['id'])
        return result


class TbkBanner(ModelBase):
    __table__ = 'banner'
    __dbcon__ = MONGO_DB

    image = StringField("img", '')
    url = StringField("url", '')
    open_type = StringField("open_type", '')
    enabled = IntField("enabled", 1)

    def get_banners(self, enabled=1):
        cond = {'enabled': enabled}
        banners = self._find_mongo(cond)
        result = []
        for banner in banners:
            result.append({
                "url": banner['url'],
                'open_type': banner['open_type'],
                'img': banner['img'],
                'id': str(banner['_id'])})
        return result


class TbkGoods(ModelBase):
    __table__ = 'goods'
    __dbcon__ = MONGO_DB

    coupon_total_count = IntField("coupon_total_count", 0)
    coupon_info = StringField("coupon_info", '')
    is_tmall = IntField("is_tmall", 0)
    end = StringField("end", '')
    start = StringField("start", '')
    created = IntField("created", int(time.time() * 1000))
    small_images = ListField("small_images", [])
    sales = IntField("sales", 0)
    num_id = IntField("num_id", 0)
    coupon_id = StringField("coupon_id", '')
    coupon_start = IntField("coupon_start", 0)
    coupon_share_url = StringField("coupon_share_url", '')
    price = FloatField("price")
    coupon_amount = IntField("coupon_amount")
    category_id = IntField("category_id")
    category_name = StringField("category_name")
    commssion_rate = FloatField("commssion_rate")
    pic_url = StringField("pic_url")
    title = StringField("title")
    coupon_remain = IntField("coupon_remain")
    update_time = IntField("update_time", int(time.time() * 1000))
    coupon_expire = IntField("coupon_expire", 0)
    similar_goods = ListField("similar_goods", [])
    source = StringField("source", "")
    coupon_fee = FloatField("coupon_fee", 0)
    sub_category_id = IntField("sub_category_id")
    sub_category_name = StringField("sub_category_name", '')
    mid = IntField("mid", 0)

    def find_goods_by_id(self):
        cond = {'num_id': self.num_id}
        return self._find_one(cond)

    def update(self, update_data):
        assert self.num_id
        cond = {"num_id": self.num_id}
        return self._update(cond, update_data)

    def delete(self):
        assert self.num_id
        return self._delete({'num_id': self.num_id})

    def disabled_goods_by_id(self):
        assert self.num_id
        cond = {'num_id': self.num_id}
        update_data = {'coupon_expire': 1}
        LOG.info("disabled goods: %s", self.num_id)
        searcher.delete_index(self.num_id)
        return self._delete(cond)

    def check_save(self):
        coupon_amount = float(self.coupon_amount)
        price = float(self.price)
        coupon_fee = price - coupon_amount
        if coupon_fee <= 0:
            return False
        if coupon_amount / coupon_fee >= 0.1:
            return True
        return False

    def find_goods_by_cond(self, condition, page, count, fields=[]):
        return self._find_mongo(condition, page, count, fields)

    def count(self, condition):
        return self._count(condition)

    def save(self):
        assert self.num_id and self.coupon_total_count is not None and self.price and\
            self.title and self.coupon_amount is not None
        old_goods = self.find_goods_by_id()
        if old_goods:
            ret = old_goods['_id']
            update_data = self._get_update_data(old_goods)
            update_data.update(
                    {
                        'update_time': int(time.time() * 1000),
                        'coupon_expire': 0})
            ret = self.update(update_data)
            LOG.info(
                    "update goods: %s, data: %s, ret: %s",
                    self.num_id,
                    update_data, ret)
        else:
            ret = self._save(self._data)
            LOG.info("save goods: %s, id: %s", ret, self.num_id)
        return str(ret)

    def _get_update_data(self, old_data):
        change_keys = (
                "coupon_total_count", "coupon_info", "is_tmall", "end",
                "start", "sales", "coupon_id", "coupon_start",
                "coupon_share_url", "price", "coupon_amount", "category_id",
                "category_name", "commssion_rate", "title", "coupon_remain",
                "sub_category_id")
        update_data = {}
        for key in change_keys:
            old_value = old_data.get(key)
            new_value = getattr(self, key)
            if new_value and old_value != new_value:
                update_data[key] = new_value
        return update_data
