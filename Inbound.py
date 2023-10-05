df['timestamp'] = pd.to_datetime(df['timestamp'])
df['timestamp'] = (df['timestamp'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

# Normalize the features (use the same scaler used during training)
scaler = MinMaxScaler()
feature_columns = ['timestamp', 'metrics', 'seasonality', 'trend', 'residual', 'metrics_sma', 'seasonality_sma', 'trend_sma', 'residual_sma', 'metrics_ema', 'seasonality_ema', 'trend_ema', 'residual_ema']
df[feature_columns] = scaler.fit_transform(df[feature_columns])

# Prepare the data for prediction
sequence_length = 10  # Adjust the sequence length as needed
num_features = len(feature_columns)
X = []

for i in range(len(df) - sequence_length):
    X.append(df[feature_columns].values[i:i + sequence_length])

X = np.array(X)

# Split the data into training and validation sets
split_ratio = 0.8
split_index = int(split_ratio * len(X))

X_train, X_val = X[:split_index], X[split_index:]
y_train, y_val = y[:split_index], y[split_index:]

# Define hyperparameters for model tuning
lstm_units = 128  # Number of LSTM units in the hidden layer
learning_rate = 0.001
batch_size = 32
epochs = 50

# Build the LSTM model
model = Sequential([
    LSTM(units=lstm_units, input_shape=(sequence_length, num_features), activation='relu'),
    Dense(1)
])

# Compile the model with the chosen optimizer, learning rate, and loss function
optimizer = Adam(learning_rate=learning_rate)
model.compile(optimizer=optimizer, loss='mse')

# Define early stopping callback
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train the model
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=epochs,
    batch_size=batch_size,
    callbacks=[early_stopping]
)

# Use the trained model to predict residuals
predicted_residuals = model.predict(X_val)

# Calculate Z-scores for the residuals using statistics from the training data
mean_residual = np.mean(y_train)  # Use the mean and std from training data
std_residual = np.std(y_train)
z_scores = (predicted_residuals - mean_residual) / std_residual

# Set a 3-sigma threshold for anomaly detection
threshold = 3

# Detect anomalies based on Z-scores and threshold
anomalies = np.abs(z_scores) > threshold

# Print timestamps where anomalies are detected
anomaly_timestamps = df.iloc[split_index + sequence_length:][anomalies]['timestamp']
print("Anomaly Timestamps:")
print(anomaly_timestamps)

# Plot training and validation loss
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()
