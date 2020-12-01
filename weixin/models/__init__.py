# coding=utf-8
'''
the models of the;
'''

# from weixin.models.redisClient import RedisClient
from weixin.models.mysqldb import Mysql, MysqlConfig
from weixin.utils.mongodb import MongoDB
from weixin.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, \
        MYSQL_PASSWORD, MYSQL_DBNAME, MONGO_URI, MONGO_DBNAME

MYSQL_CONFIG = MysqlConfig(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db_name=MYSQL_DBNAME)

MYSQL_DB = Mysql(MYSQL_CONFIG)
MONGO_DB = MongoDB(MONGO_URI, MONGO_DBNAME)
POETRY_DB = MongoDB(MONGO_URI, 'poetry')
