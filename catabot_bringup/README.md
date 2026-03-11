
## Blueboat configuration
1. pixhawk __fcu_url__: ud[://14500@] and there is no baudrate parameter.
2. new Ouster driver doesn't need `metadata` as an argument. We need to set `sensor_hostname` as `os-serialnumber.local` and `udp_dest` as computer's ip connected to LiDAR.
    a. need to record `/ouster/metadata` based on the new ROS driver

## launch 
roslaunch catabot_bringup catabot_bringup.launch 

## replay
* `TIME_FROM_ROS_TIME` is essential to retrieve the time when the bag file is recorded and time sync.
```
roslaunch ouster_ros replay.launch bag_file:=/home/catabot-4/datalog/rosbag/catabot-4_2025-10-08-20-21-20.bag timestamp_mode:=TIME_FROM_ROS_TIME
```

## checking

1. running
```
rviz
```
* fixed_frame: os_sensor
* topic: 
    * ouster_points
    * usb_surface_cam/image_raw/compressed
    * mavros/vfr_hub: 

2. replay
```
rostopic echo /ouster/points/header
```