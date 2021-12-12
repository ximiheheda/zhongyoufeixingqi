from dronekit import connect, VehicleMode, Command, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil
from ZhongYouVehicle import ZhongYouVehicle
import time
import math

#连接无人机
vehicle = connect("/dev/ttyACM0,115200", wait_ready=True, vehicle_class=ZhongYouVehicle)
print("无人机连接成功")

while True:
    now_distance = vehicle.rangefinder.distance
    print("目前雷达距地高度：",now_distance,"m")
    time.sleep(0.5)




