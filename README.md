# boat_workspace — ROS 2 ASV Platform

This workspace integrates all drivers, sensors, and data-logging packages for the **Catabot** autonomous surface vehicle (ASV), a catamaran-style robot developed at Dartmouth College.

**Tested on:** ROS 2 Humble · NVIDIA Jetson AGX Orin

## Packages

| Package | Description |
|---|---|
| [`catabot_bringup`](#catabot_bringup-for-ros-2) | Top-level orchestration — launches all sensors and drivers |
| [`inertiallabs-ros2-pkgs`](#inertiallabs-ros2-pkgs) | ROS 2 driver for Inertial Labs INS/IMU/AHRS sensors (fork with local modifications) |
| [`ouster-ros`](#ouster-ros) | Official Ouster LiDAR ROS 2 driver (OS0/OS1/OS2/OSDome) |
| [`rosbag2_composable_recorder`](#rosbag2_composable_recorder) | Composable rosbag2 recorder for in-process high-throughput recording |
| [`zed_mcap_recorder`](#zed_mcap_recorder) | Custom composable node for ZED camera data recording to MCAP |
| [`zed-ros2-wrapper`](#zed-ros2-wrapper) | Official Stereolabs ZED ROS 2 wrapper (v5.2.2) |

## inertiallabs-ros2-pkgs

Fork of the upstream [Inertial Labs ROS 2 driver](https://github.com/inertiallabs/inertiallabs-ros2-pkgs) with local modifications for the Catabot (composable node, low-latency serial, bug fixes — see the package README for details).

| Sub-package | Description |
|---|---|
| `inertiallabs_ins` | ROS 2 driver for IL INS/IMU-P/AHRS/AHRS-10 sensors (serial, TCP, or UDP) |
| `inertiallabs_msgs` | Custom message definitions (`InsData`, `SensorData`, `GpsData`, `GnssData`, `MarineData`) |
| `inertiallabs_sdk` | Vendored Inertial Labs C/C++ SDK v0.2 (not a ROS package) |

## ouster-ros

Official Ouster ROS 2 driver (v0.14.0) for OS0/OS1/OS2/OSDome sensors. See the package README for full usage. The `ouster-sdk` is included as a git submodule.

| Sub-package | Description |
|---|---|
| `ouster_ros` | Main driver node (live, record, replay, multicast modes) |
| `ouster_sensor_msgs` | Custom messages and services (`PacketMsg`, `GetConfig`, `SetConfig`, etc.) |

**Catabot config:** hostname `os-122525001750.local`, mode `1024x10`, `timestamp_mode: TIME_FROM_ROS_TIME` (see `catabot_bringup/param/os_sensor_cloud_image_params.yaml`).

## rosbag2_composable_recorder

Composable node wrapper around `rosbag2_transport::Recorder`. Runs inside the same component container as data-producing nodes to eliminate inter-process serialization overhead. See the package README for parameters and usage.

> Only needed for ROS 2 Humble/Iron — Jazzy and later include this capability in standard `rosbag2`.

## zed_mcap_recorder

Custom composable node that records ZED camera compressed images and IMU data to **MCAP** files. Uses an asynchronous producer–consumer queue to decouple ROS callbacks from disk I/O. See the package README for parameters and usage.

## zed-ros2-wrapper

Official Stereolabs ZED ROS 2 wrapper (v5.2.2). Requires ZED SDK v5.2 and CUDA. See the package README for full documentation.

| Sub-package | Description |
|---|---|
| `zed_components` | Core composable components for all ZED camera models |
| `zed_wrapper` | Launch entry-point (`zed_camera.launch.py`), YAML params, URDF/xacro, RViz2 configs |
| `zed_ros2` | Meta-package for workspace discovery |
| `zed_debug` | Development-only debug-symbol builds and GDB tooling (skip in field builds) |

## Build

```bash
cd ~/boat_ws
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release --packages-skip zed_debug
source install/setup.bash
```

> `--cmake-args -DCMAKE_BUILD_TYPE=Release` optimizes the build but does **not** exclude `zed_debug` — `--packages-skip zed_debug` is still required for that.

---

# catabot_bringup for ROS 2

---

## Package Structure

```
catabot_bringup/
├── launch/
│   ├── catabot_bringup.launch.py         # entry-point (selects composable vs. standalone)
│   ├── catabot_bringup_common.launch.py  # main bringup logic with all sensor groups
│   ├── container.launch.xml              # component container for composable mode
│   ├── sensor.composite.launch.py        # composable sensor node loader
│   ├── logger.launch.py                  # rosbag2 recorder
│   ├── zed_camera.launch.py              # per-camera ZED launch helper
│   ├── apm.launch                        # mavros / Pixhawk
│   ├── apm_config.yaml                   # mavros parameters
│   ├── apm_pluginlists.yaml              # mavros plugin whitelist
│   ├── node.launch                       # generic node launch helper
│   └── servo.launch                      # servo controller
├── param/
│   ├── catabot_config.yaml               # platform-level parameters
│   ├── os_sensor_cloud_image_params.yaml # Ouster LiDAR configuration
│   ├── recorder_topics.yaml              # topics recorded by logger
│   └── zed/
│       ├── zedx.yaml                     # ZED-X camera parameters
│       └── common_stereo.yaml            # shared stereo parameters
├── script/
│   ├── startup_bringup.sh                # system startup script
│   ├── startup_docker_lstm.sh            # Docker LSTM inference startup
│   ├── startup_docker_moa.sh             # Docker MOA inference startup
│   ├── startup_imagenex.sh               # Imagenex side-scan sonar startup
│   ├── startup_test.sh                   # test startup script
│   ├── test_connection.sh                # network connectivity test
│   ├── test_topics.py                    # ROS topic sanity check
│   ├── servo_controller.py               # servo control utility
│   ├── read_message_python.py            # message inspection utility
│   └── common_include.sh                 # shared shell functions
└── reqs/
    └── 99-catabot.rules                  # udev rules for USB devices
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

> **Field recording tip:** Use `use_composable:=true` to run all nodes in a single intra-process container, reducing CPU overhead and serialization latency on the high-bandwidth ZED and LiDAR streams. Set `zed_record_root_dir` and `bag_dir` to a path on the NVMe SSD (e.g. `/mnt/nova_ssd/datalog/`) — writing to the eMMC or SD card will bottleneck recording throughput.

```bash
ros2 launch catabot_bringup catabot_bringup.launch.py \
    use_composable:=true \
    use_miniAHRS:=true \
    use_lidar:=true \
    use_zed_blue:=true \
    use_zed_green:=true \
    use_zed_red:=true \
    use_zed_pink:=true \
    use_pixhawk:=true \
    use_logging:=true \
    use_surface_camera:=true \
    use_underwater_camera:=false \
    use_sonde:=false \
    use_sonar:=false \
    use_sidescan:=false
```

### Mode

| Argument | Default | Description |
|---|---|---|
| `use_composable` | `false` | Use intra-process composable node container instead of standalone nodes |
| `robot_name` | `robot_0` | ROS namespace for the robot |

### Device enable flags

| Argument | Default | Description |
|---|---|---|
| `use_miniAHRS` | `true` | Launch InertialLabs INS driver |
| `use_lidar` | `true` | Launch Ouster LiDAR driver |
| `lidar_ouster` | `true` | Use Ouster driver (vs. Velodyne) |
| `use_ZEDX` | `true` | Enable ZED-X camera mode |
| `use_zed_blue/green/red/pink` | `true` | Enable each ZED camera individually |
| `use_pixhawk` | `true` | Launch mavros (Pixhawk autopilot) |
| `use_logging` | `true` | Start rosbag2 recorder |
| `use_surface_camera` | `true` | Launch USB surface camera |
| `use_underwater_camera` | `false` | Launch USB underwater camera |
| `use_sonde` | `false` | Launch YSI water-quality sonde |
| `use_sonar` | `false` | Launch depth sonar |
| `use_sidescan` | `false` | Launch Imagenex side-scan sonar |

### InertialLabs miniAHRS

| Argument | Default | Description |
|---|---|---|
| `miniahrs_url` | `serial:/dev/ttyUSB0:921600` | Serial URL: `serial:<device>:<baudrate>` |
| `ins_output_format` | `149` | InertialLabs output data format ID |

### Ouster LiDAR

| Argument | Default | Description |
|---|---|---|
| `ouster_host` | `os-122525001750.local` | Sensor hostname or IP |
| `udp_dest` | `""` | UDP destination override (empty = auto) |
| `lidar_mode` | `1024x10` | Scan resolution and rate |
| `viz` | `false` | Launch RViz visualizer |

### ZED cameras

| Argument | Default | Description |
|---|---|---|
| `zed_camera_model` | `zedx` | ZED camera model |
| `zed_sn_blue/green/red/pink` | see launch file | Camera serial numbers |
| `zed_publish_tf` | `false` | Publish `odom → zed_camera_link` TF |
| `zed_publish_map_tf` | `false` | Publish `map → odom` TF |
| `zed_publish_imu_tf` | `false` | Publish IMU TF |
| `zed_record_root_dir` | `/home/catabot-5/datalog/rosbag2` | Root directory for ZED recordings |
| `zed_record_session` | current timestamp | Session subdirectory name |

### Device paths

| Argument | Default | Description |
|---|---|---|
| `usb_surface` | `/dev/surface_cam` | Surface camera device |
| `usb_underwater` | `/dev/video0` | Underwater camera device |
| `usb_sonde` | `/dev/ysi_sonde` | YSI sonde serial device |
| `usb_sonar` | `/dev/sonar` | Sonar serial device |
| `usb_pixhawk` | `udp://:14550@` | Pixhawk connection URL |
| `pixhawk_baudrate` | `57600` | Pixhawk serial baudrate |
| `usb_cam_node_start_delay` | `3.0` | Startup delay for surface camera (s) |
| `usb_cam_underwater_start_delay` | `1.0` | Startup delay for underwater camera (s) |

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

The service waits for network and NVMe mount (`/mnt/nova_ssd/data`) before launching. Add to `/etc/systemd/system/catabot_bringup.service` under `[Service]`:

```ini
LimitRTPRIO=99
LimitNICE=-20
```