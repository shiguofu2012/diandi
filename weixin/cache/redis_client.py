# coding=utf-8

'''
redis operation
'''
import redis
from weixin.utils.decorator import exception_handler


class RedisClient(object):
    '''
    redis operations
    '''
    client = None

    @exception_handler
    def __init__(self, host, port, db):
        self.client = redis.Redis(host=host, port=port, db=db)

    def keys(self, key_pattern='*'):
        return self.client.keys(key_pattern)

    @exception_handler
    def set(self, key, value, expire=None):
        '''
        set key-value data;
        '''
        ret = self.client.set(key, value)
        if expire:
            self.client.expire(key, expire)
        return ret

    @exception_handler
    def get(self, key):
        '''
        get key-value data by key;
        '''
        ret = self.client.get(key)
        return ret

    @exception_handler
    def delete(self, key):
        return self.client.delete(key)

    @exception_handler
    def expire(self, key, ttl):
        '''
        set ttl for a key;
        '''
        ret = self.client.expire(key, ttl)
        return ret

    @exception_handler
    def inc(self, key, count=1, expire=None):
        ret = self.client.incr(key, count)
        if expire:
            self.expire(key, expire)
        return ret

    @exception_handler
    def lock(self, key, expire=5):
        '''
        implement lock by incr
        '''
        ret = self.client.incr(key)
        if ret != 1:
            return False
        self.client.expire(key, expire)
        return True

    @exception_handler
    def unlock(self, key):
        ret = self.client.delete(key)
        if ret != 1:
            return False
        return True

    @exception_handler
    def zadd(self, key, value, scores):
        ret = self.client.zadd(key, value, scores)
        return ret

    @exception_handler
    def zrank(self, key, value):
        ret = self.client.zrank(key, value)
        return ret

    @exception_handler
    def zscore(self, key, value):
        ret = self.client.zscore(key, value)
        return ret

    @exception_handler
    def zincrby(self, key, value, incr_value):
        incr_value = int(incr_value)
        ret = self.client.zincrby(key, value, incr_value)
        return ret

    @exception_handler
    def zcard(self, key):
        ret = self.client.zcard(key)
        return ret

    @exception_handler
    def zrange(self, key, start=0, end=-1, withscore=False):
        ret = self.client.zrange(key, start, end, True, withscore)
        return ret

    @exception_handler
    def save_dict(self, key, data, expire=None):
        """save dict data to redis hash"""
        ret = self.client.hmset(key, data)
        if expire is not None:
            self.client.expire(key, int(expire))
        return ret

    @exception_handler
    def hset(self, key, name, value):
        """hash data set"""
        return self.client.hset(key, name, value)

    @exception_handler
    def hget(self, key, name=None):
        if name is not None:
            return self.client.hget(key, name)
        return self.client.hgetall(key)

    def echo(self, string):
        return self.client.echo(string)
