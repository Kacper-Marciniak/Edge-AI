"""
Moduł 2
"""

from sense_hat import SenseHat
from queue import Queue
from time import sleep, time
import numpy as np

BUFFER_SIZE = 5
DELTA_TEMPERATURE = 1.0
DELTA_HUMIDITY = 1.0

def run(thread_name: str, queue: Queue):
    hat = SenseHat()

    data_buffer_humidity = [hat.get_humidity()*BUFFER_SIZE]
    data_buffer_temperature = [hat.get_temperature()*BUFFER_SIZE]

    while True:
        sleep(1)
        curr_time = time()
        humidity = hat.get_humidity()
        temperature = hat.get_temperature()

        mean_h = np.mean(data_buffer_humidity)
        mean_t = np.mean(data_buffer_temperature)
      
        data_buffer_humidity.append(humidity)
        data_buffer_temperature.append(temperature)
        data_buffer_humidity.pop(0)
        data_buffer_temperature.pop(0)
        
        if np.abs(temperature-mean_t) > DELTA_TEMPERATURE:
            queue.put({
                "time": curr_time,
                "temperature": temperature,
                "event": "ABNORMAL_TEMPERATURE"
            })
        if np.abs(humidity-mean_h) > DELTA_HUMIDITY:
            queue.put({
                "time": curr_time,
                "humidity": humidity,
                "event": "ABNORMAL_HUMIDITY"
            })

        