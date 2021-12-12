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

# #模拟-------这四个点的经纬度需要手持飞机打点确认
# GEO_0 = [23.1782520, 113.2157843]
# GEO_1 = [23.1782738, 113.2158698]
# GEO_2 = [23.1781796, 113.2159103]
# GEO_3 = [23.1781580, 113.2158363]

#外场--连接真机：需要打点
GEO_0 = [30.0040591, 106.2197713]
GEO_3 = [30.0041189, 106.2196332]
GEO_2 = [30.0042382, 106.2196987]
GEO_1 = [30.0041778, 106.2198378]

mission_lock = False
PROHIBITED_COLOR = 'red'
DROPING_COLOR = 'blue'
STUDENT_ID = 100002
FIELD_SERVER_IP = '192.168.50.146'

COLOR_RECOGNIZE_INDEX = 14
LAST_TASK_POS = [15, 0]
DROPING_POS = [15, 6]
TERRAIN_POS = [12, 8]

point_index = None
TASKS = np.array([
            [6, 7],  ##red  0
            [9, 5],  ##blue  1
        ])


print("无人机连接中...")
vehicle = connect("/dev/ttyACM0,115200", wait_ready=True, vehicle_class=ZhongYouVehicle)
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


def start_fly():
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
    time.sleep(1)
    print("任务开始!")


def color_recognize():
    global mission_lock
    last_result = None
    recognize_success = False
    print("颜色识别开始...")
    last_recongize_time = time.time()
    while True:
        ret, frame = camera.read()
        result = recognize(frame)
        if result and (not mission_lock):
            if result == last_result and time.time() - last_recongize_time < 5:
                continue
            last_recongize_time = time.time()
            print(result)
            b, g, r = result[0]
            led.show(r, g, b, lock=True)  ##根据识别的颜色，反馈led灯
            global color_name
            color_name = result[3]
            next_waypoint = vehicle.commands.next
            vehicle.change_mode("BRAKE")
            time.sleep(5)
            vehicle.change_mode("AUTO")
            vehicle.commands.next = next_waypoint
            time.sleep(5)
            print("清除摄像头缓冲...")
            for i in range(30):
                ret, frame = camera.read()
            led.unlock()

    time.sleep(2)

color_recognize_thread = Thread(target=color_recognize, args=())
color_recognize_thread.start()

print("等待任务开始...")
geo_rotate_angle = get_compass_bearing(GEO_0, GEO_3)
relative_level_alt = vehicle.location._relative_alt
task_alt = relative_level_alt

for i in range(10):
    led.red_flash()

##启动无人机的避障功能
vehicle.enable_object_avoidance()
vehicle.set_object_avoid_distance(1.5)  ##避障距离 1.5米

start_fly()

next_waypoint = 0
vehicle.commands.next = 0
temp_color = None

waypoint_end = False

while not waypoint_end:
    print(next_waypoint, vehicle.commands.next)
    if next_waypoint != vehicle.commands.next:
        next_waypoint = vehicle.commands.next

        if next_waypoint < COLOR_RECOGNIZE_INDEX:
            if next_waypoint == 2:
                temp_color = color_name ##在第2个航点识别，并保存识别的颜色
            
            if temp_color != None and (17 > next_waypoint > 2):
                if color_name == temp_color:  ##如果颜色识别结果相同，则降落抓取
                    if color_name == 'red':point_index = 0
                    if color_name == 'blue':point_index = 1
                    if (point_index == 0)or(point_index == 1):
                        NEW_TASK_POS = TASKS[point_index]  
                        last_local_pos = rotate(NEW_TASK_POS, geo_rotate_angle)
                        dNorth = last_local_pos[1]
                        dEast = last_local_pos[0]
                        lat, lon = get_location_metres(GEO_0, dNorth, dEast)
                        target_range = 0.1
                        vehicle.change_mode("GUIDE")
                        heading = vehicle.calculate_initial_compass_bearing((lat, lon))
                        vehicle.reach_waypoint(lat, lon, task_alt, target_range, heading=heading, led=led)
                        time.sleep(2)

                        ##开始抓取--打开机械爪
                        vehicle.open_craw()
                        time.sleep(3)

                        ##开始降落
                        vehicle.change_mode("LAND")
                        while vehicle.armed:
                            led.red_flash()
                            print("降落完成!")

                        ##开始抓取--合上机械爪
                        vehicle.close_craw()
                        time.sleep(3)

                        mission_lock = True
                        start_fly()


        if next_waypoint == 17:  ##下一个点为投放点
            last_local_pos = rotate(DROPING_POS, geo_rotate_angle)
            dNorth = last_local_pos[1]
            dEast = last_local_pos[0]
            lat, lon = get_location_metres(GEO_0, dNorth, dEast)
            target_range = 0.1
            vehicle.change_mode("GUIDE")
            heading = vehicle.calculate_initial_compass_bearing((lat, lon))
            vehicle.reach_waypoint(lat, lon, task_alt, target_range, heading=heading, led=led)
            time.sleep(2)

            ##开始投放  
            vehicle.open_craw()
            time.sleep(4)
            vehicle.close_craw()
            time.sleep(2)

            while vehicle.mode.name != "AUTO":
                vehicle.change_mode("AUTO")
                time.sleep(1)
        
        if next_waypoint == 14:  ##仿地飞行
            task_alt = 1.5 ##仿地飞行高度
            last_local_pos = rotate(TERRAIN_POS, geo_rotate_angle)
            dNorth = last_local_pos[1]
            dEast = last_local_pos[0]
            lat, lon = get_location_metres(GEO_0, dNorth, dEast)
            target_range = 0.5
            vehicle.change_mode("GUIDE")
            heading = vehicle.calculate_initial_compass_bearing((lat, lon))
            vehicle.fly_to_terrain(lat, lon, task_alt, heading=heading)
            time.sleep(2)

        if next_waypoint == 18:  ##最后一个航点  ---降落
            last_local_pos = rotate(LAST_TASK_POS, geo_rotate_angle)
            dNorth = last_local_pos[1]
            dEast = last_local_pos[0]
            lat, lon = get_location_metres(GEO_0, dNorth, dEast)
            target_range = 0.1
            vehicle.change_mode("GUIDE")
            heading = vehicle.calculate_initial_compass_bearing((lat, lon))
            vehicle.reach_waypoint(lat, lon, task_alt, target_range, heading=heading, led=led)
            time.sleep(2)
            vehicle.change_mode("LAND")
            while vehicle.armed:
                led.red_flash()
            print("降落完成!")
            time.sleep(1)
            waypoint_end = True


    for i in range(10):
        led.red_flash()
