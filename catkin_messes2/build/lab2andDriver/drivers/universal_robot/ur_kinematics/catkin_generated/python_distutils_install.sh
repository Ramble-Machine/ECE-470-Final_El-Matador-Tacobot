#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
    DESTDIR_ARG="--root=$DESTDIR"
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/ur3/catkin_messes2/src/lab2andDriver/drivers/universal_robot/ur_kinematics"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/ur3/catkin_messes2/install/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/ur3/catkin_messes2/install/lib/python2.7/dist-packages:/home/ur3/catkin_messes2/build/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/ur3/catkin_messes2/build" \
    "/usr/bin/python2" \
    "/home/ur3/catkin_messes2/src/lab2andDriver/drivers/universal_robot/ur_kinematics/setup.py" \
    build --build-base "/home/ur3/catkin_messes2/build/lab2andDriver/drivers/universal_robot/ur_kinematics" \
    install \
    $DESTDIR_ARG \
    --install-layout=deb --prefix="/home/ur3/catkin_messes2/install" --install-scripts="/home/ur3/catkin_messes2/install/bin"
