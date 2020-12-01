#!coding=utf-8
"""add pythonpath to system"""

import sys
import os

PYH_FILE = 'weixin.pth'


def install_python_path():
    """
    Add project path to PATHONPATH
    """
    paths = [path for path in sys.path if path.endswith('dist-packages')]
    if len(paths) > 0:
        dist_path = paths[0]
        pth_path = os.path.join(dist_path, PYH_FILE)
        if os.path.exists(pth_path):
            os.remove(pth_path)
        if not os.path.exists(PYH_FILE):
            with open(PYH_FILE, "w+") as py_fp:
                py_fp.write(os.path.join(os.getcwd(), "./weixin/wxutils"))
        print 'Modifying python path...'
        print pth_path
        os.link(PYH_FILE, pth_path)


if __name__ == '__main__':
    install_python_path()
