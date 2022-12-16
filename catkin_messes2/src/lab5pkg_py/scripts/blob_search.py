#!/usr/bin/env python

import cv2
import numpy as np
import time
from  math import *
# ========================= Student's code starts here =========================

# Params for camera calibration
theta = 0
beta = 334.4
Or = 240
Oc = 320
x_w = 0.719
y_w = -0.956
col, row = 480, 640 

#264.8562316894531, second: 197.4044189453125

x_c = (row-Or)/beta
y_c = (col-Oc)/beta

Rot = np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta),np.cos(theta)]])

X_w = np.array([[x_w],[y_w]])
X_c = np.array([[x_c], [y_c]])



T =X_w -Rot * X_c
x_c = (row-Or)/beta
y_c = (col-Oc)/beta

Rot = np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta),np.cos(theta)]])

X_w0 = np.array([[x_w],[y_w]])
X_c0 = np.array([[x_c], [y_c]])

def retsign(col, row):
    pass
# Function that converts image coord to world coord
def IMG2W(col, row, color):
    global T
    global Rot
    Coord = np.array([[(row-Or)/beta], [(col-Oc)/beta]])
    return list([float(Coord[0]*1000), float(Coord[1]*1000)])


# ========================= Student's code ends here ===========================

def blob_search(image_raw, color):

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

    # ========================= Student's code starts here =========================

    # Filter by Color
    params.filterByColor = False

    # Filter by Area.
    params.filterByArea = False

    # Filter by Circularity
    params.filterByCircularity = False

    # Filter by Inerita
    params.filterByInertia = False

    # Filter by Convexity
    params.filterByConvexity = False

    # ========================= Student's code ends here ===========================

    # Create a detector with the parameters
    detector = cv2.SimpleBlobDetector_create(params)

    # Convert the image into the HSV color space
    hsv_image = cv2.cvtColor(image_raw, cv2.COLOR_BGR2HSV)

    # ========================= Student's code starts here =========================
    if (color=="orange"):
        upper = (35, 255, 255)     # orang uup
        lower = (10, 0, 0)   # orang luuu
    elif (color== "blue" ):
        upper = (150, 255, 255)     # bb uup
        lower = (100, 150, 70)   # bb luuu    
    elif (color== "green"):
        upper = (65, 255, 255)     # gren uup
        lower = (50, 0, 0)   # gren luuu    
    elif (color== "red"):
        upper = (179, 255, 255)     # red uup
        lower = (150, 50, 50)   # red luuu    
    elif (color== "babyblue"):
                upper = (179, 255, 255)     # red uup
                lower = (150, 0, 0)   # red luuu 
       
    # Define a mask using the lower and upper bounds of the target color
    if (color== "red"):
        lower_red = np.array([0,50,50])
        upper_red = np.array([10,255,255])
        mask0 = cv2.inRange(hsv_image, lower_red, upper_red)
# upper mask (170-180)
        lower_red = np.array([170,50,50])
        upper_red = np.array([180,255,255])
        mask1 = cv2.inRange(hsv_image, lower_red, upper_red)
# join my masks
        mask_image = mask0+mask1
    else:
        mask_image = cv2.inRange(hsv_image, lower, upper)

    # ========================= Student's code ends here ===========================

    keypoints = detector.detect(mask_image)

    # Find blob centers in the image coordinates
    blob_image_center = []
    num_blobs = len(keypoints)
    for i in range(num_blobs):
        blob_image_center.append((keypoints[i].pt[0],keypoints[i].pt[1]))
    
        
    # ========================= Student's code starts here =========================
    
    # Draw the keypoints on the detected block
    im_with_keypoints = cv2.drawKeypoints(image_raw, keypoints, lower, upper)

    # ========================= Student's code ends here ===========================

    xw_yw = []

    if(num_blobs == 0):
        print("No block found!")
    else:
        # Convert image coordinates to global world coordinate using IM2W() function
        for i in range(num_blobs):
            xw_yw.append(IMG2W(blob_image_center[i][0], blob_image_center[i][1], color))



    cv2.namedWindow("Keypoint View")
    cv2.imshow("Keypoint View", im_with_keypoints)

    cv2.waitKey(2)
    return xw_yw
