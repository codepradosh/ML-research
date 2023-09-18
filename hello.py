import numpy as np
from collections import deque
from datetime import datetime, timedelta

def log_transform(data):
    """Apply log transformation to data."""
    return np.log(data + 1)

def calculate_threshold(data, num_sigma=3):
    """Calculate the threshold using mean and standard deviation."""
    mu = np.mean(data)
    sigma = np.std(data)
    return mu + num_sigma * sigma

def detect_anomalies(data, threshold):
    """Detect anomalies above the given threshold."""
    return data[data > threshold]

def check_hour(anomaly_time, hour_windows):
    """Check and update the hour windows for anomaly counting."""
    if not hour_windows or anomaly_time >= hour_windows[-1][0]:
        hour_windows.append([anomaly_time, 0])

    for hour, _ in hour_windows:
        if anomaly_time >= hour:
            hour_windows[-1][1] += 1

def trigger_alert(hour_windows, max_allowed_anomalies=5):
    """Trigger an alert if anomalies exceed the allowed limit."""
    for hour, count in hour_windows:
        if count > max_allowed_anomalies:
            print(f"Alert! {count} anomalies detected in hour {hour}")

# Provided timestamps and predicted values
timestamps_predicted = [
    "2023-02-20 08:00:00", "2023-02-20 08:30:00", "2023-02-20 09:00:00",  # Replace with actual timestamps
    # ...
]

predicted_values = [
    21.5, 22.8, 13.6, 14.5, 13.8, 13.9, 12.9, 17.8, 16.4, 40.7, 58.3, 43.9, 69.2, 34.2
    # Replace with your predicted values
]

# Convert timestamps to datetime objects
timestamp_objects_predicted = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in timestamps_predicted]

# Combine timestamps and predicted values into a list of tuples
data_points_predicted = list(zip(timestamp_objects_predicted, predicted_values))

# Provided actual timestamps and values (adjusted to match the size of predicted values)
timestamps_actual = [
    "2023-02-20 08:00:00", "2023-02-20 08:30:00", "2023-02-20 09:00:00",  # Replace with actual timestamps
    # ...
]

actual_values = [
    16.3, 18.9, 15.4, 15.8, 18, 13.5, 11.4, 11.8, 12.4, 12.3, 16.8, 16.4, 21.6, 15.5, 13.6
    # Replace with your actual values
]

# Convert timestamps to datetime objects
timestamp_objects_actual = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in timestamps_actual]

# Combine timestamps and actual values into a list of tuples
data_points_actual = list(zip(timestamp_objects_actual, actual_values))

# Ensure both lists have the same length (adjust if needed)
min_length = min(len(data_points_predicted), len(data_points_actual))
data_points_predicted = data_points_predicted[:min_length]
data_points_actual = data_points_actual[:min_length]

# Calculate errors (differences between predicted and actual values)
errors = np.abs(np.array(predicted_values) - np.array(actual_values))

# Log transform errors
errors_log = log_transform(errors)

# Calculate threshold for anomalies
threshold = calculate_threshold(errors_log)

# Detect anomalies
anomalies = detect_anomalies(errors_log, threshold)

# Track the last 5 hours
hour_windows = deque(maxlen=5)

# Simulate anomaly timestamps (use actual timestamps if available)
for i, (timestamp, _) in enumerate(data_points_predicted):
    check_hour(timestamp, hour_windows)

# Trigger an alert if anomalies exceed 5
trigger_alert(hour_windows, max_allowed_anomalies=5)
