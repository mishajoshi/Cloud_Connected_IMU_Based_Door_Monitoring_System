import time
import csv
import numpy as np
from mpu6050 import mpu6050
from collections import deque

def init_imu():
    """Initialize the MPU-6050 sensor."""
    IMU_ADDRESS = 0x68
    sensor = mpu6050(IMU_ADDRESS)
    return sensor

def read_imu(sensor):
    """Read IMU accelerometer and gyroscope data."""
    accel_data = sensor.get_accel_data()
    gyro_data = sensor.get_gyro_data()

    return [
        accel_data['x'], accel_data['y'], accel_data['z'], 
        gyro_data['x'], gyro_data['y'], gyro_data['z']
    ]

def detect_movement(window, threshold, min_consecutive=3):
    """
    Detect movement based on adaptive thresholds.
    Uses a buffer of consecutive readings to reduce noise-based false positives.

    Args:
        window (deque): Sliding window of IMU readings.
        threshold (np.array): Adaptive movement threshold.
        min_consecutive (int): Number of consecutive values required to trigger movement.

    Returns:
        bool: True if movement is detected, False otherwise.
    """
    window_arr = np.array(window)
    deviations = abs(window_arr - np.mean(window_arr, axis=0))
    above_threshold = deviations > threshold

    # Count consecutive readings above the threshold
    return np.any(np.sum(above_threshold[-min_consecutive:], axis=0) >= min_consecutive)

def collect_data(filename="imu_raw_data.csv", window_size=200):
    sensor = init_imu()
    window = deque(maxlen=window_size)
    movement_data = []
    collecting = False
    movement_start_time = None

    print("📢 Keep the sensor **STILL** for calibration (3 sec)...")

    # Collect baseline data for calibration
    for _ in range(window_size):
        window.append(read_imu(sensor))
        time.sleep(0.01)

    # Compute mean and standard deviation
    mean_vals = np.mean(window, axis=0)
    std_vals = np.std(window, axis=0)

    print(mean_vals)
    print(std_vals)

    # Set dynamic threshold (higher multiplier to reduce false positives)
    threshold = mean_vals + np.array([
        6 * std_vals[0],  # ax threshold
        6 * std_vals[1],  # ay threshold
        6 * std_vals[2],  # az threshold
        4 * std_vals[3],  # gx threshold (lower sensitivity)
        4 * std_vals[4],  
        4 * std_vals[5]   
    ])

    print("✅ Calibration Done! Now detecting movement...")

    open_counter = 0
    close_counter = 0

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        headers = ["ax", "ay", "az", "gx", "gy", "gz", "timestamp", "label"]
        writer.writerow(headers)

        while True:
            imu_data = read_imu(sensor)
            timestamp = time.time()
            window.append(imu_data)

            if len(window) == window_size:
                moving = detect_movement(window, threshold, min_consecutive=5)

                if moving and not collecting:
                    collecting = True
                    movement_start_time = timestamp
                    movement_data = []
                    print(f"📡 Movement Started @ {time.strftime('%H:%M:%S', time.localtime(movement_start_time))}")

                if collecting:
                    movement_data.append(imu_data + [timestamp])

                # Stop collecting if movement ends and enough time has passed
                if collecting and not moving and (timestamp - movement_start_time > 0.5):
                    collecting = False
                    print(f"🛑 Movement Ended @ {time.strftime('%H:%M:%S', time.localtime(timestamp))}")
                    label = input('Enter Label\n 1. Open\n 0. Close\n 2. Ignore: ')
                    
                    if label == "1":
                        open_counter += 1
                    elif label == "0":
                        close_counter += 1
                    
                    if label in ["0", "1"]:
                        for row in movement_data:
                            writer.writerow(row + [label])
                    
                    print(f"📊 Open: {open_counter}, Close: {close_counter}")

            time.sleep(0.1)

if __name__ == "__main__":
    collect_data()
