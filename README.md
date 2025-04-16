# Web Interface for IMU-Based Door Monitoring System

This document provides detailed instructions on setting up and running the **web interface** for the IMU-based door monitoring system. This interface allows real-time monitoring of door movements using a **Flask web application** with MQTT integration.

## Overview

The web interface consists of:
- **Flask Server (`app.py`)**: Handles HTTP requests and WebSocket communication.
- **MQTT Client (`mqtt_client.py`)**: Listens to MQTT messages from the IoT device (Raspberry Pi) and updates the UI.
- **Frontend (`index.html` + `main.js`)**: Displays door state updates and logs events.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Web Interface](#running-the-web-interface)
- [Features](#features)
- [Project Structure](#project-structure)

## Prerequisites

- **Python 3.x** installed on the laptop or server.
- **Flask & WebSocket support** via `flask-socketio`.
- **MQTT support** using `paho-mqtt`.
- **Bootstrap for UI styling**.
- **Eventlet** for asynchronous WebSocket handling.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.ncsu.edu/juwujar/csc_591_spring2025_hw3
    cd csc_591_spring2025_hw3
    ```

2. **Install required Python packages:**
    ```bash
    pip install flask flask-socketio eventlet paho-mqtt python-dotenv
    ```

## Configuration

1. **Create a `.env` file** (not included in the repository) and define the following variables:
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

2. **Generate a Secure `SECRET_KEY`**:
   Run the following command in your terminal:
    ```bash
    python -c 'import secrets; print(secrets.token_hex(32))'
    ```
   Copy the generated key and add it to your `.env` file under `SECRET_KEY`.

## Running the Web Interface

1. **Start the Flask Web Server:**
    ```bash
    python app.py
    ```
2. **Access the UI in a Browser:**
    - Open: `http://localhost:5000`
    - If running on a remote machine, replace `localhost` with the server’s IP.
![image](https://github.ncsu.edu/juwujar/csc_591_spring2025_hw3/assets/35190/fb065463-5851-4ba0-8fb4-2d18415b8e66)

## Features

### Real-Time Door Monitoring
- Displays the **current door status** (`Open` / `Closed`).
- Shows **timestamp** of the latest update.
- Uses **WebSockets** for live updates.

### Interactive Controls
- **Pause**: Temporarily stop UI updates.
- **Resume**: Restart UI updates.
- **Stop**: Disconnects from the MQTT broker.
- **Clear Log**: Removes past updates from the UI.

### MQTT-Based Communication
- The **MQTT client** listens for updates from the Raspberry Pi.
- When a message is received, it triggers a WebSocket event to update the UI instantly.

## Project Structure

```
.
├── app.py                # Flask web app serving the UI and handling WebSocket communication
├── mqtt_client.py        # MQTT client subscribing to AWS IoT messages
├── static/
│   ├── js/main.js        # Frontend JavaScript for real-time updates
├── templates/
│   ├── index.html        # Web UI for monitoring door state
├── config.py             # Configuration file that loads environment variables from .env
├── .env                  # Environment file (not included in repo) for sensitive settings
```

This setup enables remote monitoring of the IoT-based door state detection system, allowing users to interact with real-time data in a user-friendly web interface.

## Acknowledgments

- Professor's Homework 3 document and class lecture.
- Open-source libraries and tools used in the project:
  - **NumPy**: For numerical operations and data manipulation.
  - **Pandas**: For data handling and preprocessing.
  - **Scikit-learn**: For machine learning model training and evaluation.
  - **Joblib**: For model serialization and loading.
  - **smbus**: For I2C communication with the IMU sensor.
  - **mpu6050**: For reading IMU sensor data.
  - **paho-mqtt**: For MQTT communication between Raspberry Pi and remote devices.
  - **EMQX**: MQTT broker for handling message transmission.
  - **csv**: For logging IMU data.
  - **time**: For timestamping and controlling execution timing.
  - **collections.deque**: For managing a rolling window of sensor data.
