#!/usr/bin/env python
# encoding=utf8
from __future__ import print_function
import rospy
import mavros

from mavros_msgs.srv import *
from mavros.utils import *
from mavros_msgs.srv import CommandBool, SetMode, StreamRate, StreamRateRequest, MessageInterval
from timeit import default_timer as timer
from std_msgs.msg import Float64

class Catabot:
    def __init__(self):
        self.arming_status = False
        self.start_time = None
        self.end_time = None
        self.rate = rospy.Rate(10)
        self.direction_input = None
        self.TEST_TIME = None
        self.publisher_right = rospy.Publisher("/catabot/servo/PWM_right", Float64, queue_size=10)
        self.publisher_left = rospy.Publisher("/catabot/servo/PWM_left", Float64, queue_size=10)
        self.subscriber_compass = rospy.Subscriber("/mavros/global_position/compass_hdg", Float64, self.callback_compass)
        self.turning_time = []
        self.initial_heading = None
        self.publisher_compass_turn = rospy.Publisher("/catabot/compass_turn/time", Float64, queue_size=10)
        self.right_motor = 1500
        self.left_motor = 1500

    def callback_compass(self, msg):
        if self.initial_heading is not None:
            hdg_difference = abs(self.initial_heading - msg.data)
            if self.start_time is not None:
                if hdg_difference >= 90:
                    now_time = timer()
                    time_difference = now_time - self.start_time
                    self.turning_time.append(time_difference)
                    time_msg = Float64()
                    time_msg.data = time_difference
                    self.publisher_compass_turn.publish(time_msg)

                elif hdg_difference >= 180:
                    now_time = timer()
                    time_difference = now_time - self.start_time
                    self.turning_time.append(time_difference)
                    time_msg = Float64()
                    time_msg.data = time_difference
                    self.publisher_compass_turn.publish(time_msg)

                elif hdg_difference >= 270:
                    now_time = timer()
                    time_difference = now_time - self.start_time
                    self.turning_time.append(time_difference)
                    time_msg = Float64()
                    time_msg.data = time_difference
                    self.publisher_compass_turn.publish(time_msg)


                elif len(self.turning_time) == 3 and hdg_difference >=0:
                    now_time = timer()
                    time_difference = now_time -self.start_time
                    self.turning_time.append(time_difference)
                    time_msg = Float64()
                    time_msg.data = time_difference
                    self.publisher_compass_turn.publish(time_msg)

        else:
            self.initial_heading = msg.data
            time_msg = Float64()
            time_msg.data = 0
            self.publisher_compass_turn.publish(time_msg)
            print("initial heading is", self.initial_heading)

    def setArm(self):
        rospy.wait_for_service('/mavros/cmd/arming')
        try:
            armService = rospy.ServiceProxy('/mavros/cmd/arming', mavros_msgs.srv.CommandBool)
            self.arming_status = True
            armService(True)
        except rospy.ServiceException, e:
            print("Service arm call failed:", e)

    def setDisarm(self):
        rospy.wait_for_service('/mavros/cmd/arming')
        try:
            armService = rospy.ServiceProxy('/mavros/cmd/arming', mavros_msgs.srv.CommandBool)
            self.arming_status = False
            armService(False)
        except rospy.ServiceException, e:
            print("Service arm call failed:", e)

    def myController_start(self):
        rospy.wait_for_service('/mavros/cmd/command')
        '''
        if self.direction_input == 1:
            right_motor = 1800
            left_motor = 1200
        elif self.direction_input == 2:
            right_motor = 1390
            left_motor =1610
        elif self.direction_input == 3:
            right_motor = 1800
            left_motor = 1250
        elif self.direction_input == 4:
            right_motor = 1550
            left_motor = 1650
        else:
            right_motor = 1500
            left_motor = 1500
        '''
        if right_input and left_input:
            self.right_motor = right_input
            self.left_motor = left_input

        try:
            servoControlService = rospy.ServiceProxy('/mavros/cmd/command', mavros_msgs.srv.CommandLong)
            servoControlService(command = 183, param1 = 1, param2 = self.right_motor)
            servoControlService(command = 183, param1 = 3, param2 = self.left_motor)
            #servo_right_msg = Float64()
            #servo_left_msg = Float64()
            #servo_right_msg.data = right_motor
            #servo_left_msg.data = left_motor
            #self.publisher_right.publish(servo_right_msg)
            #self.publisher_left.publish(servo_left_msg)
            print("SERVO RIGHT: ", self.right_motor, "/", "SERVO LEFT", self.left_motor)

        except rospy.ServiceException, e:
            print("Service servo control call failed: ", e)

    def myController_stop(self):
        rospy.wait_for_service('/mavros/cmd/command')
        try:
            self.right_motor = 1500
            self.left_motor =1500
            servoControlService = rospy.ServiceProxy('/mavros/cmd/command', mavros_msgs.srv.CommandLong)
            servoControlService(command = 183, param1 = 1, param2 = self.right_motor)
            servoControlService(command = 183, param1 = 3, param2 = self.left_motor)
        except rospy.ServiceException, e:
            print("Service servo control call failed: ", e)

    def stopwatch(self):
        if self.start_time is None:
            self.start_time = timer()
            self.setArm()
            print("Robot armed / start moving")
            self.myController_start()

        else:
            current_time = timer()
            if current_time - self.start_time > self.TEST_TIME:
                self.setDisarm()
                self.myController_stop()
                print("test finished")
                rospy.signal_shutdown("End") 


def main():
   global right_input, left_input
   right_input = input("Right_motor PWM: ")
   left_input = input("left_motor PWM: ")
   # direction_input= input("Direction for test - 1: Forward / 2: Backward / 3: Right / 4: Left ")
   TEST_TIME = input("How many seconds?: ")
   catabot = Catabot()
   #catabot.direction_input = direction_input
   catabot.TEST_TIME = TEST_TIME
   while not rospy.is_shutdown():
       servo_right_msg = Float64()
       servo_left_msg = Float64()
       servo_right_msg.data = catabot.right_motor
       servo_left_msg.data = catabot.left_motor
       catabot.publisher_right.publish(servo_right_msg)
       catabot.publisher_left.publish(servo_left_msg)
       catabot.stopwatch()
       catabot.rate.sleep()

if __name__ == '__main__':
   rospy.init_node('catabot_controller_node', anonymous=True)
   #rospy.Subscriber("/mavros/global_position/compass_hdg", std_msgs/Float64, compassCallback)
   #velocity_pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped, queue_size=10)
   main()