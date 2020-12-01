#coding=utf-8

import os
from fabric.operations import sudo, run, local
from fabric.api import env
from fabric.utils import abort

from ConfigParser import ConfigParser, NoOptionError


class CommonConfigParser(ConfigParser):

    def get(self, section, option):
        try:
            return ConfigParser.get(self, section, option)
        except NoOptionError:
            return None


def check(filename):
    if os.path.exists(filename):
        return True
    return False


def ensure_dir(dirname, is_local=True):
    func = local if is_local else sudo
    func("mkdir -p %s" % dirname)


def ensure_dir_windows(dirname):
    print("mkdir {} ...".format(dirname))
    if check(dirname):
        print("dir {} exists..".format(dirname))
        return
    local("mkdir {}".format(dirname))


def _init_env(cfgfile):
    #config = ConfigParser.ConfigParser()
    config = CommonConfigParser()
    config.read(cfgfile)
    section_name = 'default'
    user = config.get(section_name, "user")
    hosts = config.get(section_name, "hosts")
    port = config.get(section_name, "port")
    print user, hosts
    if port:
        env.port = port
    key_file = config.get(section_name, "keyfile")
    if not key_file:
        passwd = config.get(section_name, "passwd")
        print passwd
        env.password = passwd
    else:
        env.key_filename = key_file
    env.hosts = hosts
    env.user = user
    env.keepalive = 30
    print env


if __name__ == "__main__":
    _init_env("./release/release.cfg")
