#!/usr/bin/env python

import rosbag
def main():
    bag = rosbag.Bag('catabot_2019-09-24-20-53-28.bag')

    for topic, msg, t in bag.read_messages(topics=['/mavros/imu/data']):
        print msg
    #bag.close()

if __name__ == '__main__':
    main()