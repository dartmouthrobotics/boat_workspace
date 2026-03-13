# catabot_bringup for ROS 2

---

## Package Structure

```
catabot_bringup/
├── launch/
│   ├── catabot_bringup.launch.py   # main 
│   ├── ins.launch                  # IMU
│   └── logger.launch.py            # rosbag2 recorder
├── param/
│   └── catabot_config.yaml
├── script/
│   ├── startup_bringup.sh          
│   └── common_include.sh
└── reqs/
    └── 99-catabot.rules            # udev rules
```

---

## Sensors

| Sensor | Driver Package | Key Topic(s) |
|---|---|---|
| ZED X x4 (blue/green/red/pink) | `zed_wrapper` | `/<color>/zed/left/color/raw/image`, `/<color>/zed/imu/data` |
| MiniAHRS | `inertiallabs_ins` | `/imu/data`, `/Inertial_Labs/ins_data`, `/Inertial_Labs/gnss_data` |
| Ouster OS1 LiDAR | `ouster_ros` | `/ouster/points`, `/ouster/scan`, `/ouster/imu` |
| Surface Camera | `usb_cam_surface` | `/image_raw`, `/image_raw/compressed`, `/image_raw/compressedDepth` |
| Pixhawk (mavros) | `mavros` | `/mavros/imu/data`, `/mavros/global_position/global` |

---

## Launch Arguments

```bash
ros2 launch catabot_bringup catabot_bringup.launch.py \
    use_miniAHRS:=true \
    use_lidar:=true \
    use_zed_blue:=true \
    use_zed_green:=true \
    use_zed_red:=true \
    use_zed_pink:=true \
    use_pixhawk:=false \
    use_logging:=false
```

| Argument | Default | Description |
|---|---|---|
| `use_miniAHRS` | `true` | Launch InertialLabs INS driver |
| `miniahrs_url` | `serial:/dev/ttyUSB0:921600` | Serial URL for INS |
| `ins_output_format` | `149` | INS output format code |
| `use_lidar` | `false` | Launch Ouster LiDAR driver |
| `ouster_host` | `os-122525001750.local` | Ouster hostname |
| `lidar_mode` | `1024x10` | Ouster scan mode |
| `use_zed_blue/green/red/pink` | `true` | Enable each ZED camera |
| `zed_sn_blue/green/red/pink` | see launch file | ZED serial numbers |
| `use_pixhawk` | `false` | Launch mavros |
| `use_logging` | `false` | Start rosbag2 recorder |
| `bag_dir` | `/media/catabot-5/data/datalog/rosbag2` | Bag output path |

---

## Timestamp Alignment

All sensors use ROS wall clock (`node->now()`). Measured offsets vs ZED:

| Source | Offset | Notes |
|---|---|---|
| ZED IMU | 0ms (reference) | — |
| InertialLabs `/imu/data` | ±30ms  | GPS time re-anchored to ROS time in driver |
| Ouster `/ouster/imu` | +66ms | Timestamped at packet receipt |
| Ouster `/ouster/points` | -126ms | Timestamped at scan start |

Ouster configured with `timestamp_mode: TIME_FROM_ROS_TIME` in `os_sensor_cloud_image_params.yaml` 

---

## InertialLabs IMU Rate

The driver publishes `/imu/data` at **~143–150 Hz**  with `ins_output_format: 149`. The format 149 bundles GNSS fields whose update rate, around 27 Hz gates serial packet transmission. The internal IMU sensor runs at 200 Hz but packets are only transmitted when the full INS solution is assembled.

---

## IMU Driver Notes

`inertiallabs-ros2-pkgs` applied serveral changes:

- Removed `rclcpp::Rate rate(100)` polling loop
- Publisher queue sizes increased from 1 to 10
- `MultiThreadedExecutor` instead of `rclcpp::spin`
- `SCHED_FIFO` realtime priority via `setcap cap_sys_nice+ep`
- Magnetometer indexing changed (`Mag[0/1/2]` not all `Mag[0]`)
- Gyro unit conversion to rad/s 
- `SerialPort.cpp`: removed `isatty()` syscall on every read; `poll()` timeout reduced from 1000ms to 6ms; `VMIN=0, VTIME=0` set for low-latency reads

To apply `setcap` after each build:
```bash
sudo setcap cap_sys_nice+ep \
    ~/boat_ws/install/inertiallabs_ins/lib/inertiallabs_ins/il_ins
```

---

## Systemd Autostart

```bash
sudo cp reqs/catabot_bringup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable catabot_bringup.service
```

The service waits for network and NVMe mount (`/media/catabot-5/data`) before launching. Add to `/etc/systemd/system/catabot_bringup.service` under `[Service]`:

```ini
LimitRTPRIO=99
LimitNICE=-20
```

---

## Build

```bash
cd ~/boat_ws
colcon build --packages-select catabot_bringup inertiallabs_ins
source install/setup.bash
```