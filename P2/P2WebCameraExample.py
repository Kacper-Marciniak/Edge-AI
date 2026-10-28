"""
WebCamera example
"""

import cv2 as cv

# Initialize camera
webcam = cv.VideoCapture(0)

try:
    # Grab frame
    ret, frame = webcam.read()
    # Resize and convert to BGR
    frame = cv.resize(frame, (800, 600))
    # Save
    cv.imwrite("webcam.jpg", frame)

finally:
    # Stop the camera to free up resources
    webcam.release()
