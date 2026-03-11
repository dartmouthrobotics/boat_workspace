#!/bin/bash

source /home/catabot-5/catkin_ws/src/catabot_bringup/script/test_connection.sh

until [ `check_ipaddr` -gt 2 ]; do
  sleep 2
done

sudo route add -net 192.168.2.0/24 dev eth0
ROBOT_NAME=robot_0
source /home/catabot-5/catkin_ws/src/catabot_bringup/script/common_include.sh
ROS_NAMESPACE=$ROBOT_NAME screen -dm -S imagenex roslaunch imagenex_sidescan sidescansonar.launch
