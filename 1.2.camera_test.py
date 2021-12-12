import cv2
import datetime
import time

image_format = "jpg"        #样张格式设置
camera = cv2.VideoCapture(0)

for i in range(8):
    IMG_name = i+1
    ret, frame = camera.read()
    frame_width = 640 #初始摄像头分辨率，要更改的话改数字即可
    frame_height = 480   #初始摄像头分辨率，要更改的话改数字即可
    resize_frame = cv2.resize(frame, (frame_width, frame_height))    #分辨率
    now = datetime.datetime.now()#显示当前时间
#八个参数分别对应puttext内部参数
    img = resize_frame     #图片
    dt = str(now)  #改成字符串
    text_position = (100,20)        #文字位置
    font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX #定义字体
    font_scale = 1     #字体大小
    font_color = (0,0,255)      #文字色彩##b,g,r   要求--红色
    thickness = 4
    lineType = cv2.LINE_8
    resize_frame = cv2.putText(img, dt, text_position, font, font_scale, font_color, thickness, lineType)
    cv2.imwrite(f"{IMG_name}.{image_format}", resize_frame)
    time.sleep(0.5)  ##拍摄频率为每秒2张  帧率2Hz


camera.release()

