import time
from ultralytics import YOLO
import cv2 as cv, numpy as np

def inference(model: YOLO, image: np.ndarray): model(source=image, verbose=False, device="cpu", imgsz=640)

def measure_inference_time(model: YOLO, image_path: str, n_iterations: int=100):

    # Load image
    image = cv.imread(image_path)

    # Coldstart - pierwsze wnioskowanie, zazwyczaj wolniejsze ze względu na inicjalizację modelu i wczytanie wag
    start = time.time()
    inference(model,image)
    coldstart_time = time.time() - start
    
    # Pomiar dla N iteracji
    times = []
    for _ in range(n_iterations):
        start = time.time()
        inference(model,image)
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    
    return {
        "average_inference_time": avg_time * 1000,
        "min_time": min(times) * 1000,
        "max_time": max(times) * 1000,
    }

model = YOLO("yolo26n.pt", task="detect")

timing_results = measure_inference_time(model, "bus.jpg", n_iterations=10)
print(f"Average inference time: {timing_results['average_inference_time']:.1f}ms")
print(f"Min time: {timing_results['min_time']:.1f}ms")
print(f"Max time: {timing_results['max_time']:.1f}ms")

model = YOLO("yolo26n_int8.onnx", task="detect")

timing_results = measure_inference_time(model, "bus.jpg", n_iterations=10)
print(f"Average inference time: {timing_results['average_inference_time']:.1f}ms")
print(f"Min time: {timing_results['min_time']:.1f}ms")
print(f"Max time: {timing_results['max_time']:.1f}ms")