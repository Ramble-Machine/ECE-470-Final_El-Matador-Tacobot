#!/usr/bin/env python

import sys
import copy
import time
import rospy
import os
import argparse
import copy
import time
import rospy
import rospkg
import numpy as np
import yaml
import sys
from lab2_header import *
import numpy as np
from lab5_header import *
from blob_search import *
from lab5_func import *
from gazebo_msgs.srv import SpawnModel
from gazebo_msgs.srv import DeleteModel
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Point
from geometry_msgs.msg import Quaternion

# ========================= Student's code starts here =========================

# Position for UR3 not blocking the camera
go_away = lab_invk(-50,-250,70, 0)
tothesky = [np.pi-0.01, -np.pi/2, 0, 0, 0, -np.pi/2]
# Store world coordinates of green and yellow blocks
global xw_yw_G, xw_yw_B, xw_yw_R
xw_yw_G = []
xw_yw_Y = []
xw_yw_R = []
xw_yw_B = []
xw_yw_O = []
# Any other global variable you want to define
# Hints: where to put the blocks?
blockrelease=[123.45*PI/180, -63.17*PI/180, 74.89*PI/180, -98.98*PI/180, -89.99*PI/180,60.14*PI/180]
#locations for first color

A1 = [119.05*PI/180.0, -48.07*PI/180.0, 107.47*PI/180.0, -155.08*PI/180.0, -82.03*PI/180.0, 134.68*PI/180.0]
A2 = [124.96*PI/180.0, -58.43*PI/180.0, 118.58*PI/180.0, -153.83*PI/180.0, -84.83*PI/180.0, 134.7*PI/180.0]
A3 = [124.54*PI/180.0, -47.06*PI/180.0, 90.47*PI/180.0, -134.21*PI/180.0, -80.51*PI/180.0, 134.69*PI/180.0]
A4 = [129.39*PI/180.0, -54.63*PI/180.0, 105.62*PI/180.0, -142.27*PI/180.0, -82.96*PI/180.0, 134.68*PI/180.0]
ASpots = [A1, A2, A3, A4]

#locations for second color
B1 = [135.90*PI/180.0, -28.00*PI/180.0, 55.41*PI/180.0, -125.14*PI/180.0, -82.98*PI/180.0, 134.71*PI/180.0]
B2 = [130.87*PI/180.0, -39.71*PI/180.0, 82.26*PI/180.0, -141.63*PI/180.0, -82.98*PI/180.0, 134.69*PI/180.0]
B3 = [141.10*PI/180.0, -31.64*PI/180.0, 64.36*PI/180.0, -124.82*PI/180.0, -82.99*PI/180.0, 134.73*PI/180.0]
B4 = [136.54*PI/180.0, -43.46*PI/180.0, 89.70*PI/180.0, -140.35*PI/180.0, -83.00*PI/180.0, 134.70*PI/180.0]
BSpots = [B1, B2, B3, B4]

# ========================= Student's code ends here ===========================

################ Pre-defined parameters and functions no need to change below ################

# 20Hz
SPIN_RATE = 20

# UR3 home location
home = lab_invk(250,-150,170,0)
# UR3 current position, using home position for initialization
current_position = copy.deepcopy(home)

thetas = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

digital_in_0 = 0
analog_in_0 = 0.0

suction_on = True
suction_off = False

current_io_0 = False
current_position_set = False

image_shape_define = False


"""
Whenever ur3/gripper_input publishes info this callback function is called.
"""
def input_callback(msg):

    global digital_in_0
    digital_in_0 = msg.DIGIN


"""
Whenever ur3/position publishes info, this callback function is called.
"""
def position_callback(msg):

    global thetas
    global current_position
    global current_position_set

    thetas[0] = msg.position[0]
    thetas[1] = msg.position[1]
    thetas[2] = msg.position[2]
    thetas[3] = msg.position[3]
    thetas[4] = msg.position[4]
    thetas[5] = msg.position[5]

    current_position[0] = thetas[0]
    current_position[1] = thetas[1]
    current_position[2] = thetas[2]
    current_position[3] = thetas[3]
    current_position[4] = thetas[4]
    current_position[5] = thetas[5]

    current_position_set = True


