import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from scipy.stats import genextreme
from sklearn.decomposition import PCA
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

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

# Step 5: Additional feature engineering
combined_df['Average IO Lag 1'] = combined_df['Average_IO'].shift(1)
combined_df['Average IO Lag 2'] = combined_df['Average_IO'].shift(2)
combined_df['Queue Size Lag 2'] = combined_df['Queue_Size'].shift(2)
combined_df['Average IO Rolling Std'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).std()
combined_df['Queue Size Rolling Std'] = combined_df['Queue_Size'].rolling(window=5, min_periods=1).std()

# Step 6: Feature scaling
scaler = StandardScaler()
scaled_data = scaler.fit_transform(combined_df[['Average_IO', 'Queue_Size', 'Average IO Time Rolling Mean', 'Queue Size Lag 1', 'DayOfWeek', 'HourOfDay', 'Average IO Lag 1', 'Average IO Lag 2', 'Queue Size Lag 2', 'Average IO Rolling Std', 'Queue Size Rolling Std']])

# Step 7: Train XGBoost model with hyperparameter tuning
X = scaled_data
y = combined_df['Disk Average IO Label']

# Define the parameter grid for grid search
param_grid = {
    'max_depth': [3, 5, 7],
    'learning_rate': [0.1, 0.01, 0.001],
    'n_estimators': [100, 200, 300]
}

# Create the XGBoost classifier
model = xgb.XGBClassifier()

# Perform grid search with cross-validation
grid_search = GridSearchCV(model, param_grid, cv=5)
grid_search.fit(X, y)

# Get the best parameters and best score
best_params = grid_search.best_params_
best_score = grid_search.best_score_

# Step 8: Train the model with the best parameters
best_model = xgb.XGBClassifier(**best_params)
best_model.fit(X, y)

# Step 9: Calculate feature importances
feature_importances = best_model.feature_importances_

# Step 10: Select features with high importance (optional)
selector = SelectFromModel(best_model, threshold=0.05, prefit=True)
X_selected = selector.transform(X)
selected_features = combined_df.columns[selector.get_support()].tolist()

# Step 11: Use LSTM for feature importance
lstm_data = scaled_data.reshape(-1, 1, X.shape[1])

lstm_model = Sequential()
lstm_model.add(LSTM(64, input_shape=(1, X.shape[1])))
lstm_model.add(Dense(1))
lstm_model.compile(loss='mse', optimizer='adam')
lstm_model.fit(lstm_data, y, epochs=100, batch_size=32, verbose=0)

lstm_feature_importances = lstm_model.layers[0].get_weights()[0]
lstm_feature_importances = np.mean(np.abs(lstm_feature_importances), axis=0)

# Step 12: Use PCA for dimensionality reduction
pca = PCA(n_components=10)
X_pca = pca.fit_transform(X)

# Step 13: Calculate composite score
composite_scores = np.dot(X_pca, feature_importances[:10]) + np.dot(lstm_data.reshape(lstm_data.shape[0], -1), lstm_feature_importances)

# Step 14: Determine dynamic threshold using extreme value distribution theorem
threshold = genextreme.ppf(0.95, loc=np.mean(composite_scores), scale=np.std(composite_scores))

# Step 15: Determine disk health and busyness levels
disk_health = np.where(composite_scores <= threshold, 'Healthy', 'Unhealthy')
busyness_levels = np.where(composite_scores <= threshold, 'Low', 'High')

# Step 16: Plot the composite function graph
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

# Print the best parameters and best score
print("Best Parameters:", best_params)
print("Best Score:", best_score)
