#!/usr/bin/env python
# Send simState data as a UDP stream, packed as an FG_FDM object
# Based on runsim.py by Ardupilot Tools git

import roslib
import sys
import rospy
from pymavlink.rotmat import Vector3, Matrix3
from geometry_msgs.msg import Vector3 as RosVector3
import tf.transformations
from rosgraph_msgs.msg import Clock
from last_letter_msgs.msg import SimStates, SimPWM, Environment

import socket, struct, errno

def interpret_address(addrstr):
    '''interpret a IP:port string'''
    a = addrstr.split(':')
    a[1] = int(a[1])
    return tuple(a)

class fdmState(object):
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0
        self.heading = 0
        self.velocity = Vector3()
        self.accel = Vector3()
        self.gyro = Vector3()
        self.attitude = Vector3()
        self.airspeed = 0
        self.dcm = Matrix3()
        self.timestamp_us = 1

def state_callback(state):
	global fdm
        fdm.latitude = state.geoid.latitude
	fdm.longitude = state.geoid.longitude
	fdm.altitude = state.geoid.altitude
        fdm.velocity = Vector3(state.geoid.velocity.x,
                               state.geoid.velocity.y,
                               state.geoid.velocity.z)

	(yaw, pitch, roll) = tf.transformations.euler_from_quaternion([state.pose.orientation.x,
                                                                       state.pose.orientation.y,
                                                                       state.pose.orientation.z,
                                                                       state.pose.orientation.w],'rzyx')
        fdm.attitude = Vector3(roll, pitch, yaw)
        fdm.gyro = Vector3(state.velocity.angular.x, state.velocity.angular.y, state.velocity.angular.z)
	fdm.dcm.from_euler(roll, pitch, yaw)

def accel_callback(accel):
	global fdm
        accel = Vector3(accel.x, accel.y, accel.z)
        accel = fdm.dcm * accel
        accel.z -= 9.80665
        accel = fdm.dcm.transposed() * accel
        fdm.accel = accel

def env_callback(environment):
	global fdm
        wind = Vector3(environment.wind.x, environment.wind.y, environment.wind.z)
        fdm.airspeed = (fdm.velocity - wind).length()

def clock_callback(clock):
	global fdm
        fdm.timestamp_us = int(clock.clock.secs * 1e6 + clock.clock.nsecs/1000)


def receive_input(sock, fdm, pub):
    buf = sock.recv(32)
    if len(buf) != 32:
        return False
    servos = struct.unpack('<16H', buf)
    ctrls = SimPWM()
    for i in range(6):
        ctrls.value[i] = servos[i]
    pub.publish(ctrls)
    return True

def send_output(sock, fdm):
    '''send output to SITL'''
    buf = struct.pack('<Q17d',
                      fdm.timestamp_us,
                      fdm.latitude,
                      fdm.longitude,
                      fdm.altitude,
                      fdm.heading,
                      fdm.velocity.x,
                      fdm.velocity.y,
                      fdm.velocity.z,
                      fdm.accel.x,
                      fdm.accel.y,
                      fdm.accel.z,
                      fdm.gyro.x,
                      fdm.gyro.y,
                      fdm.gyro.z,
                      fdm.attitude.x,
                      fdm.attitude.y,
                      fdm.attitude.z,
                      fdm.airspeed)
    sock.send(buf)

###############
## Main Program
###############

if __name__ == '__main__':
    fdm = fdmState()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 9002))
    sock.connect(('127.0.0.1', 9003))
    
    rospy.init_node('fdmUDPSend')
    rospy.Subscriber('states', SimStates, state_callback, queue_size=1)
    rospy.Subscriber('linearAcc', RosVector3, accel_callback, queue_size=1)
    rospy.Subscriber('environment', Environment, env_callback, queue_size=1)
    rospy.Subscriber('/clock', Clock, clock_callback, queue_size=1)
    pub = rospy.Publisher('ctrlPWM',SimPWM, queue_size=10)
    
    timer = rospy.Rate(500)
    rospy.loginfo('fdmUDPSend node up')
    
    while not rospy.is_shutdown():
        try:
            if receive_input(sock, fdm, pub):
                send_output(sock, fdm)
        except socket.error as e:
            if e.errno not in [ errno.ECONNREFUSED ]:
                print("error in sending: %s" % e)
                raise
        timer.sleep()
    print "this node is dead"
