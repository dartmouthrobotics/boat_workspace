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
from launch.launch_description_sources import PythonLaunchDescriptionSource
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
        DeclareLaunchArgument("use_lidar",               default_value="true"),
        DeclareLaunchArgument("lidar_ouster",            default_value="true"),
        DeclareLaunchArgument("use_surface_camera",      default_value="true"),
        DeclareLaunchArgument("use_underwater_camera",   default_value="false"),
        DeclareLaunchArgument("use_sonde",               default_value="false"),
        DeclareLaunchArgument("use_sonar",               default_value="false"),
        DeclareLaunchArgument("use_sidescan",            default_value="false"),
        DeclareLaunchArgument("use_logging",             default_value="true"),
        DeclareLaunchArgument("use_pixhawk",             default_value="true"),

        # time delays 
        DeclareLaunchArgument("usb_cam_node_start_delay",        default_value="3.0"),
        DeclareLaunchArgument("usb_cam_underwater_start_delay",  default_value="1.0"),

        # device paths
        DeclareLaunchArgument("usb_underwater", default_value="/dev/video2"),
        DeclareLaunchArgument("usb_surface",    default_value="/dev/video0"),
        DeclareLaunchArgument("usb_sonde",      default_value="/dev/ysi_sonde"),
        DeclareLaunchArgument("usb_sonar",      default_value="/dev/sonar"),
        DeclareLaunchArgument("usb_pixhawk",    default_value="udp://:14550@"),
        DeclareLaunchArgument("pixhawk_baudrate", default_value="57600"),

        # miscellaneous
        DeclareLaunchArgument("ouster_host",  default_value="os-122525001750.local"),
        DeclareLaunchArgument("udp_dest",     default_value="169.254.162.114"),
        DeclareLaunchArgument("lidar_mode",   default_value="1024x10"),
        DeclareLaunchArgument("viz",          default_value="false"),

        # robot namespace 
        DeclareLaunchArgument("robot_name",   default_value="robot_0"),
    ]

    # ------------------------------------------------------------------ #
    #  LaunchConfiguration                                               #
    # ------------------------------------------------------------------ #
    use_lidar             = LaunchConfiguration("use_lidar")
    lidar_ouster          = LaunchConfiguration("lidar_ouster")
    use_surface_camera    = LaunchConfiguration("use_surface_camera")
    use_underwater_camera = LaunchConfiguration("use_underwater_camera")
    use_sonde             = LaunchConfiguration("use_sonde")
    use_sonar             = LaunchConfiguration("use_sonar")
    use_sidescan          = LaunchConfiguration("use_sidescan")
    use_logging           = LaunchConfiguration("use_logging")
    use_pixhawk           = LaunchConfiguration("use_pixhawk")
    surf_delay            = LaunchConfiguration("usb_cam_node_start_delay")
    uw_delay              = LaunchConfiguration("usb_cam_underwater_start_delay")
    usb_surface           = LaunchConfiguration("usb_surface")
    usb_underwater        = LaunchConfiguration("usb_underwater")
    usb_sonde             = LaunchConfiguration("usb_sonde")
    usb_sonar             = LaunchConfiguration("usb_sonar")
    usb_pixhawk           = LaunchConfiguration("usb_pixhawk")
    ouster_host           = LaunchConfiguration("ouster_host")
    udp_dest              = LaunchConfiguration("udp_dest")
    viz                   = LaunchConfiguration("viz")
    robot_name            = LaunchConfiguration("robot_name")

    # ------------------------------------------------------------------ #
    #  Static TF publishers                                              #
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
            "--child-frame-id", "velodyne",
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
    #  Mavros                                                              #
    # TODO: confirm mavros ROS2 package name and launch file path.        #
    #       mavros has a ROS2 port; the launch file is typically           #
    #       mavros/launch/apm.launch.py  (PythonLaunchDescriptionSource)  #
    # ------------------------------------------------------------------ #
    mavros_group = GroupAction(
        condition=IfCondition(use_pixhawk),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([FindPackageShare("mavros"), "launch", "apm.launch.py"])
                ]),
                launch_arguments={"fcu_url": usb_pixhawk}.items(),
            )
        ],
    )

    # ------------------------------------------------------------------ #
    #  Sonde                                                               #
    # TODO: verify ysi_exo has a ROS2 port and .launch.py file.           #
    # ------------------------------------------------------------------ #
    sonde_group = GroupAction(
        condition=IfCondition(use_sonde),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([FindPackageShare("ysi_exo"), "launch", "ysi_exo.launch.py"])
                ]),
                launch_arguments={"serial_port": usb_sonde}.items(),
            )
        ],
    )

    # ------------------------------------------------------------------ #
    #  Sonar (depth transducer)                                            #
    # TODO: verify nmea_depth_transducer has a ROS2 port.                 #
    #       ROS2 nodes use parameters= dict instead of <param> tags.      #
    # ------------------------------------------------------------------ #
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

    # ------------------------------------------------------------------ #
    #  Lidar – Ouster                                                      #
    # TODO: ouster_ros ROS2 uses a composable node / different launch.    #
    #       Typical path: ouster_ros/launch/driver.launch.py              #
    #       timestamp_mode arg name may differ – verify with ouster_ros.  #
    # ------------------------------------------------------------------ #
    ouster_group = GroupAction(
        condition=IfCondition(lidar_ouster),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([FindPackageShare("ouster_ros"), "launch", "driver.launch.py"])
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

    # ------------------------------------------------------------------ #
    #  Lidar – Velodyne                                                    #
    # TODO: velodyne_pointcloud ROS2 launch file may differ in name/path. #
    # ------------------------------------------------------------------ #
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
    #  Surface camera (usb_cam ROS2)                                       #
    # usb_cam ROS2 node name is "usb_cam", executable "usb_cam_node".     #
    # Parameters are passed as a dict; launch-prefix sleep → TimerAction. #
    # ------------------------------------------------------------------ #
    surface_cam_node = Node(
        package="usb_cam",
        executable="usb_cam_node_exe",      # ROS2 usb_cam executable name
        name="usb_cam_surface",
        parameters=[{
            "video_device":    usb_surface,
            "image_width":     640,
            "image_height":    480,
            "pixel_format":    "yuyv",
            "auto_focus":      False,
            "framerate":       30.0,
            "camera_frame_id": "surface_cam",
            "autoexposure":    True,
        }],
    )

    surface_cam_group = GroupAction(
        condition=IfCondition(use_surface_camera),
        actions=[
            TimerAction(period=surf_delay, actions=[surface_cam_node])
        ],
    )

    # ------------------------------------------------------------------ #
    #  Underwater camera                                                   #
    # ------------------------------------------------------------------ #
    underwater_cam_node = Node(
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

    underwater_cam_group = GroupAction(
        condition=IfCondition(use_underwater_camera),
        actions=[
            TimerAction(period=uw_delay, actions=[underwater_cam_node])
        ],
    )

    # ------------------------------------------------------------------ #
    #  Sidescan sonar                                                      #
    # TODO: imagenex_sidescan ROS2 port required.                         #
    # ------------------------------------------------------------------ #
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
    #  Logger (ros2 bag)                                                   #
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

    # ------------------------------------------------------------------ #
    #  Wrap everything under the robot namespace                           #
    # ------------------------------------------------------------------ #
    namespaced = GroupAction(actions=[
        PushRosNamespace(robot_name),
        lidar_tf,
        surfcam_tf,
        mavros_group,
        sonde_group,
        sonar_group,
        lidar_group,
        surface_cam_group,
        underwater_cam_group,
        sidescan_group,
        logger_group,
    ])

    return LaunchDescription(args + [namespaced])
