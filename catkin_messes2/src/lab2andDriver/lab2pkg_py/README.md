### Simulator

#### Terminal 1
$ catkin_make  (Only once)  
$ source devel/setup.bash  
$ roslaunch ur3_driver ur3_gazebo.launch  

#### Terminal 2
$ source devel/setup.bash
$ rosrun lab2pkg_py lab2_spawn.py  
$ rosrun lab2pkg_py lab2_exec.py  

### Real Robot

#### Terminal 1
$ catkin_make  (Only once)  
$ source devel/setup.bash  
$ roslaunch ur3_driver ur3_driver.launch  

#### Terminal 2
$ source devel/setup.bash
$ rosrun lab2pkg_py lab2_exec.py --simulator False

