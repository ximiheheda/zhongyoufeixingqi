import numpy as np
import cv2

print("摄像头加载中...")
try:
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    if(ret):
        print("分辨率", frame.shape)
        cv2.imwrite('test.jpg', frame)
    # camera.release()
except Exception as e:
    raise e

#[COLOR_VALUE, RANGE_MIN, RANGE_MAX]
BGR_COLOR_RANGE = [
        [(0,0,255), (0,0,190), (50, 40, 255), "red"],  
        [(255,0,0), (50,20,0), (90, 40, 30), "blue"],
        [(0,0,0), (20,20,20), (50, 40, 40), "black"],
        [(0,255,0), (100,100,0), (140, 255, 30), "green"],  
        [(0,60,255), (70,100,200), (100, 130, 255), "orange"],
        [(240,32,160), (160,85,60), (210, 120, 120), "purple"],
        [(192,192,192), (130,110,80), (160, 140, 120), "gray"],
        ]

TARGET_CENTER_X = 100
TARGET_CENTER_Y = 100
TARGET_PERCENTAGE = 0.4
COLOR_RECOGNIZE_TIMEOUT = 60

font = cv2.FONT_HERSHEY_SIMPLEX
font_size = 0.5

def crop_center(img,cropx,cropy):
    y,x,c = img.shape
    startx = x//2 - cropx//2
    starty = y//2 - cropy//2
    return img[starty:starty+cropy, startx:startx+cropx, :]

def unique_count(img):
    colors, count = np.unique(img.reshape(-1,img.shape[-1]), axis=0, return_counts=True)
    return colors[count.argmax()]

def recognize(frame):
    center = crop_center(frame, TARGET_CENTER_X, TARGET_CENTER_Y)
    #  target_color = unique_count(center)
    #  cv2.imwrite('center.jpg', center)
    for item in BGR_COLOR_RANGE:
        mask = cv2.inRange(center, np.array(item[1]), np.array(item[2]))
        match_count = np.count_nonzero(mask)
        match_percentage = float(match_count) / (TARGET_CENTER_X * TARGET_CENTER_Y)
        #  print(match_percentage)
        #  print(item[0], match_percentage)
        if match_percentage >= TARGET_PERCENTAGE:
            return item

def photo_add_text_name(photo_frame, name):
    cv2.putText(photo_frame,
                name,
                (500, 400),
                font, font_size,
                (0, 255, 255),
                2,
                cv2.LINE_4)
    return photo_frame

def photo_add_text_position(photo_frame, lat, lon):
    cv2.putText(photo_frame,
                f'latitude:{ lat }, longitude:{ lon }',
                (280, 450),
                font, font_size,
                (0, 255, 255),
                2,
                cv2.LINE_4)
    return photo_frame

print("摄像头加载成功!")
