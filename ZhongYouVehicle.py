from dronekit import Vehicle, VehicleMode, Command, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil
from geo import *
import math
import time
class ZhongYouVehicle(Vehicle):
    def __init__(self, *args):
        super(ZhongYouVehicle, self).__init__(*args)
        self.distances = None

        @self.on_message('OBSTACLE_DISTANCE')
        def listener(self, name, m):
            self.distances = m.distances

        self._proximity = [float("infinity") for i in range(9)]
        # http://python.dronekit.io/guide/mavlink_messages.html
        @self.on_message('DISTANCE_SENSOR')
        def prx_listener(self, name, message):
            distance    = min(message.max_distance, message.current_distance)
            orientation = message.orientation
            if orientation < 8:     # ROTATION_YAW_*
                self._proximity[orientation] = distance
                self.max_dis = message.max_distance
                self.min_dis = message.min_distance
            elif orientation == 25:  # ROTATION_PITCH_270
                self._proximity[8] = distance
            self.notify_attribute_listeners('prox', self._proximity)

            self.proximity_distance =  distance
            self.proximity_orientation = orientation

    @property
    def proximity(self):
        return self._proximity

    def calculate_initial_compass_bearing(self, pointB):
        current_position = self.location.global_frame
        pointA = (current_position.lat, current_position.lon)
        return get_compass_bearing(pointA, pointB)

    def current_distance_to_geo_point(self, lat, lon):
        current_position = self.location.global_frame
        return get_geo_distance(current_position.lat, current_position.lon, lat, lon)

    def fly_to(self, lat, lon, alt, speed=0.5, heading=None):
        if not heading:
            bearing = self.calculate_initial_compass_bearing((lat, lon))
            heading = bearing

        target_distance = self.current_distance_to_geo_point(lat, lon)
        if target_distance > 20:
            print(f"航点距离 {target_distance} 太远!")
            return

        msg = self.message_factory.set_position_target_global_int_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # frame
            0b100111111000,
            int(lat*1e7), int(lon*1e7), alt, # x, y, z positions (not used)
            0.5, 0.5, 0.5, # x, y, z velocity in m/s
            0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            math.radians(heading), 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

        self.send_mavlink(msg)

    def set_servo(self, pwm_value):
        msg = self.message_factory.command_long_encode(
                0, 0,  # target_system, target_component
                mavutil.mavlink.MAV_CMD_DO_SET_SERVO,  # command
                0,  # confirmation
                7,  # servo number
                pwm_value,  # servo position between 1000 and 2000
                0, 0, 0, 0, 0)  # param 3 ~ 7 not used

        self.send_mavlink(msg)

    def open_craw(self):
        self.set_servo(1900)

    def close_craw(self):
        self.set_servo(1050)

    def fly_to_terrain(self, lat, lon, alt, heading=0):
        target_distance = self.current_distance_to_geo_point(lat, lon)
        if target_distance > 150:
            print(f"航点距离 {target_distance} 太远!")
            return
        self._master.mav.mission_item_send(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_TERRAIN_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 2, 0, 0, 0, 0, heading, lat, lon, alt)

    def change_heading(self, heading):
        direction = 0
        self._master.mav.mission_item_send(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_TERRAIN_ALT, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 2, 0, heading, 0, direction, 0, 0, 0,0)

    def change_mode(self, mode_name):
        ret = False
        while not ret:
            try:
                self.mode = VehicleMode(mode_name)
                ret = True
            except Exception as e:
                time.sleep(0.01)

    def enable_object_avoidance(self):
        self.parameters.set("OA_TYPE", 1)
        self.parameters.set("PRX_TYPE", 2)


    def disable_object_avoidance(self):
        self.parameters.set("OA_TYPE", 0)
        self.parameters.set("PRX_TYPE", 0)

    def set_object_avoid_distance(self, distance):
        self.parameters.set("OA_MARGIN_MAX", 0.8)

    def reach_waypoint(self, lat, lon, alt, target_range, terrain=False, heading=None, led=None):
        if heading is None:
            heading = self.calculate_initial_compass_bearing((lat, lon))
        self.change_heading(heading)
        time.sleep(2)
        if terrain:
            self.fly_to_terrain(lat, lon, alt, heading=heading)
        else:
            self.fly_to(lat, lon, alt, heading=heading)
        i = 1
        while self.current_distance_to_geo_point(lat, lon) > target_range: 
            if terrain:
                self.fly_to_terrain(lat, lon, alt, heading=heading)
            else:
                self.fly_to(lat, lon, alt, heading=heading)
            i += 1
            if i > 50: 
                print(f"距离目的地剩余 {self.current_distance_to_geo_point(lat, lon)}米...")
                i = 1
            time.sleep(0.02)

            if led:
                led.red_flash()

    def motor_spin(self, motor_id, throttle, duration):
        msg = self.message_factory.command_long_encode(
                0, 1,  # target_system, target_component
                mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,  # command
                1,
                motor_id,
                mavutil.mavlink.MOTOR_TEST_THROTTLE_PERCENT,
                throttle,
                duration,
                6,
                mavutil.mavlink.MOTOR_TEST_ORDER_BOARD,
                0)

        self.send_mavlink(msg)
