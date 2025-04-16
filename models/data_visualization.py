import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("imu_raw_data.csv")  # Replace with your actual file name

# List of feature groups
accel_features = ["ax", "ay", "az"]
gyro_features = ["gx", "gy", "gz"]

# Get unique labels
labels = df["label"].unique()

# Plot acceleration features
plt.figure(figsize=(12, 5))
for label in labels:
    subset = df[df["label"] == label]
    for feature in accel_features:
        plt.plot(subset["timestamp"], subset[feature], label=f"{feature} (Label {label})", alpha=0.7)

plt.xlabel("Timestamp")
plt.ylabel("Acceleration")
plt.title("Acceleration Variance (ax, ay, az)")
plt.legend()
plt.show()

# Plot gyroscope features
plt.figure(figsize=(12, 5))
for label in labels:
    subset = df[df["label"] == label]
    for feature in gyro_features:
        plt.plot(subset["timestamp"], subset[feature], label=f"{feature} (Label {label})", alpha=0.7)

plt.xlabel("Timestamp")
plt.ylabel("Gyroscope")
plt.title("Gyroscope Variance (gx, gy, gz)")
plt.legend()
plt.show()