"""
Function to control the suction cup on/off
"""
def position_callback(msg):

    global thetas
    global current_position
    global current_position_set

    thetas[0] = msg.position[0]
    thetas[1] = msg.position[1]
    thetas[2] = msg.position[2]
    thetas[3] = msg.position[3]
    thetas[4] = msg.position[4]
    thetas[5] = msg.position[5]

    current_position[0] = thetas[0]
    current_position[1] = thetas[1]
    current_position[2] = thetas[2]
    current_position[3] = thetas[3]
    current_position[4] = thetas[4]
    current_position[5] = thetas[5]

    current_position_set = True


def gripper(pub_cmd, loop_rate, io_0):

    global SPIN_RATE
    global thetas
    global current_io_0
    global current_position

    error = 0
    spin_count = 0
    at_goal = 0

    current_io_0 = io_0

    driver_msg = command()
    driver_msg.destination = current_position
    driver_msg.v = 1.0
    driver_msg.a = 1.0
    driver_msg.io_0 = io_0
    pub_cmd.publish(driver_msg)

    while(at_goal == 0):

        if( abs(thetas[0]-driver_msg.destination[0]) < 0.0005 and \
            abs(thetas[1]-driver_msg.destination[1]) < 0.0005 and \
            abs(thetas[2]-driver_msg.destination[2]) < 0.0005 and \
            abs(thetas[3]-driver_msg.destination[3]) < 0.0005 and \
            abs(thetas[4]-driver_msg.destination[4]) < 0.0005 and \
            abs(thetas[5]-driver_msg.destination[5]) < 0.0005 ):

            at_goal = 1

        loop_rate.sleep()

        if(spin_count >  SPIN_RATE*5):

            pub_cmd.publish(driver_msg)
            rospy.loginfo("Just published again driver_msg")
            spin_count = 0

        spin_count = spin_count + 1

    return error


def move_arm(pub_cmd, loop_rate, dest, vel, accel):

    global thetas
    global SPIN_RATE

    error = 0
    spin_count = 0
    at_goal = 0

    driver_msg = command()
    driver_msg.destination = dest
    driver_msg.v = vel
    driver_msg.a = accel
    driver_msg.io_0 = current_io_0
    pub_cmd.publish(driver_msg)

    loop_rate.sleep()
    print(dest)
    while(at_goal == 0):

        if( abs(thetas[0]-driver_msg.destination[0]) < 0.0005 and \
            abs(thetas[1]-driver_msg.destination[1]) < 0.0005 and \
            abs(thetas[2]-driver_msg.destination[2]) < 0.0005 and \
            abs(thetas[3]-driver_msg.destination[3]) < 0.0005 and \
            abs(thetas[4]-driver_msg.destination[4]) < 0.0005 and \
            abs(thetas[5]-driver_msg.destination[5]) < 0.0005 ):

            at_goal = 1
            #rospy.loginfo("Goal is reached!")

        loop_rate.sleep()

        if(spin_count >  SPIN_RATE*5):

            pub_cmd.publish(driver_msg)
            rospy.loginfo("Just published again driver_msg")
            spin_count = 0

        spin_count = spin_count + 1

    return error


################ Pre-defined parameters and functions no need to change above ################


def move_block(pub_cmd, loop_rate, start_loc, end_loc):
    global Q
    global go_away
    global current_io_0
    global succ
    x=lab_invk(end_loc[0],end_loc[1],100, 0)
    y=lab_invk(end_loc[0],end_loc[1],100, 0)
    move_arm(pub_cmd, loop_rate, x, 4,4 )
    gripper(pub_cmd, loop_rate, 1)
    time.sleep(1.0)
    if (succ==0):
        print("you iadhgifgiufwij fulsjvko idipt it BROKE you isditgujioer!!!!!!!!!!!!#@@! @# ~$!@@@@@@@@@@@@@@")
    else: 
        move_arm(pub_cmd, loop_rate, go_away, 4,4 )
        shakeyshakey(pub_cmd, loop_rate, y)
    gripper(pub_cmd, loop_rate, 0)
    time.sleep(1.0)
    move_arm(pub_cmd, loop_rate, go_away, 4,4 )
    ### Hint: Use the Q array to map out your towers by location and "height".
    return error
