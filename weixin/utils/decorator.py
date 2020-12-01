# coding=utf-8
'''
utils decorators
'''


import sys
import json
import logging
import hashlib
import uuid
import traceback
from flask import jsonify, request
from functools import wraps
from time import time
from weixin.settings import LOGGER as _LOGGER

_PERF_LOGGER = logging.getLogger("weixin")


def cache_wrapper(key_info, expire_time=3600):
    def cache_wrapper_inner(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
            from weixin.cache import data_cache
            key = ''
            for arg in args:
                if isinstance(arg, basestring):
                    key = arg
            if not key:
                for arg, arg_value in kwargs.items():
                    if isinstance(arg_value, basestring):
                        key = arg_value
                        break
            if not key:
                if len(args) > 0:
                    key = json.dumps(args[0])
                elif len(kwargs) > 0:
                    key = json.dumps(kwargs.values()[0])
                else:
                    key = uuid.uuid4().hex
            key += key_info
            key = hashlib.md5(key).hexdigest()
            cache_data = data_cache.get(key)
            if cache_data:
                data = json.loads(cache_data)
                # data = unicode2utf(data)
                return data
            data = func(*args, **kwargs)
            if data:
                data_cache.set(key, json.dumps(data, ensure_ascii=False), expire_time)
            return data
        return wrapper
    return cache_wrapper_inner


def exception_handler_method(func):
    '''
    catch exception just return dict not jsonify
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            exc_type, value, detail = sys.exc_info()
            formatted_tb = traceback.format_tb(detail)
            _LOGGER.exception(formatted_tb)
            return {'errcode': -1, 'errmsg': ex}
    return wrapper


def exception_handler(func):
    '''
    decorator that can catch exception
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            exc_type, value, detail = sys.exc_info()
            formatted_tb = traceback.format_tb(detail)
            message = "url: %s traceback=%s" % (request.url, formatted_tb)
            _LOGGER.exception(message)
            return jsonify({'sta': -1, 'msg': '%s' % ex})
    return wrapper


def perf_logging(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        module_name = func.func_code.co_filename.split("/")[-1].split(".")[0]
        func_name = func.func_name
        msg = "%s.%s" % (module_name, func_name)

        start = time()
        result = func(*args, **kwargs)
        wast_time = (time() - start) * 1000
        _PERF_LOGGER.info("%s <- %s ms." % (msg, wast_time))
        return result
    return wrapper


def json_response(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        if '__error__' in kwargs:
            ret = kwargs['__error__']
        else:
            ret = func(*args, **kwargs)
        if ret and ret['errcode'] != 0:
            res = {'sta': ret['errcode'], 'msg': ret.get("errmsg", '')}
        else:
            res = {'sta': 0, 'msg': 'OK'}
            if 'data' in ret:
                res.update({'data': ret['data']})
        return jsonify(res)
    return wrapper


def str_response(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        return ret
    return wrapper


def validate_params(parameter_handlers={}):

    def validate(func):
        '''
        参数检查装饰器
        parameter_handlers:
            参数检查函数的字典格式
            当参数的值为None表示必须，没有格式的校验
            参数0是为session_id设置，表示不需要检查session_id
        '''
        @wraps(func)
        def wrapper(*args, **kwargs):
            from weixin.cache.session import check_session
            method = request.method.lower()
            if method == 'get':
                params = request.args
            elif method in ['put', 'delete', 'post']:
                get_params = request.args
                if method == 'post':
                    params = request.get_json()
                elif method == 'put':
                    params = request.data or '{}'
                    params = json.loads(params)
                if not params:
                    params = request.form
                    params = params.to_dict()
                if get_params:
                    params.update(get_params.to_dict())
            else:
                kwargs['__error__'] = {
                        "errcode": -1,
                        "errmsg": "not support method: %s" % method
                        }
                return func(*args, **kwargs)
            must_params = filter(lambda x: parameter_handlers[x] != 0, parameter_handlers)
            diff = set(must_params) - set(params)
            if diff:
                kwargs['__error__'] = {
                        'errcode': -1,
                        'errmsg': "缺少必要参数{}".format(list(diff)[0])}
                return func(*args, **kwargs)
            for param, value in params.items():
                handler = parameter_handlers.get(param)
                if handler and callable(handler):
                    value = handler(value)
                if param == 'session_id' and handler != 0:
                    value = check_session(value)
                    if not value:
                        kwargs['__error__'] = {
                                'errcode': 10000, 'errmsg': "invalid session"}
                        break
                    param = 'session'
                kwargs[param] = value
            return func(*args, **kwargs)
        return wrapper
    return validate
