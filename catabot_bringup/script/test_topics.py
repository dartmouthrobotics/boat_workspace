#!/usr/bin/env python

import rospy
import rostopic
import rosnode

#TODO topics to check in a configuration file
topics_to_check = [
    "mavros/vfr_hud",
    "ouster/lidar_packets",
    "usb_cam_surface/image_raw/compressed",
    "imagenex896/range",
    "gps_converted_odom"
        ]

# partial matching works
nodes_to_check = [
        "record"
        ]

rospy.init_node('test_topics')

r = rostopic.ROSTopicHz(-1)
ns = rospy.get_namespace()
topics_up = []
topics_down = []
for topic_name in topics_to_check:
    topic_name_with_ns = ns + topic_name
    exec("rospy.Subscriber('" + topic_name_with_ns + "', rospy.AnyMsg, r.callback_hz, callback_args='" + topic_name_with_ns + "')")
    start_time = rospy.get_time()
    topic_frequency = None
    while not rospy.is_shutdown() and rospy.get_time() - start_time < 5: # TODO parameter
        topic_frequency = r.get_hz(topic_name_with_ns) 
        rospy.sleep(0.1)
        if topic_frequency and topic_frequency[0] > 0:
            topics_up.append(topic_name)
            break
    if topic_frequency is None:
        topics_down.append(topic_name)

if topics_down:
    rospy.logerr("some topics up {}, some down {}".format(topics_up, topics_down))
else:
    rospy.loginfo("all topics up")

running_nodes = rosnode.get_node_names()
checked_running_node = []
checked_not_running_node = []
for n in nodes_to_check:
    for r in running_nodes:
        if n in r:
            checked_running_node.append(n)
            break
    if checked_running_node and n != checked_running_node[-1]:
        checked_not_running_node.append(n)
if checked_not_running_node:
    rospy.logerr("some nodes up {}, some down {}".format(checked_running_node, checked_not_running_node))
else:
    rospy.loginfo("all nodes up")