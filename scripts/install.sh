#!/bin/bash

python setup.py -q build

SCRIPT_DIR=`dirname $0`
PROJECT=weixin

if [ "$1" = "checkdeps" ] ; then

    if [ -f "${SCRIPT_DIR}/install_deps.sh" ]; then
        ${SCRIPT_DIR}/install_deps.sh
    fi
fi

if [ -f "${SCRIPT_DIR}/setup_conf.sh" ]; then
    ${SCRIPT_DIR}/setup_conf.sh
fi

PTH_FILE="${PROJECT}.pth"
if [ "$2" = "lib" ] ; then
    sudo python setup.py -q install
else
    pwd > ${PTH_FILE}
    sudo python scripts/install.py
fi

echo Installing service... 
[ -z `grep "^wechat:" /etc/passwd` ] && sudo useradd -r wechat -M -N

mkdir -p /var/app/$PROJECT/data
mkdir -p /var/app/$PROJECT/log
chmod -R a+rw /var/app/$PROJECT/data
chmod -R a+rw /var/app/$PROJECT/log
# chown wechat:wechat /var/app/$PROJECT/data
# chown wechat:wechat /var/app/$PROJECT/log

if [ ! -f "/etc/init.d/$PROJECT" ]; then
    echo "install deps..."
    ./scripts/install_deps.sh
fi

ln -sf /var/app/$PROJECT/enabled/$PROJECT/scripts/project-init.sh /etc/init.d/$PROJECT
update-rc.d $PROJECT defaults
