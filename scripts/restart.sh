#!/bin/bash
#
# This scripts is used to restart the application.
# This scripts is required for all projects.
#
#
# Author : chzhong 
#

SCRIPT_DIR=`dirname $0`
${SCRIPT_DIR}/stop.sh
${SCRIPT_DIR}/start.sh
