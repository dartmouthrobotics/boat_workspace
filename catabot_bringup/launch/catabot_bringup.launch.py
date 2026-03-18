"""
catabot_bringup.launch.py 
"""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import (
    AnyLaunchDescriptionSource,
    PythonLaunchDescriptionSource,
)
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ------------------------------------------------------------------ #
    #  Declare arguments                                                 #
    # ------------------------------------------------------------------ #
    args = [
        # --- device enable flags ---
        DeclareLaunchArgument("use_lidar",             default_value="true"),
        DeclareLaunchArgument("lidar_ouster",          default_value="true"),
        DeclareLaunchArgument("use_ZEDX",              default_value="true"),
        DeclareLaunchArgument("use_miniAHRS",          default_value="true"),
        DeclareLaunchArgument("use_pixhawk",           default_value="true"),
        DeclareLaunchArgument("use_logging",           default_value="true"),
        DeclareLaunchArgument("use_surface_camera",    default_value="true"),

        DeclareLaunchArgument("use_underwater_camera", default_value="false"),
        DeclareLaunchArgument("use_sonde",             default_value="false"),
        DeclareLaunchArgument("use_sonar",             default_value="false"),
        DeclareLaunchArgument("use_sidescan",          default_value="false"),

        # --- time delays for USB cameras ---
        DeclareLaunchArgument("usb_cam_node_start_delay",       default_value="3.0"),
        DeclareLaunchArgument("usb_cam_underwater_start_delay", default_value="1.0"),

        # --- device paths ---
        DeclareLaunchArgument("usb_surface",      default_value="/dev/surface_cam"),
        DeclareLaunchArgument("usb_underwater",   default_value="/dev/video0"),
        DeclareLaunchArgument("usb_sonde",        default_value="/dev/ysi_sonde"),
        DeclareLaunchArgument("usb_sonar",        default_value="/dev/sonar"),
        DeclareLaunchArgument("usb_pixhawk",      default_value="udp://:14550@"),
        DeclareLaunchArgument("pixhawk_baudrate", default_value="57600"),

        # miniAHRS: InertialLabs ins_url = "serial:<device>:<baudrate>"
        # Add udev rule to get persistent /dev/miniAHRS symlink
        DeclareLaunchArgument(
            "miniahrs_url",
            default_value="serial:/dev/ttyUSB0:921600",
            description="InertialLabs serial URL: serial:<device>:<baudrate>",
        ),
        DeclareLaunchArgument(
            "ins_output_format",
            default_value="149",
            description="InertialLabs output data format ID",
        ),

        # --- ZED ---
        DeclareLaunchArgument("zed_camera_model", default_value="zedx"),
        DeclareLaunchArgument("use_zed_blue",  default_value="true"),
        DeclareLaunchArgument("use_zed_green", default_value="true"),
        DeclareLaunchArgument("use_zed_red",   default_value="true"),
        DeclareLaunchArgument("use_zed_pink",  default_value="true"),
        DeclareLaunchArgument("zed_sn_blue",  default_value="47479174"),
        DeclareLaunchArgument("zed_sn_green", default_value="47983353"),
        DeclareLaunchArgument("zed_sn_red",   default_value="42151672"),
        DeclareLaunchArgument("zed_sn_pink",  default_value="47226740"),
        DeclareLaunchArgument("zed_publish_tf",     default_value="false",
            description="Let ZED publish odom->zed_camera_link TF"),
        DeclareLaunchArgument("zed_publish_map_tf", default_value="false",
            description="Let ZED publish map->odom TF"),
        DeclareLaunchArgument("zed_publish_imu_tf", default_value="false",
            description="Let ZED publish IMU TF"),

        # --- Ouster LiDAR ---
        DeclareLaunchArgument("ouster_host", default_value="os-122525001750.local"),
        DeclareLaunchArgument("udp_dest",    default_value=""),
        DeclareLaunchArgument("lidar_mode",  default_value="1024x10"),
        DeclareLaunchArgument("viz",         default_value="false"),

        # --- robot namespace ---
        DeclareLaunchArgument("robot_name",  default_value="robot_0"),
    ]

    # ------------------------------------------------------------------ #
    #  LaunchConfiguration handles                                       #
    # ------------------------------------------------------------------ #
    use_lidar             = LaunchConfiguration("use_lidar")
    lidar_ouster          = LaunchConfiguration("lidar_ouster")
    use_ZEDX              = LaunchConfiguration("use_ZEDX")
    use_miniAHRS          = LaunchConfiguration("use_miniAHRS")
    use_pixhawk           = LaunchConfiguration("use_pixhawk")
    use_logging           = LaunchConfiguration("use_logging")
    use_surface_camera    = LaunchConfiguration("use_surface_camera")
    use_underwater_camera = LaunchConfiguration("use_underwater_camera")
    use_sonde             = LaunchConfiguration("use_sonde")
    use_sonar             = LaunchConfiguration("use_sonar")
    use_sidescan          = LaunchConfiguration("use_sidescan")
    surf_delay            = LaunchConfiguration("usb_cam_node_start_delay")
    uw_delay              = LaunchConfiguration("usb_cam_underwater_start_delay")
    usb_surface           = LaunchConfiguration("usb_surface")
    usb_underwater        = LaunchConfiguration("usb_underwater")
    usb_sonde             = LaunchConfiguration("usb_sonde")
    usb_sonar             = LaunchConfiguration("usb_sonar")
    usb_pixhawk           = LaunchConfiguration("usb_pixhawk")
    miniahrs_url          = LaunchConfiguration("miniahrs_url")
    ins_output_format     = LaunchConfiguration("ins_output_format")
    zed_camera_model      = LaunchConfiguration("zed_camera_model")
    zed_publish_tf        = LaunchConfiguration("zed_publish_tf")
    zed_publish_map_tf    = LaunchConfiguration("zed_publish_map_tf")
    zed_publish_imu_tf    = LaunchConfiguration("zed_publish_imu_tf")
    use_zed_blue          = LaunchConfiguration("use_zed_blue")
    use_zed_green         = LaunchConfiguration("use_zed_green")
    use_zed_red           = LaunchConfiguration("use_zed_red")
    use_zed_pink          = LaunchConfiguration("use_zed_pink")
    zed_sn_blue           = LaunchConfiguration("zed_sn_blue")
    zed_sn_green          = LaunchConfiguration("zed_sn_green")
    zed_sn_red            = LaunchConfiguration("zed_sn_red")
    zed_sn_pink           = LaunchConfiguration("zed_sn_pink")
    
    ouster_host           = LaunchConfiguration("ouster_host")
    udp_dest              = LaunchConfiguration("udp_dest")
    viz                   = LaunchConfiguration("viz")
    robot_name            = LaunchConfiguration("robot_name")

    # ------------------------------------------------------------------ #
    #  Static TF publishers                                              #
    #                                                                    #
    #  TODO: update x/y/z offsets to match physical mount on catabot.    #
    # ------------------------------------------------------------------ #
    lidar_tf = Node(
        condition=IfCondition(use_lidar),
        package="tf2_ros",
        executable="static_transform_publisher",
        name="lidar_tf_broadcaster",
        arguments=[
            "--x", "-0.8", "--y", "0", "--z", "0.515",
            "--roll", "0", "--pitch", "0", "--yaw", "0",
            "--frame-id", "base_link",
            "--child-frame-id", "os_sensor",  # ouster_ros ROS2 frame name
        ],
    )

    surfcam_tf = Node(
        condition=IfCondition(use_surface_camera),
        package="tf2_ros",
        executable="static_transform_publisher",
        name="surfcam_tf_broadcaster",
        arguments=[
            "--x", "-0.8", "--y", "0", "--z", "0.4",
            "--roll", "0", "--pitch", "0", "--yaw", "0",
            "--frame-id", "base_link",
            "--child-frame-id", "surface_cam",
        ],
    )

    # ------------------------------------------------------------------ #
    #  Mavros                                                            #
    # ------------------------------------------------------------------ #
    mavros_group = GroupAction(
        condition=IfCondition(use_pixhawk),
        actions=[
            IncludeLaunchDescription(
                AnyLaunchDescriptionSource([
                    PathJoinSubstitution([FindPackageShare("catabot_bringup"), "launch", "apm.launch"])
                ]),
                launch_arguments={"fcu_url": usb_pixhawk}.items(),
            )
        ],
    )

    # ------------------------------------------------------------------ #
    #  miniAHRS                                                          #
    #  serial:/dev/ttyUSB0:921600.                                       #
    # ------------------------------------------------------------------ #
    miniahrs_group = GroupAction(
        condition=IfCondition(use_miniAHRS),
        actions=[
            PushRosNamespace('miniAHRS'),
            IncludeLaunchDescription(
                AnyLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare("inertiallabs_ins"), "launch", "ins.launch"
                    ])
                ]),
                launch_arguments={
                    "ins_url":           miniahrs_url,
                    "ins_output_format": ins_output_format,
                }.items(),
            ),
        ],
    )

    # ------------------------------------------------------------------ #
    #  ZED X Camera                                                      #
    #  publish_tf=true   to ZED publishes odom to zed_camera_link        #
    #  publish_map_tf    to ZED publishes map  to odom                   #
    #  publish_imu_tf    to ZED publishes imu link TF                    #
    # ------------------------------------------------------------------ #
    def _zed_include(namespace, serial_number, use_condition):
        return GroupAction(
            condition=IfCondition(use_condition),
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([
                        PathJoinSubstitution([
                            FindPackageShare("zed_wrapper"), "launch", "zed_camera.launch.py"
                        ])
                    ]),
                    launch_arguments={
                        "namespace":      namespace,
                        "camera_model":   zed_camera_model,
                        "serial_number":  serial_number,
                        "publish_tf":     zed_publish_tf,
                        "publish_map_tf": zed_publish_map_tf,
                        "publish_imu_tf": zed_publish_imu_tf,
                        "container_name": "",   
                    }.items(),
                ),
            ],
        )

    zed_blue  = _zed_include("blue",  zed_sn_blue,  use_zed_blue)
    zed_green = _zed_include("green", zed_sn_green, use_zed_green)
    zed_red   = _zed_include("red",   zed_sn_red,   use_zed_red)
    zed_pink  = _zed_include("pink",  zed_sn_pink,  use_zed_pink)

    # ------------------------------------------------------------------ #
    #  Ouster LiDAR                                                      #
    # ------------------------------------------------------------------ #
    ouster_group = GroupAction(
        condition=IfCondition(lidar_ouster),
        actions=[
            IncludeLaunchDescription(
                #PythonLaunchDescriptionSource([
                AnyLaunchDescriptionSource([
                    PathJoinSubstitution([
                        #FindPackageShare("ouster_ros"), "launch", "driver.launch.py"
                        FindPackageShare("ouster_ros"), "launch", "sensor.launch.xml"
                    ])
                ]),
                launch_arguments={
                    "sensor_hostname": ouster_host,
                    "udp_dest":        udp_dest,
                    "timestamp_mode":  "TIME_FROM_ROS_TIME",
                    "viz":             viz,
                }.items(),
            )
        ],
    )

    # Velodyne fallback; use_lidar:=true, lidar_ouster:=false
    # TODO: verify velodyne_pointcloud ROS2 launch file path
    velodyne_group = GroupAction(
        condition=UnlessCondition(lidar_ouster),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare("velodyne_pointcloud"), "launch", "VLP16_points.launch.py"
                    ])
                ]),
                launch_arguments={
                    "calibration": PathJoinSubstitution([
                        FindPackageShare("velodyne_pointcloud"), "params", "VLP16db.yaml"
                    ])
                }.items(),
            )
        ],
    )

    lidar_group = GroupAction(
        condition=IfCondition(use_lidar),
        actions=[ouster_group, velodyne_group],
    )

    # ------------------------------------------------------------------ #
    #  USB cameras                                                       #
    # ------------------------------------------------------------------ #
    surface_cam_group = GroupAction(
        condition=IfCondition(use_surface_camera),
        actions=[
            TimerAction(
                period=surf_delay,
                actions=[
                    Node(
                        package="usb_cam",
                        executable="usb_cam_node_exe",
                        name="usb_cam_surface",
                        namespace="usb_cam_surface",
                        parameters=[{
                            "video_device":    usb_surface,
                            "image_width":     640,
                            "image_height":    480,
                            "pixel_format":    "yuyv",
                            "auto_focus":      False,
                            "framerate":       30.0,
                            "camera_name":     "surface_cam",
                            "camera_frame_id": "surface_cam",
                            "autoexposure":    True,
                        }],
                    )
                ],
            )
        ],
    )

    underwater_cam_group = GroupAction(
        condition=IfCondition(use_underwater_camera),
        actions=[
            TimerAction(
                period=uw_delay,
                actions=[
                    Node(
                        package="usb_cam",
                        executable="usb_cam_node_exe",
                        name="usb_cam_underwater",
                        parameters=[{
                            "video_device":    usb_underwater,
                            "image_width":     640,
                            "image_height":    360,
                            "pixel_format":    "yuyv",
                            "auto_focus":      False,
                            "framerate":       30.0,
                            "camera_frame_id": "underwater_cam",
                            "autoexposure":    False,
                        }],
                    )
                ],
            )
        ],
    )

    # ------------------------------------------------------------------ #
    #  legacy sensors                                                    #
    # ------------------------------------------------------------------ #
    sonde_group = GroupAction(
        condition=IfCondition(use_sonde),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare("ysi_exo"), "launch", "ysi_exo.launch.py"
                    ])
                ]),
                launch_arguments={"serial_port": usb_sonde}.items(),
            )
        ],
    )

    sonar_group = GroupAction(
        condition=IfCondition(use_sonar),
        actions=[
            Node(
                package="nmea_depth_transducer",
                executable="nmea_depth_transducer_node",
                name="nmea_depth_transducer",
                parameters=[{"serial_port": usb_sonar}],
            )
        ],
    )

    sidescan_group = GroupAction(
        condition=IfCondition(use_sidescan),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare("imagenex_sidescan"), "launch", "sidescansonar.launch.py"
                    ])
                ]),
            )
        ],
    )

    # ------------------------------------------------------------------ #
    #  Logger                                                             #
    # ------------------------------------------------------------------ #
    logger_group = GroupAction(
        condition=IfCondition(use_logging),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare("catabot_bringup"), "launch", "logger.launch.py"
                    ])
                ]),
            )
        ],
    )

    # ----------------------------------------------------------------- #
    #  Assemble everything under robot namespace                        #
    # ----------------------------------------------------------------- #
    namespaced = GroupAction(actions=[
        # PushRosNamespace(robot_name),

        # TF static transforms 
        lidar_tf,
        surfcam_tf,

        # sensors 
        mavros_group,
        miniahrs_group,
        zed_blue,
        zed_green,
        zed_red,
        zed_pink,
        lidar_group,

        # legacy
        surface_cam_group,
        underwater_cam_group,
        sonde_group,
        sonar_group,
        sidescan_group,

        # Logging
        logger_group,
    ])

    return LaunchDescription(args + [namespaced])
