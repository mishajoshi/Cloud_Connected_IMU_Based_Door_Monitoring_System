# IMU Data Collection and Prediction

This IoT Device code demonstrates how to collect and process motion data from an MPU6050 sensor using a Raspberry Pi. The code is divided into three main components:

## Data Collection (`data_collection.py`)
Reads raw accelerometer and gyroscope data from the MPU6050 sensor. It performs a calibration step, detects movement using adaptive thresholds, and saves labeled movement segments of "Open" or "Close" to a CSV file.

## Training the SVM Model (`train_svm.py`)
Processes collected IMU data, extracts features (Mean, Variance, FFT), applies feature scaling and dimensionality reduction (LDA), and trains a Support Vector Machine (SVM) model. The trained model, scaler, and LDA transformation are saved as `.pkl` files for real-time prediction.

## Real-Time Prediction (`predict_svm.py`)
Collects IMU data in real time, processes it through a pre-trained SVM model (using the saved scaler and LDA transformation), and predicts the door state (open/closed). The predicted state is then published via MQTT (configured for AWS IoT).

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)

## Features

### Calibration:
The data collection script calibrates the sensor by recording a baseline while the sensor is kept still. Mean and standard deviation values are used to set dynamic movement thresholds.

### Adaptive Movement Detection:
Using a sliding window of IMU readings, the script detects movement based on deviations from the baseline.

### User Labeling:
After a movement event is detected, the user is prompted to label the event as "Open", "Close", or "Ignore".

### Model Training:
The `train_svm.py` script processes labeled data, extracts features, scales them, applies dimensionality reduction, and trains an SVM model. The trained model is then saved for real-time use.

### Real-Time Prediction:
The prediction script uses a pre-trained SVM model to classify real-time IMU data and publishes the result via MQTT to AWS IoT.

## Prerequisites

### Hardware:
- MPU6050 sensor
- Raspberry Pi
- MQTT broker credentials for AWS IoT

### Software:
- Python 3.x
- [mpu6050](https://pypi.org/project/mpu6050-raspberrypi/) Python library
- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Joblib](https://joblib.readthedocs.io/) (for model loading)
- [paho-mqtt](https://pypi.org/project/paho-mqtt/) (for MQTT communication)
- [SciPy](https://www.scipy.org/) (for interpolation)
- [python-dotenv](https://pypi.org/project/python-dotenv/) (for loading environment variables)
- [scikit-learn](https://scikit-learn.org/) (for training the SVM model)

## Installation

### Clone the repository:
```bash
git clone https://github.ncsu.edu/juwujar/csc_591_spring2025_hw3
cd csc_591_spring2025_hw3
```

### Install required Python packages:
```bash
pip install numpy pandas matplotlib joblib paho-mqtt scipy mpu6050-raspberrypi python-dotenv scikit-learn
```
## Configuration

### Create a `.env` file (not included in the repository) and define the following environment variables:
```ini
AWS_ENDPOINT=your-aws-endpoint
MQTT_PORT=your-mqtt-port
TOPIC=your-topic
CLIENT_ID=your-client-id
KEEPALIVE=60

ROOT_CA=./Certificates/AmazonRootCA1.pem
CERTIFICATE_PATH=./Certificates/certificate.pem.crt
PRIVATE_KEY_PATH=./Certificates/private.pem.key

SECRET_KEY=your-secret-key
```

### Generating a Secure Secret Key:
If you need to generate a secure `SECRET_KEY`, you can use Python’s `secrets` module:
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```
Copy and paste this into your `.env` file under `SECRET_KEY`.

### Ensure `config.py` loads the `.env` file:
```python
from dotenv import load_dotenv
import os

load_dotenv()

AWS_ENDPOINT = os.getenv("AWS_ENDPOINT")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
KEEPALIVE = int(os.getenv("KEEPALIVE", 60))
TOPIC = os.getenv("TOPIC")
CLIENT_ID = os.getenv("CLIENT_ID")

ROOT_CA = os.getenv("ROOT_CA")
CERTIFICATE_PATH = os.getenv("CERTIFICATE_PATH")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")

SECRET_KEY = os.getenv("SECRET_KEY")
```

## Usage

### Running Data Collection
```bash
python data_collection.py
```

### Training the SVM Model
```bash
python train_svm.py
```

This will:
- Load `imu_raw_data.csv`
- Extract and scale features
- Train the SVM model
- Save `svm_rbf_door_model.pkl`, `scaler.pkl`, and `lda.pkl`

### Running Real-Time Prediction
```bash
python predict_svm.py
```

This will:
- Collect live IMU sensor data
- Process features and apply the pre-trained SVM model
- Publish the predicted door state to AWS IoT via MQTT
