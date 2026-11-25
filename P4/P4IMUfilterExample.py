import time
import math
from sense_hat import SenseHat

class IMUFilter:
    def __init__(self, sense: SenseHat, alpha: float = 0.96):
        """
        Inicjalizacja filtra komplementarnego
        (alpha bliżej 1 = większe zaufanie do żyroskopu,
        alpha bliżej 0 = większe zaufanie do akcelelometru).
        """
        self.alpha = alpha
        self.pitch = 0.0  # obrót wokół osi Y [rad]
        self.roll = 0.0   # obrót wokół osi X [rad]
        self.yaw = 0.0    # obrót wokół osi Z [rad]
        self.last_time = time.monotonic()
        self.sense = sense
        self.initialized = False

    def update(self):
        """
        Odczytuje czujniki Sense HAT i oblicza odfiltrowane kąty Pitch, Roll i Yaw.
        Wywołuj w pętli, możliwie często i regularnie.
        Zwraca słownik z kątami w stopniach (0-360 dla Yaw, +/-180 dla P/R).
        """
        now = time.monotonic()
        dt = now - self.last_time
        self.last_time = now

        if dt <= 0:
            dt = 0.001

        accel = self.sense.get_accelerometer_raw()  # [g]
        gyro = self.sense.get_gyroscope_raw()       # [rad/s]
        mag = self.sense.get_compass_raw()          # [µT]

        ax, ay, az = accel['x'], accel['y'], accel['z']
        gx, gy, gz = gyro['x'], gyro['y'], gyro['z']
        mx, my, mz = mag['x'], mag['y'], mag['z']

        # Kąty z akcelerometru (roll wokół X, pitch wokół Y)
        acc_roll = math.atan2(ay, az)
        acc_pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2))

        if not self.initialized:
            # Pierwszy odczyt: startujemy od zmierzonych kątów, a nie od zera
            self.roll = acc_roll
            self.pitch = acc_pitch
        else:
            self.roll = self.alpha * (self.roll + gx * dt) + (1 - self.alpha) * acc_roll
            self.pitch = self.alpha * (self.pitch + gy * dt) + (1 - self.alpha) * acc_pitch

        # Kompensacja pochylenia magnetometru
        mx_comp = mx * math.cos(self.pitch) + mz * math.sin(self.pitch)
        my_comp = (mx * math.sin(self.roll) * math.sin(self.pitch)
                   + my * math.cos(self.roll)
                   - mz * math.sin(self.roll) * math.cos(self.pitch))

        mag_yaw = math.atan2(-my_comp, mx_comp)

        if not self.initialized:
            self.yaw = mag_yaw
            self.initialized = True
        else:
            yaw_gyro_prediction = self.yaw + gz * dt
            yaw_diff = mag_yaw - yaw_gyro_prediction
            yaw_diff = math.atan2(math.sin(yaw_diff), math.cos(yaw_diff))  # najkrótsza droga
            self.yaw = yaw_gyro_prediction + (1 - self.alpha) * yaw_diff
            self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))  # trzymaj w +/-pi

        return {
            "pitch": math.degrees(self.pitch),
            "roll": math.degrees(self.roll),
            "yaw": math.degrees(self.yaw) % 360
        }

# Przykładowe wykorzystanie
if __name__ == '__main__':
    TIME_WAIT = 0.01 # Częstotliwość próbkowania ok. 100Hz

    # Utworzenie instancji SenseHAT
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

            time.sleep(TIME_WAIT)

    except KeyboardInterrupt:
        print("\nZatrzymano.")