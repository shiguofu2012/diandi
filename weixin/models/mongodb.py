#!/usr/bin/python
# coding=utf-8

import pymongo
import time
from weixin.settings import LOGGER as LOG


class MongoDB(object):
    def __init__(self, mongo_uri, dbname='helper', replset=0, pool_size=100):
        try:
            if replset:
                read_perf = pymongo.ReadPreference.SECONDARY_PREFERRED
                self.con = pymongo.MongoReplicaSetClient(
                        mongo_uri,
                        read_preference=read_perf,
                        max_pool_size=pool_size)
            else:
                self.con = pymongo.MongoClient(mongo_uri)
            self.db = self.con[dbname]
        except Exception as e:
            raise Exception('connect mongodb: %s, error: %s' % (mongo_uri, e))

    def find(
            self, table, cond,
            fields=[], page=1, count=20, sort=None):
        LOG.info("cond: %s, sort: %s", cond, sort)
        skip = (page - 1) * count
        if not fields:
            cursor = self.db[table].find(cond)
        else:
            cursor = self.db[table].find(cond, fields)
        if sort:
            cursor = cursor.sort(sort).skip(skip).limit(count)
        else:
            cursor = cursor.skip(skip).limit(count)
        return cursor

    def find_one(self, table, cond, fields=[]):
        if not fields:
            data = self.db[table].find_one(cond)
        else:
            data = self.db[table].find_one(cond, fields)
        return data

    def find_and_sort_with_index_and_skip(
            self,
            table,
            cond,
            sort_key,
            direction=pymongo.DESCENDING,
            fields=[],
            index=0,
            count=20):
        if not fields:
            cursor = self.db[table].find(cond).sort(sort_key, direction).skip(
                    int(index)).limit(int(count))
        else:
            cursor = self.db[table].find(cond, fields).sort(
                    sort_key, direction).skip(int(index)).limit(int(count))
        return cursor

    def count(self, table, cond):
        count = self.db[table].find(cond).count()
        return count

    def update(self, table, cond, data, multi=False, upsert=False):
        return self.db[table].update(
            cond, {'$set': data}, upsert=upsert, multi=multi)

    def remove(self, table, cond):
        return self.db[table].remove(cond)

    def insert(self, table, data):
        return self.db[table].insert(data)

    def save(self, table, data):
        return self.db[table].save(data)

    def increase(self, table, cond, field, value=1):
        return self.db[table].find_and_modify(cond, {'$inc': {field: value}})

    def find_and_modify(self, table, cond, data, upsert=False):
        return self.db[table].find_and_modify(
            cond, {'$set': data}, upsert=upsert)

    def try_find_one(self, table, cond, fields=[], try_count=3):
        while try_count:
            r = self.db[table].find_one(cond)
            if r:
                break
            try_count -= 1
            time.sleep(0.1)
        return r

    def try_find(self, table, cond, fields=[], try_count=3):
        while try_count:
            if fields:
                r = self.db[table].find(cond, fields)
            else:
                r = self.db[table].find(cond)
            if r.count() != 0:
                break
            try_count -= 1
            time.sleep(0.1)
        return r

    def unset(self, table, cond, data, multi=False):
        return self.db[table].update(
            cond, {'$unset': data}, multi=multi)


if __name__ == '__main__':
    mongo_db = MongoDB("mongodb://localhost", dbname='test')
    print mongo_db.find_one("test", {})
