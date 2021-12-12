from dronekit import connect, VehicleMode, Command, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil
import time
import math

import numpy as np
import cv2
import os
import io

from threading import Thread

from ZhongYouVehicle import ZhongYouVehicle
from server_function import *
from geo import *
from image_process import *
import led as led

#模拟--连接仿真无人机
GEO_0 = [23.17824430, 113.21576250]
GEO_1 = [23.1782443, 113.21597259568992]
GEO_2 = [23.178370064139777, 113.21597259568992]
GEO_3 = [23.178370064139777, 113.2157625]

# #外场--连接真机，并注释“模拟”航点，取消以下注释：
# GEO_0 = [30.0040591, 106.2197713]
# GEO_3 = [30.0041189, 106.2196332]
# GEO_2 = [30.0042382, 106.2196987]
# GEO_1 = [30.0041778, 106.2198378]

NORMAL_WAYPOINT = 0
COLOR_RECOGNIZE_TASK = 1
CHARGING_TASK = 2
TERRAIN_TASK = 3
DROPING_TASK = 4
AVOID_TASK = 5

TASKS = [
            [NORMAL_WAYPOINT, [0, 1]],
            [COLOR_RECOGNIZE_TASK, [0, 4]],
            [NORMAL_WAYPOINT, [0, 11]],
            [NORMAL_WAYPOINT, [3, 11]],
            [AVOID_TASK, [3, 6]],
            [NORMAL_WAYPOINT, [3, 1]],
            [NORMAL_WAYPOINT, [6, 1]],
            [COLOR_RECOGNIZE_TASK, [6, 7]],
            [NORMAL_WAYPOINT, [6, 11]],
            [NORMAL_WAYPOINT, [9, 11]],
            [COLOR_RECOGNIZE_TASK, [9, 5]],
            [NORMAL_WAYPOINT, [9, 1]],
            [NORMAL_WAYPOINT, [12, 1]],
            [TERRAIN_TASK, [12, 8]],
            [NORMAL_WAYPOINT, [12, 11]],
            [NORMAL_WAYPOINT, [15, 11]],
            [DROPING_TASK, [15, 6]],
            [NORMAL_WAYPOINT, [15, 0]],

        ]

geo_rotate_angle = get_compass_bearing(GEO_0, GEO_3)
drone_task_name = 'waypoints.txt'
output='QGC WPL 110\n'
#Add home location as 0th waypoint
START_TASK_INDEX = 0

##连接仿真无人机--- 注意配置端口
vehicle = connect("0.0.0.0:14553", wait_ready=True, vehicle_class=ZhongYouVehicle) 

# ##如果在外场，则为连接真机---
# vehicle = connect("/dev/ttyACM0,115200", wait_ready=True, vehicle_class=ZhongYouVehicle)

for index, task in enumerate(TASKS[START_TASK_INDEX:]):
    seq = index + 1
    print("==========================")
    print(task)
    task_type = task[0]
    task_pos = task[1]
    local_pos = rotate(task_pos, geo_rotate_angle)
    dNorth = local_pos[1]
    dEast = local_pos[0]
    lat, lon = get_location_metres(GEO_0, dNorth, dEast)
    alt = 2  ##起飞高度设定为2米
    current = 0
    commandline="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (seq,current,10,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,0,0,0,0,lat,lon,alt,0)
    output+=commandline

with open(drone_task_name, 'w') as file_:
    print(" Write mission to file")
    file_.write(output)
    file_.close()



def readmission(aFileName):
    print("\nReading mission from file: %s" % aFileName)
    cmds = vehicle.commands
    missionlist=[]
    with open(aFileName) as f:
        for i, line in enumerate(f):
            if i==0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                linearray=line.split('\t')
                ln_index=int(linearray[0])
                ln_currentwp=int(linearray[1])
                ln_frame=int(linearray[2])
                ln_command=int(linearray[3])
                ln_param1=float(linearray[4])
                ln_param2=float(linearray[5])
                ln_param3=float(linearray[6])
                ln_param4=float(linearray[7])
                ln_param5=float(linearray[8])
                ln_param6=float(linearray[9])
                ln_param7=float(linearray[10])
                ln_autocontinue=int(linearray[11].strip())
                cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist


def upload_mission(aFileName,Object):
    #Read mission from file
    missionlist = readmission(aFileName)
    
    print("\nUpload mission from a file: %s" % aFileName)
    #Clear existing mission from vehicle
    print(' Clear mission')
    cmds = Object.commands
    cmds.clear()
    #Add new mission to vehicle
    for command in missionlist:
        cmds.add(command)
    print(' Upload mission')
    Object.commands.upload()        

#Upload mission from file
upload_mission(drone_task_name,vehicle)

time.sleep(5)


print("\nall data uploaded done!")  ##上传航线完毕