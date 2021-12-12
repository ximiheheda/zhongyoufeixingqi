#!/usr/bin/env python3
import numpy as np
import cv2
import os
import io
import time

from dronekit import connect, VehicleMode, Command, LocationGlobal, LocationGlobalRelative
from ZhongYouVehicle import ZhongYouVehicle
from pymavlink import mavutil
import math
from image_process import *


while True:
    ret, frame = camera.read()
    result = recognize(frame)
    
#根据识别到的照片，选择不同操作
    if result:
        color_name = result[3]

        if color_name  == 'red':
            print("识别为违禁区域，即将进行拍照取证")  ###得分点---
            cv2.imwrite("1-4颜色识别.jpg",frame)
            time.sleep(2)

        elif color_name  == 'blue':
            print("识别为异常区域") ###得分点---
            cv2.imwrite("1-4颜色识别.jpg",frame)
            time.sleep(2)

    time.sleep(2)