def shakeyshakey(pub_cmd,loop_rate, y):
    move_arm(pub_cmd, loop_rate, y, 4,4 )
    try:
        time.sleep(0.2)
        y[3]=y[3]+np.pi/8
        move_arm(pub_cmd, loop_rate, y, 4,4 )
    except:
        try:
            y[3]=y[3]-np.pi/8
            time.sleep(0.2)
            move_arm(pub_cmd, loop_rate, y, 4,4 )
            y[3]=y[3]+np.pi/8
            move_arm(pub_cmd, loop_rate, y, 4,4 )
        except:
            "poop"
    print("may or may not work")
    try: 
        y[3]=y[3]-np.pi/8
        time.sleep(0.2)
        move_arm(pub_cmd, loop_rate, y, 4,4 )
        y[3]=y[3]+np.pi/8
        move_arm(pub_cmd, loop_rate, y, 4,4 )
    except:
        "poop"
    return error

class ImageConverter:

    def __init__(self, SPIN_RATE):

        self.bridge = CvBridge()
        self.image_pub = rospy.Publisher("/image_converter/output_video", Image, queue_size=10)
        self.image_sub = rospy.Subscriber("/cv_camera_node/image_raw", Image, self.image_callback)
        self.loop_rate = rospy.Rate(SPIN_RATE)

        # Check if ROS is ready for operation
        while(rospy.is_shutdown()):
            print("ROS is shutdown!")


    def image_callback(self, data):

        global xw_yw_G # store found green blocks in this list
        global xw_yw_Y # store found yellow blocks in this list
        global xw_yw_O
        global xw_yw_B
        global xw_yw_R

        try:
          # Convert ROS image to OpenCV image
            raw_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        cv_image = cv2.flip(raw_image, -1)
        cv2.line(cv_image, (0,50), (640,50), (0,0,0), 5)

        # You will need to call blob_search() function to find centers of green blocks
        # and yellow blocks, and store the centers in xw_yw_G & xw_yw_Y respectively.

        # If no blocks are found for a particular color, you can return an empty list,
        # to xw_yw_G or xw_yw_Y.

        # Remember, xw_yw_G & xw_yw_Y are in global coordinates, which means you will
        # do coordinate transformation in the blob_search() function, namely, from
        # the image frame to the global world frame.

        xw_yw_G = blob_search(cv_image, "green")
        #xw_yw_O = blob_search(cv_image, "orange")
        xw_yw_R = blob_search(cv_image, "red")
        xw_yw_B = blob_search(cv_image, "blue")
        #xw_yw_Y = blob_search(cv_image, "yellow")
def otherside(ang):
    return [-ang[0], ang[1], ang[2], ang[3], ang[4], ang[5]]

