#!/bin/bash
# 

PARENT=weixin
PROJECT=weixin
DESC="wechat API service"
. /etc/profile
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/var/app/$PARENT/enabled/$PROJECT
NAME=$PROJECT
PID_FILE=/var/run/$NAME.pid
DAEMON=/usr/local/bin/uwsgi

if [ -f /etc/default/$PROJECT ]; then
	. /etc/default/$PROJECT
fi

function stop_service()
{
	if [ -f "${PID_FILE}" ]; then
        pushd /var/app/$PARENT/enabled/$PROJECT/ >/dev/null
        PID=`cat ${PID_FILE}`
        kill -INT ${PID} || echo "maybe process has been killed!"
        sleep 1
        IDS=`ps -ef | grep ${PID_FILE} | grep -v "grep" | awk '{print $2}'`
        for pid in ${IDS}
        do
            kill -INT ${pid} || echo "no such process: ${pid}"
        done
        rm "${PID_FILE}"
        echo "${DESC} stopped."
    else
        echo "${PROJECT} stop/waiting."
	fi
}

function start_service()
{
	if [ -f "$PID_FILE" ]; then
	    echo "$NAME is already running."
	else
	    pushd /var/app/$PARENT/enabled/$PROJECT/ >/dev/null
	    uwsgi --pidfile=${PID_FILE} --ini uwsgi.cfg --uid root --gid nogroup
	    popd >/dev/null
	fi
}

set -e

. /lib/lsb/init-functions

case "$1" in
	start)
		echo "Starting $DESC..."
		start_service
		echo "Done."
		;;
	stop)
		echo "Stopping $DESC..."
		stop_service
		echo "Done."
		;;

	restart)
		echo "Restarting $DESC..."
		stop_service
		start_service
		echo "Done."
		;;
	status)
		status_of_proc -p /var/run/$NAME.pid "$DAEMON" $NAME && exit 0 || exit $?
		;;
	*)
		echo "Usage: $NAME {start|stop|restart|status}" >&2
		exit 1
		;;
esac

exit 0

