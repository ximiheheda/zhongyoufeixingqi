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


#外场-------这四个点的经纬度需要手持飞机打点确认
##模拟
GEO_0 = [23.1782520, 113.2157843]
GEO_1 = [23.1782738, 113.2158698]
GEO_2 = [23.1781796, 113.2159103]
GEO_3 = [23.1781580, 113.2158363]

LAST_TASK_POS = [14.5, 0]
TERRAIN_POS = [14.5, 1.5]
mission_lock = False
PROHIBITED_COLOR = 'red'
DROPING_COLOR = 'blue'
STUDENT_ID = 100002
FIELD_SERVER_IP = '192.168.50.15'


print("仿真系统连接中...")
vehicle = connect("0.0.0.0:14553", wait_ready=True, vehicle_class=ZhongYouVehicle)
print("连接成功!")


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
                if color_name  == PROHIBITED_COLOR:  ##声光反馈
                    audio_broadcast(FIELD_SERVER_IP, STUDENT_ID, 'red')
                    photo_name = 'prohibited_crop.jpg'
                    photo_frame = photo_add_text_position(frame, vehicle.location.global_frame.lat, vehicle.location.global_frame.lon)
                    cv2.imwrite(photo_name, photo_frame)
                elif color_name  == DROPING_COLOR:
                    audio_broadcast(FIELD_SERVER_IP, STUDENT_ID, 'blue')
        led.unlock()

color_recognize_thread = Thread(target=color_recognize, args=())
color_recognize_thread.start()



print("等待任务开始...")
# geo_rotate_angle = get_compass_bearing(GEO_0, GEO_3)
# # relative_level_alt = vehicle.location._relative_alt
# # task_alt = relative_level_alt + 1
# task_alt = 2  ###飞行高度为2米

for i in range(10):
    led.red_flash()

time.sleep(5)
vehicle.change_mode("GUIDED")
time.sleep(1)
vehicle.armed= True
print("解锁成功")
time.sleep(0.5)
vehicle.simple_takeoff(2) ##飞行高度为2米
print("起飞！")
time.sleep(5)
while vehicle.mode.name != "AUTO":
    vehicle.change_mode("AUTO")
    time.sleep(1)
print("自主飞行")
time.sleep(1)
print("任务开始!")


##启动仿真机的避障功能
vehicle.enable_object_avoidance()
vehicle.set_object_avoid_distance(1.5) ##避障距离1.5m

while True:
    
    ##调用仿地雷达
    now_distance = vehicle.rangefinder.distance
    print("目前雷达距地高度：",now_distance,"m")
    time.sleep(3)