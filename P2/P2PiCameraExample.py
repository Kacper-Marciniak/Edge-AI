"""
PiCamera example
"""

import cv2 as cv

from picamera2 import Picamera2

# Initialize camera
picam = Picamera2()
picam.configure(picam.create_still_configuration(main={"size": (3280, 2464)}))
picam.start()

try:
    # Grab frame
    frame = picam.capture_array(name="main")
    # Resize and convert to BGR
    frame = cv.resize(frame, (800, 600))
    frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
    # Save
    cv.imwrite("arducam.jpg", frame)

finally:
    # Stop the camera to free up resources
    picam.stop()
