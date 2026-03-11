#!/bin/bash
while (! docker stats --no-stream ); do
        echo "Waiting for docker"
        sleep 2
done
cd /home/catabot-5/vnc-ros-noetic && docker compose up -d
cd /home/catabot-5/vnc-ros-noetic && docker compose exec ros bash -c "source ~/catkin_ws/devel/setup.bash && cd passing_intention_lstm/src/passing_intention_lstm && python3 lstm_classifier_ros.py"
