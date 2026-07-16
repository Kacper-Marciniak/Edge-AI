"""
Moduł 1
"""

from sense_hat import SenseHat
from queue import Queue
from time import sleep, time

BRIGHTNESS_THRESH_MIN = 5
BRIGHTNESS_THRESH_MAX = 50

def run(thread_name: str, queue: Queue):
    
    hat = SenseHat()    
    hat.color.gain = 4
    hat.color.integration_cycles = 64

    while True:
        sleep(2 * hat.colour.integration_time)
        curr_time = time()
        red, green, blue, brightness = hat.colour.colour
        
        if brightness < BRIGHTNESS_THRESH_MIN or brightness > BRIGHTNESS_THRESH_MAX:
            queue.put({
                "time": curr_time,
                "brightness": brightness,
                "event": "ABNORMAL_AMBIENT_LIGHTNING"
            })