"""
Program run from here
"""
def main():

    global go_away
    global xw_yw_R
    global xw_yw_G
    global xw_yw_O
    global xw_yw_B

    # global variable1
    # global variable2

    # Initialize ROS node
    rospy.init_node('lab5node')

    # Initialize publisher for ur3/command with buffer size of 10
    pub_command = rospy.Publisher('ur3/command', command, queue_size=10)

    # Initialize subscriber to ur3/position & ur3/gripper_input and callback fuction
    # each time data is published
    sub_position = rospy.Subscriber('ur3/position', position, position_callback)
    sub_input = rospy.Subscriber('ur3/gripper_input', gripper_input, input_callback)
    
    # Check if ROS is ready for operation
    while(rospy.is_shutdown()):
        print("ROS is shutdown!")
    ic = ImageConverter(SPIN_RATE)
    time.sleep(5)

    GreenPos= xw_yw_G
    Redpos= xw_yw_R
    BluePos = xw_yw_B
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    #print(GreenPos)
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    #try:
        #bwomp=lab_invk([xw_yw_G])
    #except:
    #    try:
    #        bwomp=lab_invk([GreenPos[0], GreenPos[1],90,0])
    #    except:
    #        print("cant find it lol")
    # Initialize the rate to publish to ur3/command
    bwomp=lab_invk(250,0,30,0)
    bwompabove=lab_invk(250, 0,250,0)
    loop_rate = rospy.Rate(SPIN_RATE)
    gripper(pub_command, loop_rate, False)
    move_arm(pub_command, loop_rate, bwompabove, 3, 2)
    time.sleep(1)
    gripper(pub_command, loop_rate, True)
    vel = 4.0
    accel = 4.0
    for i in range(0,200):
        gripper(pub_command, loop_rate, True)
        move_arm(pub_command, loop_rate, bwompabove, vel, accel)
        move_arm(pub_command, loop_rate, bwomp, vel, 2)
        time.sleep(1)
        move_arm(pub_command, loop_rate, bwompabove, vel, 2)
        gripper(pub_command, loop_rate, False)
        time.sleep(1)
    

    # ========================= Student's code starts here =========================

    """
    Hints: use the found xw_yw_G, xw_yw_Y to move the blocks correspondingly. You will
    need to call move_block(pub_command, loop_rate, start_xw_yw_zw, target_xw_yw_zw, vel, accel)
    """



    # ========================= Student's code ends here ===========================

    move_arm(pub_command, loop_rate, go_away, vel, accel)
    rospy.loginfo("Task Completed!")
    print("Use Ctrl+C to exit program")
    rospy.spin()
def testmove():
    global tothesky
    global go_away
    global xw_yw_R
    global xw_yw_G
    global xw_yw_O
    global xw_yw_B

    # global variable1
    # global variable2
    
    # Initialize ROS node
    rospy.init_node('lab5node')

    # Initialize publisher for ur3/command with buffer size of 10
    pub_command = rospy.Publisher('ur3/command', command, queue_size=20)

    # Initialize subscriber to ur3/position & ur3/gripper_input and callback fuction
    # each time data is published
    sub_position = rospy.Subscriber('ur3/position', position, position_callback)
    sub_input = rospy.Subscriber('ur3/gripper_input', gripper_input, input_callback)

    # Check if ROS is ready for operation
    while(rospy.is_shutdown()):
        print("ROS is shutdown!")
    loop_rate = rospy.Rate(SPIN_RATE)
    tortillaloc = [0, -1.0051214616493602, 2.1617526550197788, -2.7274275201204183, -1.5707963267948966, 0.44143910730776303]
    move_arm(pub_command, loop_rate, tothesky, 4, 4)
    time.sleep(0.2)
    spawntortilla()
    time.sleep(1)
    ic = ImageConverter(SPIN_RATE)
    time.sleep(9)
    print("moving to green")
    movebowl(pub_command, loop_rate, xw_yw_G, tortillaloc, "meat")
    print("moving to blue")
    movebowl(pub_command, loop_rate, xw_yw_B, tortillaloc, "lettuce")
    print("moving to red")
    movebowl(pub_command, loop_rate, xw_yw_R, tortillaloc, "sourcream")
    print("taco 1 done")
    move_arm(pub_command, loop_rate, tothesky, 4, 4)
    time.sleep(0.2)
    spawntortilla2()
    time.sleep(1)
    print("moving to green")
    movebowl2(pub_command, loop_rate, xw_yw_G, tortillaloc, "meat")
    print("moving to blue")
    movebowl2(pub_command, loop_rate, xw_yw_B, tortillaloc, "lettuce")
    print("moving to red")
    movebowl2(pub_command, loop_rate, xw_yw_R, tortillaloc, "sourcream")
    print("enjoy your tacos!")
    rospy.loginfo("Task Completed!")
    print("Use Ctrl+C to exit program")
    rospy.spin()
