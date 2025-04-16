import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from scipy.interpolate import interp1d
from collections import Counter

def compute_features(data):
    data_arr = np.array(data)
    mean_vals = np.mean(data_arr, axis=0)
    var_vals = np.var(data_arr, axis=0)
    fft_vals = np.abs(np.fft.fft(data_arr, axis=0))[0]

    return np.concatenate([mean_vals, var_vals, fft_vals])

def resample_segment(segment, target_size=10):
    """ Resample the segment to a fixed number of rows (target_size) using interpolation or padding """
    segment = np.array(segment)
    original_size = len(segment)
    
    if original_size == target_size:
        return segment
    
    # If more rows than target, sample evenly
    if original_size > target_size:
        indices = np.linspace(0, original_size - 1, target_size).astype(int)
        return segment[indices]
    
    # If fewer rows than target, interpolate or pad
    x_original = np.linspace(0, 1, original_size)
    x_target = np.linspace(0, 1, target_size)
    
    # Interpolating each column separately
    interpolated = np.array([interp1d(x_original, segment[:, col], kind='linear', fill_value="extrapolate")(x_target) 
                             for col in range(segment.shape[1])]).T
    return interpolated

def load_and_process_data(filename="imu_raw_data.csv", time_threshold=0.5, target_size=100):
    df = pd.read_csv(filename)
    
    # Convert timestamp column to numeric
    df["timestamp"] = pd.to_numeric(df["timestamp"])
    
    # Sort by time to ensure proper grouping
    df = df.sort_values(by="timestamp")
    
    features = []
    labels = []
    
    prev_timestamp = None
    current_segment = []
    current_label = None

    for _, row in df.iterrows():
        timestamp = row["timestamp"]
        label = row["label"]
        imu_values = row.drop(["timestamp", "label"]).values  # Extract sensor data

        if prev_timestamp is None:
            prev_timestamp = timestamp
            current_segment.append(imu_values)
            current_label = label
            continue

        # If time difference is too large OR label changes, process previous segment
        if (timestamp - prev_timestamp > time_threshold) or (label != current_label):
            if len(current_segment) > 2:  # Ensure it's a valid movement
                resampled_segment = resample_segment(current_segment, target_size)
                features.append(compute_features(resampled_segment))
                labels.append(current_label)

            # Start new segment
            current_segment = [imu_values]
            current_label = label
        else:
            current_segment.append(imu_values)

        prev_timestamp = timestamp

    # Process the last segment
    if len(current_segment) > 2:
        resampled_segment = resample_segment(current_segment, target_size)
        features.append(compute_features(resampled_segment))
        labels.append(current_label)

    return np.array(features), np.array(labels)

features, labels = load_and_process_data()
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

lda = LinearDiscriminantAnalysis(n_components=1)
features_lda = lda.fit_transform(features_scaled, labels)

# Split dataset into training and test sets
X_train, X_test, y_train, y_test = train_test_split(features_lda, labels, test_size=0.3, random_state=42)
print(f"Total Samples: {len(features)}")
print(f"Training Samples: {len(X_train)}")
print(f"Test Samples: {len(X_test)}")
print(f"Unique Labels in Training: {set(y_train)}")
print(f"Unique Labels in Test: {set(y_test)}")
print("Training Label Distribution:", Counter(y_train))
print("Test Label Distribution:", Counter(y_test))


svm_model = SVC(kernel="rbf", gamma="scale", class_weight="balanced")
svm_model.fit(X_train, y_train)

# Compute accuracy
train_accuracy = svm_model.score(X_train, y_train)
test_accuracy = svm_model.score(X_test, y_test)

# Cross-validation accuracy
cv_scores = cross_val_score(svm_model, features_lda, labels, cv=5)
cv_accuracy = np.mean(cv_scores)

# Print accuracy results
print(f"Training Accuracy: {train_accuracy * 100:.2f}%")
print(f"Test Accuracy: {test_accuracy * 100:.2f}%")
print(f"Cross-Validation Accuracy: {cv_accuracy * 100:.2f}%")

# Save models
joblib.dump(scaler, "scaler.pkl")
joblib.dump(lda, "lda.pkl")
joblib.dump(svm_model, "svm_rbf_door_model.pkl")
print("Training complete! Model saved.")
