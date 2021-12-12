import time
from neopixel import *
led_lock = False

LED_COUNT      = 12      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

strip.begin()

def show(r, g, b, lock=False):
    global led_lock
    if not led_lock:
        for i in range(LED_COUNT):
            strip.setPixelColor(i,  Color(g, r, b))
        strip.show()
        if lock:
            led_lock = True

def unlock():
    global led_lock
    led_lock = False

def lock():
    global led_lock
    led_lock = True

def red_flash():
    show(255,0,0)
    time.sleep(0.1)
    show(0,0,0)
    time.sleep(0.1)

def green_flash():
    show(0,255,0)
    time.sleep(0.1)
    show(0,0,0)
    time.sleep(0.1)

def blue_flash():
    show(0,0,255)
    time.sleep(0.1)
    show(0,0,0)
    time.sleep(0.1)

def white_flash():
    show(255,255,255)
    time.sleep(0.1)
    show(0,0,0)
    time.sleep(0.1)

show(255,0,0)
time.sleep(1)
show(0,255,0)
time.sleep(1)
show(0,0,255)
time.sleep(1)
show(255,255,255)
print("LED 模块加载完成!")
