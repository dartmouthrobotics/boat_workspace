#!/bin/bash

while (! docker stats --no-stream ); do
	echo "Waiting for docker"
	sleep 2
done

cd /home/catabot-5/ros-apple-silicon && docker compose up -d 
cd /home/catabot-5/ros-apple-silicon && docker compose exec ros bash -c "source ~/catkin_ws/devel/setup.bash && roslaunch obstacle_avoidance_ros_pkg gps_transformer.launch gps_transform_ns:=robot_0" 
# && docker compose exec ros bash -c "source ~/catkin_ws/devel/setup.bash && roslaunch obstacle_avoidance_ros_pkg pseudo_obstacle_control.launch robot_1_init_x:=0 robot_1_init_y:=0 robot_1_init_yaw:=0"
