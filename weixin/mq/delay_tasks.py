# coding=utf-8

from .celery_app import app
from weixin.settings import LOGGER


@app.task
def add(x, y):
    return x + y
