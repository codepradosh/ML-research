import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import STL
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

df = pd.DataFrame({'timestamp': date_rng, 'value': data, 'seasonality': seasonality, 'trend': trend, 'noise': noise})


stl = STL(df['value'], seasonal=13) 
result = stl.fit()
df['seasonality'] = result.seasonal
df['trend'] = result.trend
df['residual'] = result.resid


window_size = 3 
df['seasonality_moving_avg'] = df['seasonality'].rolling(window=window_size, min_periods=1).mean()
df['trend_moving_avg'] = df['trend'].rolling(window=window_size, min_periods=1).mean()
df['residual_moving_avg'] = df['residual'].rolling(window=window_size, min_periods=1).mean()


scaler = MinMaxScaler()  #logscaling of data
features = ['seasonality', 'trend', 'residual', 'seasonality_moving_avg', 'trend_moving_avg', 'residual_moving_avg']
df[features] = scaler.fit_transform(df[features])

# Plot the original data and the decomposed components
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['value'], label='Original Data', color='blue')
plt.plot(df['timestamp'], df['seasonality'], label='Seasonality', color='red')
plt.plot(df['timestamp'], df['trend'], label='Trend', color='green')
plt.plot(df['timestamp'], df['residual'], label='Residual', color='purple')
plt.legend()
plt.title('Original Data and Decomposed Components')
plt.xlabel('Timestamp')
plt.ylabel('Value')
plt.show()

mean_residual = df['residual'].mean()
std_residual = df['residual'].std()
df['residual_z_score'] = (df['residual'] - mean_residual) / std_residual

# Set a 3-sigma threshold for anomaly detection
threshold = 3

# Detect anomalies based on the residual z-scores and threshold
anomalies = np.abs(df['residual_z_score']) > threshold

# Print timestamps where anomalies are detected
anomaly_timestamps = df.loc[anomalies, 'timestamp']
print("Anomaly Timestamps:")
print(anomaly_timestamps)
In this code:



seasonality_amplitude = 10
seasonality_period = 24  # 24 hours for daily seasonality
trend_slope = 0.5
noise_stddev = 2

seasonality = seasonality_amplitude * np.sin(2 * np.pi * np.arange(len(date_rng)) / seasonality_period)
trend = trend_slope * np.arange(len(date_rng))
noise = np.random.normal(loc=0, scale=noise_stddev, size=len(date_rng))

# Create a DataFrame for the components
component_df = pd.DataFrame({'seasonality': seasonality, 'trend': trend, 'noise': noise})

# Calculate moving averages on each component
window_size = 3 
component_df['seasonality_moving_avg'] = component_df['seasonality'].rolling(window=window_size, min_periods=1).mean()
component_df['trend_moving_avg'] = component_df['trend'].rolling(window=window_size, min_periods=1).mean()
component_df['residual_moving_avg'] = component_df['noise'].rolling(window=window_size, min_periods=1).mean()

# Combine the components with the original DataFrame
df['seasonality'] = component_df['seasonality']
df['trend'] = component_df['trend']
df['residual'] = component_df['noise']
df['seasonality_moving_avg'] = component_df['seasonality_moving_avg']
df['trend_moving_avg'] = component_df['trend_moving_avg']
df['residual_moving_avg'] = component_df['residual_moving_avg']





