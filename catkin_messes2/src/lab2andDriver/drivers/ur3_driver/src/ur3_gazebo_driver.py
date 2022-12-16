#!/usr/bin/env python

import rospy
import random
import math

# UR3 messages
from ur3_driver.msg import command
from ur3_driver.msg import position
from ur3_driver.msg import gripper_input
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from std_msgs.msg import Bool
from std_srvs.srv import Empty
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Point
from gazebo_msgs.msg import LinkStates

gazebo_pos = None
gripper_is_on = False

def get_duration(dest, vel):
    global gazebo_pos
    if not gazebo_pos:
        return rospy.Time(0.0001)
    max_duration = -1
    for joint_idx in range(6):
        curr_duration = abs((dest[joint_idx] - gazebo_pos[joint_idx]) / vel)
        if curr_duration > max_duration:
            max_duration = curr_duration
    if max_duration < 0.0001:
        max_duration = 0.0001
    return rospy.Time(max_duration)

# Callback function for the subscriber that subscribe to "ur3/command" topic.
def ctrl_sub_callback(data):
    global gripper_is_on

    # Joint Trajectory Setup
    jt = JointTrajectory()
    jt.joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint',
    'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
    pt = JointTrajectoryPoint()
    pt.positions = list(data.destination)
    pt.positions[0] -= math.pi
    pt.velocities = [0.0] * 6
    pt.accelerations = [0.0] * 6
    pt.time_from_start = get_duration(data.destination, data.v)
    jt.points = [pt]

    # Vacuum Gripper
    
    if data.io_0 and (not gripper_is_on):
        gripper_on_srv = rospy.ServiceProxy('/gripper/on', Empty)
        gripper_on_srv()
        gripper_is_on = True
    elif (not data.io_0) and gripper_is_on:
        gripper_off_srv = rospy.ServiceProxy('/gripper/off', Empty)
        gripper_off_srv()
        gripper_is_on = False

    cmd_pub.publish(jt)


# Callback function for the subscriber that subscribe to "joint_states"
def gazebo_pos_sub_callback(data):
    global gazebo_pos
    gazebo_pos = list(data.position)
    gazebo_pos = [gazebo_pos[2] + math.pi, gazebo_pos[1], gazebo_pos[0],
                  gazebo_pos[3], gazebo_pos[4], gazebo_pos[5]]
    pos_msg = position()
    pos_msg.position = gazebo_pos
    pos_msg.isReady = True
    pos_pub.publish(pos_msg)

# Callback function for the subscriber that subscribe to "gripper/grasping"
def gripper_sub_callback(data):
    global gripper_is_on
    g_in = gripper_input()
    if gripper_is_on:
        if data.data:
            g_in.DIGIN = 1
            g_in.AIN0 = 1.89 + 0.02 * random.random() 
        else:
            g_in.DIGIN = 0
            g_in.AIN0 = 1.45 + 0.02 * random.random()
    else:
        g_in.DIGIN = 0
        g_in.AIN0 = 1.05 + 0.02 * random.random()
    g_in.AIN1 = 0.00470
    gripper_input_pub.publish(g_in)

# Callback function for the subscriber that subscribe to "gazebo/link_states"
def link_states_sub_callback(data):
    for i in range(len(data.name)):
        if data.name[i] == 'robot::vacuum_gripper':
            gripper_pose = data.pose[i]
            gripper_position_pub.publish(gripper_pose.position)
            return

if __name__ == '__main__':
    # Initialize ROS node
    rospy.init_node('ur3_gazebo_driver', anonymous=True)
    rate = rospy.Rate(10)

    rospy.Subscriber('joint_states', JointState, gazebo_pos_sub_callback)
    rospy.Subscriber('ur3/command', command, ctrl_sub_callback)
    rospy.Subscriber('gripper/grasping', Bool, gripper_sub_callback)
    rospy.Subscriber('gazebo/link_states', LinkStates, link_states_sub_callback)

    pos_pub = rospy.Publisher('ur3/position', position, queue_size=10)
    cmd_pub = rospy.Publisher('arm_controller/command', JointTrajectory, queue_size=10)
    gripper_input_pub = rospy.Publisher('ur3/gripper_input', gripper_input, queue_size=10)
    gripper_position_pub = rospy.Publisher('gripper/position', Point, queue_size=10)

    try:
        while not rospy.is_shutdown():

            rate.sleep()
    except rospy.ROSInterruptException:
        pass
