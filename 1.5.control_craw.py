#!/usr/bin/env python3
import numpy as np
import cv2
import os
import io

from dronekit import connect, VehicleMode, Command, LocationGlobal, LocationGlobalRelative
from ZhongYouVehicle import ZhongYouVehicle
from pymavlink import mavutil
import time
import math

vehicle = connect("/dev/ttyACM0,115200", wait_ready=True, vehicle_class=ZhongYouVehicle)
print("无人机连接成功")

frame_index = 0

while frame_index < 3:
    print("开合次数:", frame_index + 1)
    vehicle.open_craw()
    time.sleep(3)  ##每次张开时间保持3秒
    vehicle.close_craw()
    time.sleep(3) 
    frame_index += 1








