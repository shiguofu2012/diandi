# coding=utf-8
"""all API access"""

from weixin import app
from weixin.api import wechat_push
from weixin.api import wxpay
from weixin.api import xcxapi
from weixin.api import poetryapi
from weixin.api import config
from weixin.api import tbk_api
from weixin.api import admin_poetry
from weixin.api import poetry_web_api
from weixin.api import user_api
from weixin.api import grid_mini


if __name__ == '__main__':
    app.run(host='0.0.0.0', processes=8, debug=False, port=80)
