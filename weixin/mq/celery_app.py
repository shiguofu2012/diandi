# coding=utf-8

from celery import Celery
import celery_config


app = Celery(__name__)
app.config_from_object(celery_config)
