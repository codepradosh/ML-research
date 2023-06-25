import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from scipy.stats import genextreme

# Step 1: Load the dataset
df = pd.read_csv('disk_metrics.csv')

# Step 2: Preprocess the dataset
df['Disk Average IO Label'] = np.where(df['Average_IO'] > 10, 1, 0)
df['Label Disk Queue Time'] = np.where(df['Queue_Size'] > 10, 1, 0)
df['Disk Health'] = np.where(df['IO_Time'] > 30, 1, 0)

# Step 3: Combine the metrics
combined_df = df[['Time', 'Average_IO', 'Queue_Size', 'IO_Time', 'Disk Average IO Label', 'Label Disk Queue Time', 'Disk Health']]

# Step 4: Feature engineering
combined_df['Average_IO_Squared'] = combined_df['Average_IO'] ** 2
combined_df['Queue_Size_Log'] = np.log1p(combined_df['Queue_Size'])
combined_df['IO_Time_Divided_By_Average_IO'] = combined_df['IO_Time'] / combined_df['Average_IO']
combined_df['Queue_Size_Squared_Root'] = np.sqrt(combined_df['Queue_Size'])
combined_df['IO_Average_Ratio_Log'] = np.log1p(combined_df['IO_Time'] / combined_df['Average_IO'])
combined_df['IO_Average_Product'] = combined_df['IO_Time'] * combined_df['Average_IO']
combined_df['Queue_Size_Cubed'] = combined_df['Queue_Size'] ** 3

# Lagged features
combined_df['Average_IO_Lag1'] = combined_df['Average_IO'].shift(1)
combined_df['Queue_Size_Lag1'] = combined_df['Queue_Size'].shift(1)
combined_df['IO_Time_Lag1'] = combined_df['IO_Time'].shift(1)

# Rolling statistics
combined_df['Average_IO_RollingMean'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).mean()
combined_df['Queue_Size_RollingMean'] = combined_df['Queue_Size'].rolling(window=5, min_periods=1).mean()
combined_df['IO_Time_RollingMean'] = combined_df['IO_Time'].rolling(window=5, min_periods=1).mean()
combined_df['Average_IO_RollingStd'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).std()
combined_df['Queue_Size_RollingStd'] = combined_df['Queue_Size'].rolling(window=5, min_periods=1).std()
combined_df['IO_Time_RollingStd'] = combined_df['IO_Time'].rolling(window=5, min_periods=1).std()

# Step 5: Feature scaling
scaler = StandardScaler()
scaled_data = scaler.fit_transform(combined_df.drop(columns=['Time', 'Disk Average IO Label', 'Label Disk Queue Time', 'Disk Health']))

# Step 6: Prepare data for LSTM
X = scaled_data.reshape(scaled_data.shape[0], 1, scaled_data.shape[1])
y = combined_df[['Disk Average IO Label', 'Label Disk Queue Time', 'Disk Health']].values

# Step 7: Build LSTM model
model = Sequential()
model.add(LSTM(64, input_shape=(1, X.shape[2])))
model.add(Dense(3, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam')

# Step 8: Train LSTM model
model.fit(X, y, epochs=10, batch_size=16, verbose=1)

# Step 9: Calculate composite scores for training data
train_composite_scores = model.predict(X)

# Step 10: Determine the dynamic threshold for the training data using Extreme Value Distribution
threshold = genextreme.ppf(0.95, loc=np.mean(train_composite_scores[:, 0]), scale=np.std(train_composite_scores[:, 0]))

# Step 11: Plot the composite function with the dynamic threshold for the training data
plt.figure(figsize=(10, 6))
plt.plot(df['Time'], train_composite_scores[:, 0], color='blue')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Composite Function Graph')
plt.legend()
plt.show()

# Step 12: Determine disk health and busyness levels for the training data
disk_health = np.where(train_composite_scores[:, 0] <= threshold, 'Healthy', 'Unhealthy')
busyness_levels = np.where(train_composite_scores[:, 0] <= threshold, 'Low', 'High')

# Print the resulting composite scores, disk health, and busyness levels for the training data
result_df = pd.DataFrame({'Time': df['Time'], 'Composite Score': train_composite_scores[:, 0], 'Disk Health': disk_health, 'Busyness Levels': busyness_levels})
print(result_df)
