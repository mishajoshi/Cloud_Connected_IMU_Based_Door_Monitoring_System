# System Overview: IMU Door State Monitor

## 1. Introduction and Purpose

### What is the Device?
The **IMU Door State Monitor** is an IoT-based door-monitoring system that uses an **MPU6050 IMU sensor** attached to a door to capture motion and orientation data. A **Raspberry Pi 5** collects sensor data, classifies door states using a machine learning model, and communicates status updates via **AWS IoT Core**.

### Intended Application
This system is designed for **real-time door monitoring** in **security and access control applications**. It is useful for:
- Homeowners
- Small business owners
- Security professionals

### Why Was It Created?
The project was developed to provide hands-on experience in **working with real sensors, analytics tools, and cloud-based platforms**.

### Key Benefits
- **Real-time event detection**
- **Robust data processing** using a trained **SVM classifier**
- **Secure cloud communication** via **AWS IoT**
- **User-friendly interface** for monitoring status and receiving alerts

## 2. Device Functionality

### Core Capabilities
The device continuously monitors door movement by:
- Collecting raw **accelerometer and gyroscope data** from the **MPU6050**
- Processing this data using an **SVM classifier** to determine whether the door is **open or closed**
- Publishing the result to **AWS IoT** for cloud-based storage and monitoring

### Data Collection and Processing
1. **`data_collection.py`** captures and stores sensor readings in CSV format.
2. **Feature extraction** (Mean, Variance, FFT) is applied in:
   - The **training module (`train_svm.py`)**
   - The **real-time prediction module (`predict_svm.py`)**
3. The **trained SVM classifier** determines the door state, and the result is published via **MQTT**.
4. **Dynamic movement detection** is implemented using an adaptive threshold approach to minimize false positives.
5. **Real-time processing in `predict_svm.py`** includes segmentation, feature extraction, and classification before publishing results.

### Connectivity
- The **Raspberry Pi 5** connects via **Wi-Fi**.
- Sensor data is transmitted using **MQTT**.
- The system **does not use a local broker** like we did in our last project—instead, **AWS IoT Core** acts as the **MQTT broker**.

## 3. Key Components

### **Hardware**
- **MPU6050 IMU Sensor**: Captures acceleration and gyroscopic data.
- **Raspberry Pi 5**: Processes sensor data and runs prediction scripts.

### **Software**
| Component  | Description |
|------------|-------------|
| **Data Collection (`data_collection.py`)** | Reads sensor data, detects movement, and logs raw data to a CSV file. Implements an adaptive threshold for movement detection. |
| **Prediction Module (`predict_svm.py`)** | Processes live sensor data, applies real-time feature extraction (Mean, Variance, FFT), predicts door status, and publishes to AWS MQTT. Includes adaptive noise filtering and thresholding. |
| **Training Module (`train_svm.py`)** | Trains and saves the **SVM classifier**, scaler, and LDA for feature transformation. Implements cross-validation and hyperparameter tuning. |
| **User Interface** | **Flask app (`app.py`)** with **Socket.IO integration**, `index.html`, and `main.js` to display real-time updates. |
| **MQTT Client (`mqtt_client.py`)** | Subscribes to door status topics and updates the web UI. Implements WebSocket communication for real-time updates. |

### Connectivity
- **MQTT over TLS/SSL** ensures **secure communication**.
- **AWS IoT Core** is used as the cloud broker.

## 4. Machine Learning

### **Feature Extraction & Selection**

#### 1. **Mean & Variance**
- **Purpose**: Helps differentiate between **movement and stillness**.
- **Benefit**: Reduces noise while keeping key motion information.

#### 2. **Fast Fourier Transform (FFT)**
- **Purpose**: Converts raw motion data to the frequency domain.
- **Benefit**: Helps detect unusual motion patterns (e.g., forced entry).

#### 3. **Standardization & Dimensionality Reduction**
- **StandardScaler** normalizes features.
- **Linear Discriminant Analysis (LDA)** reduces feature space.
- **Benefit**: Increases model efficiency and generalization.

### **Classifier Training**
1. **Data Collection & Segmentation**
   - Sensor data is logged in `imu_raw_data.csv` and segmented into **fixed intervals of 10 readings per segment**.
2. **Feature Extraction & Scaling**
   - Extracted features are standardized using **StandardScaler**.
   - **LDA reduces dimensionality** while preserving motion patterns.
3. **Training & Cross-Validation**
   - The dataset is split into **80% training and 20% testing**.
   - The **SVM classifier** is trained using the **RBF kernel**.
   - **5-fold cross-validation** ensures model generalization.
4. **Model Deployment**
   - Saves **SVM model, scaler, and LDA transformation** as `.pkl` files.
   - Used in `predict_svm.py` for real-time classification.

## 5. System Architecture
### Diagram
#### Breadboard View
![image](https://github.ncsu.edu/juwujar/csc_591_spring2025_hw3/assets/35190/951ef325-7000-42c1-b0dc-1bcfd03fbe85)

#### Schematic View
![image](https://github.ncsu.edu/juwujar/csc_591_spring2025_hw3/assets/35190/13622ea2-8901-4f9b-af60-fecc566ba319)

#### Live Image of IoT Device Setup
![WhatsApp Image 2025-03-19 at 19 40 23_66b0f6f9](https://github.ncsu.edu/juwujar/csc_591_spring2025_hw3/assets/35190/60c94e71-179f-4df3-8755-a7254beba604)

### **Data Flow**
![image](https://github.ncsu.edu/juwujar/csc_591_spring2025_hw3/assets/35190/9bbe0fbc-cd4c-4fe9-8f6f-25692a3f3c69)

### **Inter-Device Communication**
- **Raspberry Pi → AWS IoT** (publishes door status via MQTT)
- **AWS IoT → Flask App** (web interface subscribes & displays updates)

## 6. Security Considerations

### **Data Encryption**
- Uses **TLS/SSL** to encrypt MQTT messages.

### **Authentication & Authorization**
- Requires **client certificates & private keys** for MQTT connections.
- **AWS IoT policies** restrict unauthorized access.

## 7. Deployment and Maintenance

### **Installation Steps**
1. **Assemble Hardware** (Connect MPU6050 to Raspberry Pi 5)
2. **Install Required Software Packages**
   ```bash
   pip install flask flask-socketio eventlet paho-mqtt python-dotenv
   ```
3. **Configure AWS IoT Credentials** in `.env`
4. **Run Prediction & UI Services**
   ```bash
   python predict_svm.py & python app.py
   ```
## 8. Code Overview

### **Data Collection (`data_collection.py`)**
- Implements **adaptive movement detection** to reduce false positives.
- Logs IMU sensor data into a CSV file.

### **Prediction Module (`predict_svm.py`)**
- Implements **real-time noise calibration**.
- Extracts and normalizes features before classification.
- Publishes results to **AWS IoT MQTT endpoint**.

### **Training Module (`train_svm.py`)**
- Implements **cross-validation and hyperparameter tuning**.
- Saves **scaler, LDA, and classifier** for real-time predictions.

### **MQTT Client (`mqtt_client.py`)**
- **Subscribes** to MQTT topics.
- **Updates Web UI** using WebSockets.
