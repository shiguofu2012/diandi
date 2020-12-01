# coding=utf-8
"""deploy service to host"""

import os
import platform
import tarfile

from fabric.api import env, lcd, put, cd
from fabric.utils import abort
from fabric.operations import sudo, local
from fabcommon import _init_env, check, ensure_dir, ensure_dir_windows

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CUR_DIR)
REMOTE_DIR = "/var/app/weixin/available"
REMOTE_SER_DIR = "/var/app/weixin/enabled"
LOCAL_TMP = '/tmp/build'
PROJECT_NAME = 'weixin'
SERVICE_NAME = 'weixin'
ENVIRON = ''
PLATFORM = 'linux'


def test():
    '''test env'''
    global ENVIRON
    ENVIRON = 'test'
    init()


def release():
    '''release env'''
    global ENVIRON
    ENVIRON = "release"
    init()


def localhost():
    '''lochost '''
    global ENVIRON
    ENVIRON = 'localhost'
    init()


def init():
    '''read config file and get config var'''
    # cfg_file = '%s/%s.cfg' % (ENVIRON, ENVIRON)
    global PLATFORM, LOCAL_TMP
    PLATFORM = platform.system().lower()
    if PLATFORM == 'windows':
        LOCAL_TMP = LOCAL_TMP.replace('/', '\\')
    cfg_file = os.path.join(ENVIRON, '{}.cfg'.format(ENVIRON))
    if check(cfg_file):
        _init_env(cfg_file)
    else:
        env.hosts = ''
        abort("config file: %s not found!" % cfg_file)


def deploy():
    print "deploy service to host..."
    dist_id = local("git rev-parse --short HEAD", capture=True)
    local_dist_dir = os.path.join(LOCAL_TMP, dist_id)

    # src_dir = os.path.join(ROOT_DIR, PROJECT_NAME)
    src_dir = ROOT_DIR
    config_dir = os.path.join(CUR_DIR, ENVIRON)
    if not check(src_dir):
        abort("src code dir: (%s) not found" % PROJECT_NAME)
    if PLATFORM == 'windows':
        ensure_dir_windows(local_dist_dir)
    else:
        ensure_dir(local_dist_dir)
    dist_file_name = "%s_%s.tar.gz" % (PROJECT_NAME, dist_id)
    remote_dir = "{}/{}".format(REMOTE_DIR, dist_id)
    with lcd(local_dist_dir):
        if PLATFORM == 'windows':
            local("xcopy {} . /S /E /Y".format(src_dir))
            local("xcopy {}\\*.cfg . /S /E /Y".format(config_dir))
            os.chdir(local_dist_dir)
            with tarfile.open(dist_file_name, 'w') as tar:
                tar.add('.')
        else:
            local("cp -rf %s/* ." % src_dir)
            local("cp -f %s/*.cfg ." % config_dir)
            local("tar -cvf %s .>/dev/null" % (dist_file_name))
        ensure_dir(remote_dir, False)
        sudo("chmod 777 %s -R" % remote_dir)
        put(dist_file_name, remote_dir)

    with cd(remote_dir):
        ensure_dir(REMOTE_SER_DIR, False)
        sudo("chmod 777 %s -R" % REMOTE_SER_DIR)
        # service_dir = os.path.join(REMOTE_SER_DIR, PROJECT_NAME)
        service_dir = "{}/{}".format(REMOTE_SER_DIR, PROJECT_NAME)
        sudo("tar -xvf %s>/dev/null" % dist_file_name)
        sudo("rm -rf %s" % dist_file_name)
        sudo("rm -rf %s" % service_dir)
        sudo("ln -sf %s %s" % (remote_dir, service_dir))

    with cd(service_dir):
        sudo("chmod +x ./scripts/*.sh")
        sudo("./scripts/install.sh")
        sudo("service %s restart" % SERVICE_NAME)
