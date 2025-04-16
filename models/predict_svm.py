import joblib
import time
import numpy as np
import paho.mqtt.client as mqtt
import ssl
import json
from mpu6050 import mpu6050
from collections import deque
from scipy.interpolate import interp1d
from config import AWS_ENDPOINT, MQTT_PORT, KEEPALIVE, TOPIC, ROOT_CA, CERTIFICATE_PATH, PRIVATE_KEY_PATH, CLIENT_ID


# Load models
svm_model = joblib.load("svm_rbf_door_model.pkl")
scaler = joblib.load("scaler.pkl")
lda = joblib.load("lda.pkl")

def init_imu():
    """Initialize MPU6050 sensor."""
    IMU_ADDRESS = 0x68
    return mpu6050(IMU_ADDRESS)

def read_imu(sensor):
    """Read accelerometer and gyroscope data from IMU."""
    accel_data = sensor.get_accel_data()
    gyro_data = sensor.get_gyro_data()
    
    return [
        accel_data['x'], accel_data['y'], accel_data['z'], 
        gyro_data['x'], gyro_data['y'], gyro_data['z']
    ]

def compute_features(data):
    """Extract features: mean, variance, and FFT components."""
    data_arr = np.array(data)
    mean_vals = np.mean(data_arr, axis=0)
    var_vals = np.var(data_arr, axis=0)
    fft_vals = np.abs(np.fft.fft(data_arr, axis=0))[0]  # First FFT coefficient
    return np.concatenate([mean_vals, var_vals, fft_vals])

def resample_segment(segment, target_size=100):
    """Resample collected movement data to a fixed length."""
    segment = np.array(segment)
    original_size = len(segment)

    if original_size == target_size:
        return segment

    x_original = np.linspace(0, 1, original_size)
    x_target = np.linspace(0, 1, target_size)
    
    interpolated = np.array([interp1d(x_original, segment[:, col], kind='linear', fill_value="extrapolate")(x_target) 
                             for col in range(segment.shape[1])]).T
    return interpolated

def detect_movement(window, threshold, min_consecutive=5):
    """
    Detect movement based on adaptive thresholds.
    Args:
        window (deque): Sliding window of IMU readings.
        threshold (np.array): Adaptive movement threshold.
        min_consecutive (int): Minimum consecutive values above threshold for movement detection.
    Returns:
        bool: True if movement is detected, False otherwise.
    """
    window_arr = np.array(window)
    deviations = abs(window_arr - np.mean(window_arr, axis=0))
    above_threshold = deviations > threshold

    return np.any(np.sum(above_threshold[-min_consecutive:], axis=0) >= min_consecutive)

def predict_state(window_size=200, target_segment_size=100):
    """Predict door state using real-time IMU data."""
    sensor = init_imu()
    window = deque(maxlen=window_size)
    movement_data = []
    collecting = False
    movement_start_time = None
    noise_window = deque(maxlen=100)  # Track rolling noise levels

    mqtt_client = mqtt.Client(client_id=CLIENT_ID)
    mqtt_client.tls_set(ROOT_CA, certfile=CERTIFICATE_PATH, keyfile=PRIVATE_KEY_PATH, tls_version=ssl.PROTOCOL_TLSv1_2)

    mqtt_client.connect(AWS_ENDPOINT, MQTT_PORT, KEEPALIVE)
    print('Connected to AWS IOT')

    # Initial calibration phase
    print("Calibrating - keep sensor still for 3 seconds")
    for _ in range(window_size):
        imu_data = read_imu(sensor)
        window.append(imu_data)
        noise_window.append(np.abs(imu_data))
        time.sleep(0.01)

    # Compute initial noise threshold
    mean_vals = np.mean(noise_window, axis=0)
    std_vals = np.std(noise_window, axis=0)

    threshold = mean_vals + np.array([
        6 * std_vals[0],  # ax threshold
        6 * std_vals[1],  
        6 * std_vals[2],  
        4 * std_vals[3],  # gx threshold (lower sensitivity)
        4 * std_vals[4],  
        4 * std_vals[5]   
    ])

    print('✅ Calibration done! Detecting movement...')

    while True:
        imu_data = read_imu(sensor)
        timestamp = time.time()
        window.append(imu_data)

        if len(window) == window_size:
            moving = detect_movement(window, threshold, min_consecutive=5)

            # Start collecting movement data if not already collecting
            if moving and not collecting:
                collecting = True
                movement_start_time = timestamp
                print(f"📡 Movement Started @ {time.strftime('%H:%M:%S', time.localtime(movement_start_time))}")
                movement_data = []

            if collecting:
                movement_data.append(imu_data)

            # Stop collecting if movement ceases for 0.5 seconds
            if collecting and not moving and (timestamp - movement_start_time > 0.5):
                collecting = False
                movement_end_time = timestamp
                print(f"🛑 Movement Ended @ {time.strftime('%H:%M:%S', time.localtime(timestamp))}")

                if len(movement_data) > 2:
                    # Process collected movement data
                    resampled_segment = resample_segment(movement_data, target_segment_size)
                    features = compute_features(resampled_segment)
                    features_scaled = scaler.transform([features])
                    features_lda = lda.transform(features_scaled)

                    prediction = svm_model.predict(features_lda)
                    door_state = "Open" if prediction[0] == 1 else "Closed"
                    print(f"🚪 Door State: {door_state}")
                    msg = json.dumps({"Door State": door_state, "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))})
                    mqtt_client.publish(TOPIC, msg)

        time.sleep(0.1)  # Sampling rate ~10 Hz

if __name__ == "__main__":
    predict_state()
