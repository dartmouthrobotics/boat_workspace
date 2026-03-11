#!/bin/bash

sudo route del -net 169.254.0.0 gw 0.0.0.0 netmask 255.255.0.0
sudo route add -net 169.254.0.0/16 dev eth0
source /home/catabot-5/catkin_ws/src/catabot_bringup/script/common_include.sh
ROS_NAMESPACE=$ROBOT_NAME roscore
