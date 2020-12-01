# coding=utf-8

import logging
from enum import Enum
from logging.config import dictConfig

QINIU_ACCESS_TOKEN = 'xxxxx'
QINIU_KEY = 'xxxxxx'
QINIU_BUCKET = 'image'
QINIU_DOMAIN = 'http://image.shiguofu.cn'

# jiaofan mp
APPID = 'xxxxxx'
APPSEC = 'xxxxxxx'
TOKEN_VALIDATE = 'xxxxx'

# mp number hust
HUST_APPID = 'wxxxxxx'
HUST_APPSEC = '8xxxxxxxxxx8bda7'

# diandi shici
XCX_APPID = 'wxxxxxx'
XCX_APPSEC = 'cxxxxxxx'
TOKEN = 'xxxxxxxx'
AESKEY = 'xxxxxxx'

# shiyiwenhua
XCX_APPID_PAYED = 'xxxxx'
XCX_APPSEC_PAYED = 'xxxxx'


# wxpay config
MCHID = 'xxxxx'
PAY_KEY = 'xxxxx'
CERT_PATH = '/var/app/weixin/enabled/weixin/static/data/apiclient_cert.pem'
KEY_PATH = '/var/app/weixin/enabled/weixin/static/data/apiclient_key.pem'


TBK_CRAWLER_APKEY = 'xxxxx'
TBK_CRAWLER_APPSEC = 'xxxxx'
TBK_CRAWLER_PID = 'xxxxx'

TBK_APPKEY = 'xxxxx'
TBK_APPSEC = 'xxxxx'
TBK_PID = 'xxxxx'

# mongo config
MONGO_URI = 'mongodb://127.0.0.1:27017'
MONGO_DBNAME = 'weixin'

# weather config
HE_UNAME = 'HE1801241511171434'
HE_KEY = '91fa7ffe8d7644c9bac83baafd8183aa'

# redis config
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

CELERY_BROKER = 'redis://localhost/11'
# mysql config
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'P@55word'
MYSQL_DBNAME = 'minipro'

DEFAULT_HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 '
        'Safari/537.36'}

LOG_PATH = '/var/app/weixin/log'
LOGGER = None
LOG_WECHAT = None
LOG_TRACK = None
LOG_CRAWLER = None
LOG_MODEL = None
LOG_ALIMAMA = None


class TabId(Enum):
    RECOMMEND = 0
    POETRY = 1
    FAMOUS = 2
    AUTHOR = 3
    ANCIENT = 4
    SEN_DAILY = 5


def _load_config():
    global LOGGER, LOG_WECHAT, LOG_TRACK, LOG_CRAWLER, LOG_MODEL, LOG_ALIMAMA
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '|%(levelname)s %(asctime)s| '
                '[%(filename)s:%(lineno)d] %(message)s',
                },
            'detail': {
                'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
                }
        },
        'handlers': {
            'weixin': {
                'level': 'DEBUG',
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'verbose',
                'filename': LOG_PATH + '/weixin.log'
            },
            'err': {
                'level': 'ERROR',
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'verbose',
                'filename': LOG_PATH + '/error.log'
            },
            'wechat': {
                'level': 'INFO',
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'verbose',
                'filename': LOG_PATH + '/wechat.log'
            },
            'track': {
                'level': 'INFO',
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'verbose',
                'filename': LOG_PATH + '/track.log'
            },
            'crawler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'verbose',
                'filename': LOG_PATH + '/crawler.log'
            },
            'model': {
                'level': 'INFO',
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'verbose',
                'filename': LOG_PATH + '/model.log'
            },
            'alimama': {
                'level': 'DEBUG',
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'verbose',
                'filename': LOG_PATH + '/sync_orders.log'
            },
        },
        'loggers': {
            'weixin': {
                'handlers': ['weixin', 'err'],
                'level': 'INFO',
                'propagate': True
            },
            'wechat': {
                'handlers': ['wechat', 'err'],
                'level': 'INFO',
                'propagate': True
            },
            'track': {
                'handlers': ['track', 'err'],
                'level': 'INFO',
                'propagate': True
            },
            'crawler': {
                'handlers': ['crawler', 'err'],
                'level': 'DEBUG',
                'propagate': True
            },
            'model': {
                'handlers': ['model', 'err'],
                'level': 'INFO',
                'propagate': True
            },
            'alimama': {
                'handlers': ['alimama', 'err'],
                'level': 'DEBUG',
                'propagate': True
                }
        }
    }
    dictConfig(logging_config)
    LOGGER = logging.getLogger("weixin")
    LOG_WECHAT = logging.getLogger('wechat')
    LOG_TRACK = logging.getLogger("track")
    LOG_CRAWLER = logging.getLogger("crawler")
    LOG_MODEL = logging.getLogger("model")
    LOG_ALIMAMA = logging.getLogger("alimama")


def read_conf(filename):
    pass


_load_config()
