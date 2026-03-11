#!/bin/bash
# startup_bringup.sh, ROS 2 port

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/test_connection.sh"

until [ "$(check_ipaddr)" -gt 2 ]; do
    sleep 2
done

ROBOT_NAME=robot_0
source "${SCRIPT_DIR}/common_include.sh"

ros2 launch catabot_bringup catabot_bringup.launch.py robot_name:="${ROBOT_NAME}"
