#!/usr/bin/env python3
from cmath import acos, atan, asin
from pyexpat.model import XML_CTYPE_NAME
import numpy as np
from scipy.linalg import expm
from scipy.optimize import fsolve
import math
from lab5_header import *
def arccos(x):
	if (x<-1):
		x=x+np.abs(math.floor(x))
	elif (x>=1):
		x=x-np.abs(math.floor(x))
	return np.arccos(x)
	
"""
Use 'expm' for matrix exponential.
Angles are in radian, distance are in meters.
"""
def Get_MS():
	# =================== Your code starts here ====================#
	# Fill in the correct values for a1~6 and q1~6, as well as the M matrix
	M = np.eye(4)
	S = np.zeros((6,6))
	# =================== Your code starts here ====================#
	# Fill in the correct values for S1~6, as well as the M matrix
	
	w0 = np.array([0,0,1])
	w1 = np.array([0,1,0])
	w2 = np.array([0,1,0])
	w3 = np.array([0,1,0])
	w4 = np.array([1,0,0])
	w5 = np.array([0,1,0])

	q0 = np.array([-150,150,10])
	q1 = np.array([-150,270,162])
	q2 = np.array([94,270,162])
	q3 = np.array([307,177,162])
	q4 = np.array([307,260,162])
	q5 = np.array([390,260,162])
 
	v0 = -1 * np.cross(w0,q0)
	v1 = -1 * np.cross(w1,q1)
	v2 = -1 * np.cross(w2,q2)
	v3 = -1 * np.cross(w3,q3)
	v4 = -1 * np.cross(w4,q4)
	v5 = -1 * np.cross(w5,q5)
	v = np.array([v0,v1,v2,v3,v4,v5])
	S = np.array([[w0,v0],[w1,v1],[w2,v2],[w3,v3],[w4,v4],[w5,v5]])

	# w_b = np.array([[0,-w3,w2],[w3,0,-w1],[-w2,w1,0]])
	# S_b = np.array([[w_b,v],[0,0]])
	#s_b = np.zeros(())
	#s_b0 = np.array([[],[],[],[]])
	# t0=(np.array([[[1,0,0],[0,1,0],[0,0,1],[390,401,215.5]],[0, 1]))
	# logthing= logm(t0)
	# 
	M = np.array([[0,-1,0, 390],[0,0,-1,401],[1,0,0,215.5],[0,0,0,1]])
	# ==============================================================#
	return M, S

def calculate(x):
    w = np.array(x[0])
    v = np.array(x[1])
    s_b = np.zeros((4,4))
    s_b[0][0] = 0
    s_b[0][1] = -w[2]
    s_b[0][2] = w[1]
    s_b[0][3] = v[0]
    s_b[1][0] = w[2]
    s_b[1][1] = 0
    s_b[1][2] = -w[0]
    s_b[1][3] = v[1]
    s_b[2][0] = -w[1]
    s_b[2][1] = w[0]
    s_b[2][2] = 0
    s_b[2][3] = v[2]
    s_b[3][0] = 0
    s_b[3][1] = 0
    s_b[3][2] = 0
    s_b[3][3] = 0

    return s_b

"""
Function that calculates encoder numbers for each motor
"""
def lab_fk(theta1, theta2, theta3, theta4, theta5, theta6):

	# Initialize the return_value
	return_value = [None, None, None, None, None, None]
	M,S = Get_MS()
	
	# =========== Implement joint angle to encoder expressions here ===========

	# =================== Your code starts here ====================#
	phase = np.array([theta1*calculate(S[0]), theta2*calculate(S[1]) ,theta3*calculate(S[2]) ,theta4*calculate(S[3]) , theta5*calculate(S[4]) ,theta6*calculate(S[5])])
	temp=np.identity(4)
	for i in range(0,6):
		temp=temp * expm(phase[i])
	T = np.dot(temp,M)
	# ==============================================================#


	return_value[0] = theta1 + PI
	return_value[1] = theta2
	return_value[2] = theta3
	return_value[3] = theta4 - (0.5*PI)
	return_value[4] = theta5
	return_value[5] = theta6

	return return_value


"""
Function that calculates an elbow up Inverse Kinematic solution for the UR3
"""

def lab_invk(xWgrip, yWgrip, zWgrip, yaw_WgripDegree):
	# =================== Your code starts here ====================#
	L1 = 152
	L2 = 120
	L3 = 244
	L4 = 93
	L5 = 213
	L6 = 83
	L7 = 83
	L8 = 82
	L9 = 53.5
	L10 = 59
	print(xWgrip, yWgrip, zWgrip)
	xWgrip = xWgrip + 150
	yWgrip = yWgrip - 150
	zWgrip = zWgrip - 10

	yaw = np.radians(yaw_WgripDegree)

	xcen = xWgrip - L9*np.cos(yaw)
	ycen = yWgrip - L9*np.sin(yaw)
	zcen = zWgrip

	theta1 = np.arctan(ycen/xcen) - np.arcsin((L2-L4+L6)/(np.sqrt(xcen**2+ycen**2)))
	theta6 = (np.pi/2 - yaw) + theta1

	xend = xcen - L7*np.cos(theta1) + (L6+27)*np.sin(theta1)
	yend = ycen - (L6+27)*np.cos(theta1) - L7*np.sin(theta1)
	zend = zcen + L8 + L10
	

	hypot = np.sqrt((xend**2) + (yend**2))

	phi1 = np.arccos((2*(hypot**2))/(2*(hypot)*((hypot**2)+((zend-L1)**2))**0.5))
	phi2 = np.arccos(((L3**2)+(hypot**2)+((zend-L1)**2)-L5**2)/(2*(L3)*((hypot**2)+(zend-L1)**2)**0.5))

	theta2 = phi1 + phi2
	theta3 = np.pi - (np.arccos((L3**2+L5**2 - (hypot**2 + (zend-L1)**2))/(2*L3*L5)))
	theta4 = theta3 - theta2

	theta2 = theta2*-1
	theta4 = theta4*-1

	theta5 = -np.pi/2


	# ==============================================================#
	return lab_fk(theta1, theta2, theta3, theta4, theta5, theta6)

