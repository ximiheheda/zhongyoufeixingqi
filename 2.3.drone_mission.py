from dronekit import connect, VehicleMode, Command, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil
import time
import math
from threading import Thread
import numpy as np
import cv2
import os
import io
import led as led
from ZhongYouVehicle import ZhongYouVehicle
from geo import *
from image_process import *

print("无人机仿真系统连接中...")
vehicle = connect("0.0.0.0:14550", wait_ready=True, vehicle_class=ZhongYouVehicle)
print("连接成功!")

print("无人机真机连接中...")
real_vehicle = connect("/dev/ttyACM0,115200", wait_ready=True, vehicle_class=ZhongYouVehicle)
print("连接成功!")


##目标识别--数据获取
def target_recog():
    global frame
    while True:
        ret, frame = camera.read()
        time.sleep(1)
        for i in range(30):
            ret, frame = camera.read()

target_recog_thread = Thread(target=target_recog, args=())
target_recog_thread.start()

def color_recognize():
    print("颜色识别开始...")
    while True:
        last_recongize_time = time.time()
        result = recognize(frame)
        if result:
            if time.time() - last_recongize_time >= 5:
                last_recongize_time = time.time()
                print(result)
                b, g, r = result[0]
                led.show(r, g, b, lock=True) ##显示灯色
                color_name = result[3]
                if color_name  == 'blue':
                    real_vehicle.open_craw()  ##机械爪张开
        led.unlock()

color_recognize_thread = Thread(target=color_recognize, args=())
color_recognize_thread.start()


time.sleep(5)
vehicle.change_mode("GUIDED")
time.sleep(1)
vehicle.armed= True
print("解锁成功")
time.sleep(0.5)
vehicle.simple_takeoff(1.5)
print("起飞！")
time.sleep(5)
while vehicle.mode.name != "AUTO":
    vehicle.change_mode("AUTO")
    time.sleep(1)
print("自主飞行")
while True:
    time.sleep(1)
