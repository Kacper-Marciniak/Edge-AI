import time
import math
from sense_hat import SenseHat

class IMUFilter:
    def __init__(self, sense: SenseHat, alpha: float = 0.96):
        """Inicjalizacja filtra komplementarnego."""
        self.alpha = alpha
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.last_time = time.time()
        self.sense = sense

    def update(self):
        """
        Oblicza odfiltrowane kąty Pitch, Roll i Yaw.
        Przyjmuje słowniki z surowymi danymi z Sense HAT.
        Zwraca słownik z kątami w stopniach (0-360 dla Yaw, +/-180 dla P/R).
        """
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        if dt <= 0:
            dt = 0.001

        accel = self.sense.get_accelerometer_raw()
        gyro = self.sense.get_gyroscope_raw()
        mag = self.sense.get_compass_raw()
        
        ax, ay, az = accel['x'], accel['y'], accel['z']
        gx, gy, gz = gyro['x'], gyro['y'], gyro['z']
        mx, my, mz = mag['x'], mag['y'], mag['z']

        acc_pitch = math.atan2(ay, math.sqrt(ax**2 + az**2))
        acc_roll = math.atan2(-ax, az)

        self.pitch = self.alpha * (self.pitch + gx * dt) + (1 - self.alpha) * acc_pitch
        self.roll = self.alpha * (self.roll + gy * dt) + (1 - self.alpha) * acc_roll

        mx_comp = mx * math.cos(self.pitch) + mz * math.sin(self.pitch)
        my_comp = mx * math.sin(self.roll) * math.sin(self.pitch) + my * math.cos(self.roll) - mz * math.sin(self.roll) * math.cos(self.pitch)

        mag_yaw = math.atan2(-my_comp, mx_comp)

        yaw_gyro_prediction = self.yaw + gz * dt
        yaw_diff = mag_yaw - yaw_gyro_prediction
        yaw_diff = math.atan2(math.sin(yaw_diff), math.cos(yaw_diff))
        
        self.yaw = yaw_gyro_prediction + (1 - self.alpha) * yaw_diff

        return {
            "pitch": math.degrees(self.pitch),
            "roll": math.degrees(self.roll),
            "yaw": (math.degrees(self.yaw) + 360) % 360
        }



sense = SenseHat()
    
# Utworzenie instancji filtra i przesłanie instancji SenseHat
imu_filter = IMUFilter(sense)

print("Uruchamianie odczytu. Naciśnij Ctrl+C, aby zatrzymać.")
    
try:
    while True:
        # Pobranie danych z czujników i filtracja
        orientation = imu_filter.update()

        # Wyświetlenie stabilnych wyników
        print(f"Pitch: {orientation['pitch']:5.1f}° | "
                  f"Roll: {orientation['roll']:5.1f}° | "
                  f"Yaw (Heading): {orientation['yaw']:5.1f}°")

        # Częstotliwość próbkowania ok. 100Hz
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nZatrzymano.")