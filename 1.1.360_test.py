from dronekit import connect, VehicleMode, Command, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil
from ZhongYouVehicle import ZhongYouVehicle
import time
import math

#连接无人机
real_vehicle = connect("/dev/ttyACM0,115200", wait_ready=True, vehicle_class=ZhongYouVehicle)
print("无人机连接成功")
time.sleep(5)

temp_lock = 0
temp_orien = 0

while True:
    # time.sleep(0.05)
    if real_vehicle._proximity:
        if(temp_lock == 0):
            print(f"探测最大距离: {real_vehicle.max_dis / 100} m")
            print(f"探测最小距离: {real_vehicle.min_dis / 100} m")
            temp_lock = 1
        orientation = real_vehicle.proximity_orientation
        distance = real_vehicle.proximity_distance / 100
        if(temp_orien != orientation):
            print(f"{orientation}方向障碍物距离: {distance} m")
            temp_orien = orientation


        # print(f"{orientation}方向障碍物距离: {distance} m")




