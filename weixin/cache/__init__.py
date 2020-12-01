# coding=utf-8


from weixin.cache.redis_client import RedisClient
from weixin.settings import REDIS_HOST, REDIS_PORT, \
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, \
    MYSQL_DBNAME


lock_cache = RedisClient(REDIS_HOST, REDIS_PORT, 3)
wx_cache = RedisClient(REDIS_HOST, REDIS_PORT, 1)
data_cache = RedisClient(REDIS_HOST, REDIS_PORT, 2)
session_cache = RedisClient(REDIS_HOST, REDIS_PORT, 2)
tbk_cache = RedisClient(REDIS_HOST, REDIS_PORT, 14)
web_session_cache = RedisClient(REDIS_HOST, REDIS_PORT, 3)
# test connection
lock_cache.echo('')
