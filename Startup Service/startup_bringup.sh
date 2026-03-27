#!/bin/bash
# startup_bringup.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source /opt/ros/humble/setup.bash
source /home/catabot-5/boat_ws/install/setup.bash

# source "${SCRIPT_DIR}/test_connection.sh"

until [ "$(check_ipaddr)" -gt 2 ]; do
    sleep 2
done

ros2 launch catabot_bringup catabot_bringup.launch.py \
    use_logging:=true \
    use_miniAHRS:=true \
    use_ZEDX:=true \
    use_lidar:=true \
    bag_dir:=/media/catabot-5/data/datalog/rosbag2