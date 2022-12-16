import rospkg

PI = 3.1415926535

# messages for student to use
from ur3_driver.msg import command
from ur3_driver.msg import position
from ur3_driver.msg import gripper_input

from std_msgs.msg import String
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge, CvBridgeError
"""

command msg
------------------------
float64[] destination
float64 v
float64 a
bool io_0


position msg
------------------------
float64[] position
bool isReady


gripper_input msg
------------------------
int32 DIGIN 
float64 AIN0
float64 AIN1

"""