def shakedabowl(pub_command, loop_rate, mid):
    left=[float(mid[0]-np.pi/8), mid[1], mid[2], mid[3], mid[4], mid[5]]
    right=[float(mid[0]+np.pi/8), mid[1], mid[2], mid[3], mid[4], mid[5]]
    move_arm(pub_command, loop_rate, mid, 1,1 )
    move_arm(pub_command, loop_rate, left, 2,1 )
    move_arm(pub_command, loop_rate, right, 2,1 )
    move_arm(pub_command, loop_rate, mid, 2,1 )
    move_arm(pub_command, loop_rate, left, 2,1 )
    move_arm(pub_command, loop_rate, right, 1,1 )
    move_arm(pub_command, loop_rate, mid, 1,1 )

def correctyaw(GreenPos):
    try:
        greenang=lab_invk(GreenPos[0][0],GreenPos[0][1],32,0)
        abovegreen=lab_invk(GreenPos[0][0],GreenPos[0][1],250,0)
        print("yaw 0")
    except:
        try:
            greenang=lab_invk(GreenPos[0][0],GreenPos[0][1],32,90)
            abovegreen=lab_invk(GreenPos[0][0],GreenPos[0][1],250,90)
            print("yaw 90")
        except:
            try:
                greenang=lab_invk(GreenPos[0][0],GreenPos[0][1],32,-90)
                abovegreen=lab_invk(GreenPos[0][0],GreenPos[0][1],250,-90)
                print("yaw -90")
            except:
                try:
                    greenang=lab_invk(GreenPos[0][0],GreenPos[0][1],32,180)
                    abovegreen=lab_invk(GreenPos[0][0],GreenPos[0][1],250,180)
                    print("yaw 180")
                except:
                    try:
                        greenang=lab_invk(GreenPos[0][0],GreenPos[0][1],32,-45)
                        abovegreen=lab_invk(GreenPos[0][0],GreenPos[0][1],250,-45)
                        print("yaw -45")
                    except:
                        try:
                            greenang=lab_invk(GreenPos[0][0],GreenPos[0][1],32,45)
                            abovegreen=lab_invk(GreenPos[0][0],GreenPos[0][1],250,45)
                            print("Yaw 45")
                        except:
                            try:
                                greenang=lab_invk(GreenPos[0][0],GreenPos[0][1],32,-135)
                                abovegreen=lab_invk(GreenPos[0][0],GreenPos[0][1],250,-135)

                                print("yaw -135")
                            except:
                                greenang=lab_invk(GreenPos[0][0],GreenPos[0][1],32,135)
                                abovegreen=lab_invk(GreenPos[0][0],GreenPos[0][1],250,135)
                                print("yaw 135")
    return greenang, abovegreen
def retang(ang1, ang2=tothesky):
    retang=[0,0,0,0,0,0]
    for i in range(0,6):
        retang[i]=(ang1[i]+ang2[i])/2
    return retang


def movebowl(pub_command, loop_rate, xw_yw_G, tortilla, foodspawn):
    greenang, abovegreen, = correctyaw(xw_yw_G)
    halfwayg2=retang(abovegreen)
    gripper(pub_command, loop_rate, True)
    move_arm(pub_command, loop_rate, abovegreen, 4, 4)

    move_arm(pub_command, loop_rate, greenang, 4, 4)
    time.sleep(1)
    move_arm(pub_command, loop_rate, abovegreen, 4, 4)
 


    shakedabowl(pub_command, loop_rate, [0,abovegreen[1],abovegreen[2],abovegreen[3],abovegreen[4], abovegreen[5]])
    time.sleep(0.2)
    foodspawner(foodspawn)
    print(foodspawn, " dropped")
    time.sleep(3)

    move_arm(pub_command, loop_rate, abovegreen, 4, 4)
    time.sleep(0.5)
    
    
    move_arm(pub_command, loop_rate, greenang, 4, 4)
    gripper(pub_command, loop_rate, False)
    print("bowl dropped")
    time.sleep(0.5)
    move_arm(pub_command, loop_rate, abovegreen, 4, 4)
    print("movement complete")
    time.sleep(3)
