import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from scipy.stats import genextreme

# Step 1: Load the dataset
df = pd.read_csv('disk_metrics.csv')

# Step 2: Preprocess the dataset
df['Disk Average IO Label'] = np.where(df['Average_IO'] > 10, 1, 0)
df['Label Disk Queue Time'] = np.where(df['Queue_Size'] > 10, 1, 0)

# Step 3: Combine the metrics
combined_df = df[['Time', 'Average_IO', 'Queue_Size', 'Disk Average IO Label', 'Label Disk Queue Time']]

# Step 4: Feature engineering
combined_df['Average IO Time Rolling Mean'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).mean()
combined_df['Queue Size Lag 1'] = combined_df['Queue_Size'].shift(1)
combined_df['DayOfWeek'] = pd.to_datetime(combined_df['Time']).dt.dayofweek
combined_df['HourOfDay'] = pd.to_datetime(combined_df['Time']).dt.hour

# Step 5: Feature scaling
scaler = StandardScaler()
scaled_data = scaler.fit_transform(combined_df[['Average_IO', 'Queue_Size', 'Average IO Time Rolling Mean', 'Queue Size Lag 1', 'DayOfWeek', 'HourOfDay']])

# Step 6: Calculate feature importances
X = scaled_data
y = combined_df[['Disk Average IO Label', 'Label Disk Queue Time']]
model = RandomForestClassifier()
model.fit(X, y)
feature_importances = model.feature_importances_

# Step 7: Calculate composite score
composite_scores = np.dot(X, feature_importances)

# Step 8: Determine dynamic threshold using extreme value distribution theorem
threshold = genextreme.ppf(0.95, loc=np.mean(composite_scores), scale=np.std(composite_scores))

# Step 9: Determine disk health and busyness levels
disk_health = np.where(composite_scores <= threshold, 'Healthy', 'Unhealthy')
busyness_levels = np.where(composite_scores <= threshold, 'Low', 'High')

# Step 10: Plot the composite function graph
plt.figure(figsize=(10, 6))
plt.plot(df['Time'], composite_scores, color='blue')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Composite Function Graph')
plt.legend()
plt.show()

# Print the resulting composite scores, disk health, and busyness levels
result_df = pd.DataFrame({'Time': df['Time'], 'Composite Score': composite_scores, 'Disk Health': disk_health, 'Busyness Levels': busyness_levels})
print(result_df)


result_df['Time'] = pd.to_datetime(result_df['Time'])  # Convert 'Time' column to datetime

# Plot the composite scores with respect to time
plt.figure(figsize=(10, 6))
plt.plot(result_df['Time'], result_df['Composite Score'], color='blue')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Composite Function Graph')
plt.legend()
plt.show()

result_df['Time'] = pd.to_datetime(result_df['Time'])  # Convert 'Time' column to datetime

# Set the time range for zooming in
start_time = '2023-01-01 00:00:00'
end_time = '2023-02-01 00:00:00'

# Filter the data within the specified time range
zoomed_df = result_df[(result_df['Time'] >= start_time) & (result_df['Time'] <= end_time)]

# Plot the composite scores within the zoomed time range
plt.figure(figsize=(10, 6))
plt.plot(zoomed_df['Time'], zoomed_df['Composite Score'], color='blue')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Zoomed Composite Function Graph')
plt.legend()
plt.xlim(start_time, end_time)  # Set the x-axis limits
plt.show()





result_df['Time'] = pd.to_datetime(result_df['Time'])  # Convert 'Time' column to datetime

# Set the time range for zooming
start_time = pd.to_datetime('2023-01-01 00:00:00')
end_time = pd.to_datetime('2023-02-01 00:00:00')

# Filter the data within the specified time range
zoomed_df = result_df[(result_df['Time'] >= start_time) & (result_df['Time'] <= end_time)]

# Find the spikes (Composite scores above the threshold)
spike_df = zoomed_df[zoomed_df['Composite Score'] > threshold]

# Plot the composite scores within the zoomed time range
plt.figure(figsize=(10, 6))
plt.plot(zoomed_df['Time'], zoomed_df['Composite Score'], color='blue')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.scatter(spike_df['Time'], spike_df['Composite Score'], color='red', label='Spikes')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Zoomed Composite Function Graph')
plt.legend()
plt.xlim(start_time, end_time)  # Set the x-axis limits
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.show()

# Print the timestamps of spikes
print("Spikes Timestamps:")
print(spike_df['Time'])


