import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import StandardScaler
from scipy.stats import genextreme

df = pd.read_csv('disk_metrics1.csv')
df.head()

df['Disk Average IO Label'] = np.where(df['Average_IO'] > 10, 1, 0)
df['Label Disk Queue Time'] = np.where(df['Queue_Size'] > 10, 1, 0)
df['Disk_Health'] = np.where(df['IO_Time'] > 30, 1, 0)
df['Writes_Label'] = np.where(df['Writes'] > 1000, 1, 0)
df['Reads_Label'] = np.where(df['Reads'] > 250, 1, 0)

combined_df = df[['Time', 'Average_IO', 'Queue_Size', 'IO_Time', 'Writes', 'Reads', 'Disk_Health',
                  'Disk Average IO Label', 'Label Disk Queue Time', 'Writes_Label', 'Reads_Label']]

combined_df['Average IO Time Rolling Mean'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).mean()
combined_df['Queue Size Lag 1'] = combined_df['Queue_Size'].shift(1)
combined_df['IO Time Rolling Mean'] = combined_df['IO_Time'].rolling(window=5, min_periods=1).mean()
combined_df['Reads_Rolling Mean'] = combined_df['Reads'].rolling(window=5, min_periods=1).mean()
combined_df['Writes_Rolling Mean'] = combined_df['Writes'].rolling(window=5, min_periods=1).mean()
combined_df['Reads_Lag 1'] = combined_df['Reads'].shift(1)
combined_df['Writes_Lag 1'] = combined_df['Writes'].shift(1)
combined_df['DayOfWeek'] = pd.to_datetime(combined_df['Time']).dt.dayofweek
combined_df['HourOfDay'] = pd.to_datetime(combined_df['Time']).dt.hour

combined_df = combined_df.dropna()

scaler = StandardScaler()
scaled_data = scaler.fit_transform(combined_df[['Average_IO', 'Queue_Size', 'IO_Time', 'Writes', 'Reads',
                                                 'Average IO Time Rolling Mean', 'Queue Size Lag 1',
                                                 'IO Time Rolling Mean', 'Reads_Rolling Mean',
                                                 'Writes_Rolling Mean', 'Reads_Lag 1', 'Writes_Lag 1',
                                                 'DayOfWeek', 'HourOfDay', 'Writes_Label', 'Reads_Label']])

X = scaled_data
y = combined_df[['Disk_Health', 'Disk Average IO Label', 'Label Disk Queue Time', 'Writes_Label', 'Reads_Label']]
model = RandomForestClassifier()
model.fit(X, y)
feature_importances = model.feature_importances_
print(feature_importances)

composite_scores = np.dot(X, feature_importances)
shape_param = genextreme.fit(composite_scores)[0]
threshold = genextreme.ppf(0.80, shape_param, loc=np.mean(composite_scores), scale=np.std(composite_scores))
disk_health = np.where(composite_scores <= threshold, 'Healthy', 'Unhealthy')
business_levels = np.where(composite_scores <= threshold, 'Low', 'High')

combined_df['Time'] = pd.to_datetime(df['Time'])
combined_df['Composite_Scores'] = composite_scores

plt.figure(figsize=(10, 6))
plt.plot(combined_df['Time'], composite_scores, color='blue')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Composite Function Graph')
plt.legend()
plt.show()

# Zoomed Composite Graph for any time date
start_date = '2023-05-01'
end_date = '2023-06-05'
start_time = '08:00:00'
end_time = '11:00:00'
start_datetime = pd.to_datetime(start_date + ' ' + start_time)
end_datetime = pd.to_datetime(end_date + ' ' + end_time)
mask = (combined_df['Time'] >= start_datetime) & (combined_df['Time'] <= end_datetime)
zoomed_scores = composite_scores[mask]
zoomed_time = combined_df['Time'][mask]

plt.figure(figsize=(12, 6))
plt.plot(zoomed_time, zoomed_scores, color='blue')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Zoomed Composite Graph')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
