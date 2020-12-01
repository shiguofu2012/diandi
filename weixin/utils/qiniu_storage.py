# coding=utf-8

import os
import qiniu
import uuid
import imghdr
from StringIO import StringIO
from urlparse import urljoin
from datetime import datetime
from qiniu import BucketManager
from weixin.cache import data_cache
from weixin.settings import QINIU_ACCESS_TOKEN, QINIU_KEY, QINIU_BUCKET, \
    LOGGER, QINIU_DOMAIN


class QiNiuStorage(object):

    def __init__(self, qiniu_token, qiniu_secret, qiniu_bucket):
        self.qiniu_token = qiniu_token
        self.qiniu_secret = qiniu_secret
        self.qiniu_bucket = qiniu_bucket
        self.auth = None
        data_cache.delete(self.qiniu_token_key)

    def list_data(self, marker='', limit=100):
        self.qiniu_access_token
        bucket_manager = BucketManager(self.auth)
        ret, eof, info = bucket_manager.list(
            self.qiniu_bucket, marker=marker, limit=limit)
        if ret is None:
            return [], ''
        return ret['items'], ret.get('marker', '')

    def upload_file(self, file_path, remote_path='images'):
        file_data = None
        try:
            with open(file_path, 'rb') as _file:
                file_data = _file.read()
        except Exception as ex:
            LOGGER.error("update file: %s ex: %s", file_path, ex)
            return False, ex
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = remote_path.split("/")[-1]
        if filename.find('.') == -1:
            filename = file_path.split('/')[-1]
            up_path = os.path.join(date_str, filename)
            if remote_path:
                up_path = os.path.join(remote_path, up_path)
        else:
            up_path = remote_path
        return self._upload_data(file_data, up_path)

    def upload_memfile(self, file_data, remote_path='images'):
        filename = remote_path.split("/")[-1]
        if filename.find('.') == -1:
            filename = uuid.uuid4().hex
            file_type = imghdr.what(StringIO(file_data))
            if file_type:
                filename += ('.' + file_type)
            date_str = datetime.now().strftime("%Y-%m-%d")
            remote_path = os.path.join(remote_path, date_str)
            remote_path = os.path.join(remote_path, filename)
        return self._upload_data(file_data, remote_path)

    def delete_file(self, remote_path):
        self.qiniu_access_token
        bucket_manager = BucketManager(self.auth)
        ret, info = bucket_manager.delete(self.qiniu_bucket, remote_path)
        return ret

    def _upload_data(self, file_data, file_name):
        ret, info = qiniu.put_data(
            self.qiniu_access_token, file_name, file_data)
        if ret is not None:
            return True, urljoin(QINIU_DOMAIN, file_name)
        return False, info

    def _fresh_token(self):
        qiniu_auth = qiniu.Auth(self.qiniu_token, self.qiniu_secret)
        self.auth = qiniu_auth
        token = qiniu_auth.upload_token(self.qiniu_bucket)
        data_cache.set(self.qiniu_token_key, token, 3580)
        return token

    @property
    def qiniu_access_token(self):
        token = data_cache.get(self.qiniu_token_key)
        if not token:
            token = self._fresh_token()
        return token

    @property
    def qiniu_token_key(self):
        return "qiniu_{0}".format(self.qiniu_token)


QINIU_STORAGE = QiNiuStorage(QINIU_ACCESS_TOKEN, QINIU_KEY, QINIU_BUCKET)
