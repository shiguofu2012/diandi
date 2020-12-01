# coding=utf-8
# !/usr/bin/python
'''
time convert;
'''
import time

_DEFAURT_FORMAT = '%Y-%m-%d %H:%M:%S'


def stamp2time(stamp, _format=_DEFAURT_FORMAT):
    '''
    convert a timestamp to time string in _format;
    '''
    return time.strftime(_format, time.localtime(stamp))


def time2stamp(time_str, _format=_DEFAURT_FORMAT):
    '''
    convert a time string to timestamp;
    '''
    return time.mktime(time.strptime(time_str, _format))