def movebowl2(pub_command, loop_rate, xw_yw_G, tortilla, foodspawn):
    greenang, abovegreen, = correctyaw(xw_yw_G)
    halfwayg2=retang(abovegreen)
    gripper(pub_command, loop_rate, True)
    move_arm(pub_command, loop_rate, abovegreen, 4, 4)

    move_arm(pub_command, loop_rate, greenang, 4, 4)
    time.sleep(1)
    move_arm(pub_command, loop_rate, abovegreen, 4, 4)
 


    shakedabowl(pub_command, loop_rate, [np.pi/2,abovegreen[1],abovegreen[2],abovegreen[3],abovegreen[4], abovegreen[5]])
    time.sleep(0.2)
    foodspawner2(foodspawn)
    print(foodspawn, " dropped")
    time.sleep(3)

    move_arm(pub_command, loop_rate, abovegreen, 4, 4)
    time.sleep(0.5)
    
    
    move_arm(pub_command, loop_rate, greenang, 4, 4)
    gripper(pub_command, loop_rate, False)
    print("bowl dropped")
    time.sleep(0.5)
    move_arm(pub_command, loop_rate, abovegreen, 4, 4)
    print("movement complete")
    time.sleep(3)

def foodspawner2(food):
    spawn = rospy.ServiceProxy('gazebo/spawn_urdf_model', SpawnModel)
    if (food=="meat"):
        path2=open('/home/ur3/Downloads/tacostuff/meatmodel.urdf', 'r').read()
        spawn("meat2", path2, 'meat2', Pose(Point(-0.05, -0.35, 1.06), Quaternion(0,0,0,0)), 'world')
    elif (food == "lettuce"):
        path3=open('/home/ur3/Downloads/tacostuff/lettuce.urdf', 'r').read()
        spawn("lettuce2", path3, 'lettuce2', Pose(Point(-0.05,-0.35, 1.06), Quaternion(0,0,0,0)), 'world')
    elif (food == "sourcream"):
        path4=open('/home/ur3/Downloads/tacostuff/sourcream.urdf', 'r').read()
        spawn("sourcream2", path4, 'sourcream2', Pose(Point(-0.05,-0.35, 1.09), Quaternion(0,0,0,0)), 'world')
    else:
        pass

def spawntortilla2():
    path1=open('/home/ur3/Downloads/tacostuff/tortilla.urdf', 'r').read()
    spawn = rospy.ServiceProxy('gazebo/spawn_urdf_model', SpawnModel)
    spawn("tortilla2", path1, 'torilla2', Pose(Point(-0.05,-0.35, 1.2), Quaternion(0,0,0,0)), 'world')

def spawntortilla():
    path1=open('/home/ur3/Downloads/tacostuff/tortilla.urdf', 'r').read()
    spawn = rospy.ServiceProxy('gazebo/spawn_urdf_model', SpawnModel)
    spawn("tortilla", path1, 'torilla', Pose(Point(-0.7,0.05, 1.2), Quaternion(0,0,0,0)), 'world')

def foodspawner(food):
    spawn = rospy.ServiceProxy('gazebo/spawn_urdf_model', SpawnModel)
    if (food=="meat"):
        path2=open('/home/ur3/Downloads/tacostuff/meatmodel.urdf', 'r').read()
        spawn("meat", path2, 'meat', Pose(Point(-0.7,0.05, 1.06), Quaternion(0,0,0,0)), 'world')
    elif (food == "lettuce"):
        path3=open('/home/ur3/Downloads/tacostuff/lettuce.urdf', 'r').read()
        spawn("lettuce", path3, 'lettuce', Pose(Point(-0.7,0.05, 1.06), Quaternion(0,0,0,0)), 'world')
    elif (food == "sourcream"):
        path4=open('/home/ur3/Downloads/tacostuff/sourcream.urdf', 'r').read()
        spawn("sourcream", path4, 'sourcream', Pose(Point(-0.7,0.05, 1.09), Quaternion(0,0,0,0)), 'world')
    else:
        pass

if __name__ == '__main__':

    try:  

        testmove()  
    # When Ctrl+C is executed, it catches the exception
    except rospy.ROSInterruptException:
        pass
