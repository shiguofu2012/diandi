#!/bin/bash
# exec this scripts as root, or you will

SYS_DEPS=( python-pip mongodb redis libmysqlclient-dev wheel setuptools )

PYTHON_DEPS=( "pycrypto" "flask" "pymongo==2.7" "simplejson" "uwsgi" 
        "requests==2.4.3" "redis" "qrcode" "mysql" "jinja2" "xmltodict" "pillow"
        "qiniu==7.2.6" "lxml" "jnius"
        )


function install_dependencies()
{
   # update to latest to avoid some packages can not found.
   # apt-get update
   echo "Installing required system packages..."
   # for sys_dep in ${SYS_DEPS[@]};do
   #    install_sys_dep $sys_dep
   # done
   echo "Installing required system packages finished."

   echo "Installing required python packages..."
   for python_dep in ${PYTHON_DEPS[@]};do
      install_python_dep ${python_dep}
   done
   echo "Installing required python packages finished."

   echo "install wechat util..."
   install_wechatutil
   echo "wechat util install Done"

}


function install_sys_dep()
{         
    # input args  $1 package name 
    if [ `aptitude  search  $1  | grep -c "^i \+${1} \+"` = 0 ];then
        aptitude install  -y $1
    else
        echo "Package ${1} already installed."
    fi
}

function install_python_dep()
{                          
    # input args $1 like simplejson==1.0 ,can only extractly match
    if [ `pip freeze | grep -c "^${1}"` = 0 ];then
        pip install  $1
    else
        echo "Python package ${1} already installed."
    fi
}

# 商品搜索用到lucene
function install_jdk()
{
    `cd /opt && wget http://image.shiguofu.cn/static/jdk1.8.0_144.tar.xz`
    echo "decompress file..."
    cd /opt && xz -z jdk1.8.0_144.tar.xz
    cd /opt && tar -xvf jdk1.8.0_144.tar
    echo "export JAVA_HOME=/opt/jdk1.8.0_144" >> ~/.bashrc
    echo 'export PATH=$PATH:$JAVA_HOME/bin' >> ~/.bashrc
    echo 'export CLASS_PATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar' >> ~/.bashrc
    source ~/.bashrc
}

# 安装自己封装的微信库
function install_wechatutil()
{
  echo "git clone https://github.com/shiguofu2012/wechat.git..."
  `cd /opt && git clone "https://github.com/shiguofu2012/wechat.git"`
  echo "install wechat..."
  `cd /opt/wechat && python setup.py install`
}
export JDK_HOME=$JAVA_HOME
source ~/.bashrc
install_dependencies
