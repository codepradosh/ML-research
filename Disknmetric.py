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
df['Disk Health'] = np.where(df['IO_Time'] > 30, 1, 0)
df['Disk Average IO Label'] = np.where(df['Average_IO'] > 10, 1, 0)
df['Label Disk Queue Time'] = np.where(df['Queue_Size'] > 10, 1, 0)

# Step 3: Combine the metrics
combined_df = df[['Time', 'Average_IO', 'Queue_Size', 'IO_Time', 'Disk Health', 'Disk Average IO Label', 'Label Disk Queue Time']]

# Step 4: Feature engineering
combined_df['Average_IO_Squared'] = combined_df['Average_IO'] ** 2  # Square of Average_IO
combined_df['Queue_Size_Log'] = np.log1p(combined_df['Queue_Size'])  # Logarithm of Queue_Size
combined_df['IO_Time_Divided_By_Average_IO'] = combined_df['IO_Time'] / combined_df['Average_IO']  # Ratio of IO_Time to Average_IO
combined_df['Queue_Size_Squared_Root'] = np.sqrt(combined_df['Queue_Size'])  # Square root of Queue_Size
combined_df['IO_Average_Ratio_Log'] = np.log1p(combined_df['IO_Time'] / combined_df['Average_IO'])  # Logarithm of IO_Time divided by Average_IO
combined_df['IO_Average_Product'] = combined_df['IO_Time'] * combined_df['Average_IO']  # Product of IO_Time and Average_IO
combined_df['Queue_Size_Cubed'] = combined_df['Queue_Size'] ** 3  # Cube of Queue_Size

# Lagged features
combined_df['Average_IO_Lag1'] = combined_df['Average_IO'].shift(1)  # Lagged Average_IO (t-1)
combined_df['Queue_Size_Lag1'] = combined_df['Queue_Size'].shift(1)  # Lagged Queue_Size (t-1)
combined_df['IO_Time_Lag1'] = combined_df['IO_Time'].shift(1)  # Lagged IO_Time (t-1)

# Rolling statistics
combined_df['Average_IO_RollingMean'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).mean()  # Rolling mean of Average_IO
combined_df['Queue_Size_RollingMean'] = combined_df['Queue_Size'].rolling(window=5, min_periods=1).mean()  # Rolling mean of Queue_Size
combined_df['IO_Time_RollingMean'] = combined_df['IO_Time'].rolling(window=5, min_periods=1).mean()  # Rolling mean of IO_Time
combined_df['Average_IO_RollingStd'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).std()  # Rolling standard deviation of Average_IO
combined_df['Queue_Size_RollingStd'] = combined_df['Queue_Size'].rolling(window=5, min_periods=1).std()  # Rolling standard deviation of Queue_Size
combined_df['IO_Time_RollingStd'] = combined_df['IO_Time'].rolling(window=5, min_periods=1).std()  # Rolling standard deviation of IO_Time

# Step 5: Feature scaling
scaler = StandardScaler()
scaled_data = scaler.fit_transform(combined_df.drop(['Time'], axis=1))

# Step 6: Prepare the input data for LSTM
X = scaled_data[:-1]  # Input sequence
y = combined_df[['Disk Health', 'Disk Average IO Label', 'Label Disk Queue Time']][1:]  # Predicted labels

# Reshape the input data into the required format for LSTM (samples, time steps, features)
X = np.reshape(X, (X.shape[0], 1, X.shape[1]))

