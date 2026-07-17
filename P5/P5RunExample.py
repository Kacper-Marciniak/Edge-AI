"""
'Nadzorca' - nasłuchuje wątki 1 oraz 2 i tworzy LOG
"""

from Code1 import run as run1
from Code2 import run as run2

from threading import Thread
from queue import Queue
from sense_hat import SenseHat
import time, datetime
import json, os

FILE_PATH = "log.json"
with open (FILE_PATH, mode="w") as file:
    curr_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    file.write( "[{}]".format(json.dumps({"time": curr_time, "event": "EVENT_DEVICE_START"})))

sense_hat = SenseHat()

queue = Queue()
thread1 = Thread(target=run1, args=("T1", queue,))
thread2 = Thread(target=run2, args=("T2", queue,))

thread1.start()
thread2.start()
while not len(sense_hat.stick.get_events()):
    if not queue.empty():
        event_dict = queue.get()
        
        with open (FILE_PATH, mode="r+") as file:
            file.seek(os.stat(FILE_PATH).st_size -1)
            file.write( ",\n{}]".format(json.dumps(event_dict)))

thread1.join()
thread2.join()
