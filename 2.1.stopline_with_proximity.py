from dronekit import connect, VehicleMode, Command, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil
import time
import math

import numpy as np
import cv2
import os
import io

from ZhongYouVehicle import ZhongYouVehicle
from geo import *

print("无人机真机连接中...")
vehicle = connect("/dev/ttyACM0,115200", wait_ready=True, vehicle_class=ZhongYouVehicle)
print("连接成功!")

time.sleep(5)
vehicle.change_mode("GUIDED")
time.sleep(1)
vehicle.armed= True
print("解锁成功")
time.sleep(0.5)
vehicle.simple_takeoff(1.5)
print("开始测试")

temp_orien = 25

while True:
    if vehicle._proximity:
        orientation = vehicle.proximity_orientation
        distance = vehicle.proximity_distance / 100
        if(temp_orien != orientation) and (orientation != 25):
            print(f"{orientation}方向障碍物距离: {distance} m")
            if distance < 1:
                vehicle.change_mode("BRAKE")