# Step 7: Build the LSTM model
model = Sequential()
model.add(LSTM(64, input_shape=(X.shape[1], X.shape[2])))
model.add(Dense(32, activation='relu'))
model.add(Dense(y.shape[1], activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam')

# Step 8: Train the model
model.fit(X, y, epochs=50, batch_size=32)

# Step 9: Calculate feature importances
feature_importances = model.layers[0].get_weights()[0]  # Get the weights of the LSTM layer

# Step 10: Create the composite function in real-time
def create_composite_function(input_data):
    scaled_input = scaler.transform(input_data)
    reshaped_input = np.reshape(scaled_input, (1, 1, scaled_input.shape[1]))
    composite_score = model.predict(reshaped_input)
    return composite_score

# Step 11: Determine the dynamic threshold using extreme value distribution
def calculate_threshold(composite_scores):
    threshold = genextreme.ppf(0.95, loc=np.mean(composite_scores), scale=np.std(composite_scores))
    return threshold

# Step 12: Visualize the composite function in real-time with dynamic threshold
def plot_composite_function(time, composite_scores, threshold):
    plt.figure(figsize=(10, 6))
    plt.plot(time, composite_scores, color='blue')
    plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
    plt.xlabel('Time')
    plt.ylabel('Composite Score')
    plt.title('Composite Function Graph')
    plt.legend()
    plt.show()

# Step 9: Calculate feature importances
feature_importances = model.layers[0].get_weights()[0]  # Get the weights of the LSTM layer

# Step 10: Create the composite function in real-time
def create_composite_function(input_data):
    scaled_input = scaler.transform(input_data)
    reshaped_input = np.reshape(scaled_input, (1, 1, scaled_input.shape[1]))
    composite_score = model.predict(reshaped_input)
    return composite_score

# Step 11: Determine the dynamic threshold using extreme value distribution
def calculate_threshold(composite_scores):
    threshold = genextreme.ppf(0.95, loc=np.mean(composite_scores), scale=np.std(composite_scores))
    return threshold

# Step 12: Visualize the composite function in real-time with dynamic threshold
def plot_composite_function(time, composite_scores, threshold):
    plt.figure(figsize=(10, 6))
    plt.plot(time, composite_scores, color='blue')
    plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
    plt.xlabel('Time')
    plt.ylabel('Composite Score')
    plt.title('Composite Function Graph')
    plt.legend()
    plt.show()

# Get the composite scores for the training data
train_composite_scores = model.predict(X)

# Determine the dynamic threshold for the training data
train_threshold = genextreme.ppf(0.95, loc=np.mean(train_composite_scores), scale=np.std(train_composite_scores))

# Plot the composite function with the dynamic threshold for the training data
plt.figure(figsize=(10, 6))
plt.plot(combined_df['Time'][1:], train_composite_scores, color='blue')
plt.axhline(train_threshold, color='red', linestyle='--', label='Threshold')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Composite Function Graph')
plt.legend()
plt.show()





# Example usage:
# Assume you have real-time data for IO_Time, Average_IO, and Queue_Size
current_time = pd.Timestamp.now()
current_io_time = 25.5
current_average_io = 12.3
current_queue_size = 8.9

# Create a new row of data with the current values
new_data = pd.DataFrame({
    'Time': [current_time],
    'Average_IO': [current_average_io],
    'Queue_Size': [current_queue_size],
    'IO_Time': [current_io_time],
    'Disk Health': [0],  # Placeholder value, not used in real-time prediction
    'Disk Average IO Label': [0],  # Placeholder value, not used in real-time prediction
    'Label Disk Queue Time': [0]  # Placeholder value, not used in real-time prediction
})

# Add additional features to the new data
new_data['Average_IO_Squared'] = new_data['Average_IO'] ** 2
new_data['Queue_Size_Log'] = np.log1p(new_data['Queue_Size'])
new_data['IO_Time_Divided_By_Average_IO'] = new_data['IO_Time'] / new_data['Average_IO']
new_data['Queue_Size_Squared_Root'] = np.sqrt(new_data['Queue_Size'])
new_data['IO_Average_Ratio_Log'] = np.log1p(new_data['IO_Time'] / new_data['Average_IO'])
new_data['IO_Average_Product'] = new_data['IO_Time'] * new_data['Average_IO']
new_data['Queue_Size_Cubed'] = new_data['Queue_Size'] ** 3
new_data['Average_IO_Lag1'] = combined_df['Average_IO'].iloc[-1]  # Use the last available value for lagged features
new_data['Queue_Size_Lag1'] = combined_df['Queue_Size'].iloc[-1]  # Use the last available value for lagged features
new_data['IO_Time_Lag1'] = combined_df['IO_Time'].iloc[-1]  # Use the last available value for lagged features
new_data['Average_IO_RollingMean'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).mean().iloc[-1]  # Use the last available rolling mean
new_data['Queue_Size_RollingMean'] = combined_df['Queue_Size'].rolling(window=5, min_periods=1).mean().iloc[-1]  # Use the last available rolling mean
new_data['IO_Time_RollingMean'] = combined_df['IO_Time'].rolling(window=5, min_periods=1).mean().iloc[-1]  # Use the last available rolling mean
new_data['Average_IO_RollingStd'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).std().iloc[-1]  # Use the last available rolling std
new_data['Queue_Size_RollingStd'] = combined_df['Queue_Size'].rolling(window=5, min_periods=1).std().iloc[-1]  # Use the last available rolling std
new_data['IO_Time_RollingStd'] = combined_df['IO_Time'].rolling(window=5, min_periods=1).std().iloc[-1]  # Use the last available rolling std

# Use the composite function to calculate the score
composite_score = create_composite_function(new_data.drop(['Time'], axis=1).values)

# Calculate the dynamic threshold
threshold = calculate_threshold(composite_score)

# Visualize the composite function with the dynamic threshold
plot_composite_function(new_data['Time'], composite_score, threshold)





# Get the composite scores for the training data
train_composite_scores = model.predict(X)

# Determine the dynamic threshold for the training data
train_threshold = genextreme.ppf('0.95', c=0.1, loc=np.mean(train_composite_scores), scale=np.std(train_composite_scores))

# Plot the composite function with the dynamic threshold for the training data
plt.figure(figsize=(10, 6))
plt.plot(combined_df['Time'][1:], train_composite_scores, color='blue')
plt.axhline(train_threshold, color='red', linestyle='--', label='Threshold')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Composite Function Graph')
plt.legend()
plt.show()

