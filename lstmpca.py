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
from sklearn.feature_selection import SelectFromModel

# Step 1: Load the dataset
df = pd.read_csv('disk_metrics.csv')

# Step 2: Preprocess the dataset
df['Disk Health'] = np.where(df['IO_Time'] > 30, 1, 0)
df['Disk Average IO Label'] = np.where(df['Average_IO'] > 10, 1, 0)
df['Label Disk Queue Time'] = np.where(df['Queue_Size'] > 10, 1, 0)

# Step 3: Combine the metrics
combined_df = df[['Time', 'Average_IO', 'Queue_Size', 'IO_Time', 'Disk Health', 'Disk Average IO Label', 'Label Disk Queue Time']]

# Step 4: Feature engineering
combined_df['Average IO Time Rolling Mean'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).mean()
combined_df['Queue Size Lag 1'] = combined_df['Queue_Size'].shift(1)
combined_df['DayOfWeek'] = pd.to_datetime(combined_df['Time']).dt.dayofweek
combined_df['HourOfDay'] = pd.to_datetime(combined_df['Time']).dt.hour

# Additional feature engineering
combined_df['IO_Average_Ratio'] = combined_df['IO_Time'] / combined_df['Average_IO']
combined_df['IO_Queue_Ratio'] = combined_df['IO_Time'] / combined_df['Queue_Size']
combined_df['Average_IO_Queue_Ratio'] = combined_df['Average_IO'] / combined_df['Queue_Size']
combined_df['IO_Average_Difference'] = combined_df['IO_Time'] - combined_df['Average_IO']
combined_df['Average_IO_Queue_Difference'] = combined_df['Average_IO'] - combined_df['Queue_Size']

# Lag features
combined_df['Average_IO_Lag_1'] = combined_df['Average_IO'].shift(1)
combined_df['Queue_Size_Lag_1'] = combined_df['Queue_Size'].shift(1)
combined_df['IO_Time_Lag_1'] = combined_df['IO_Time'].shift(1)

# Rolling statistics
combined_df['Average_IO_Rolling_Mean'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).mean()
combined_df['Average_IO_Rolling_Std'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).std()
combined_df['Queue_Size_Rolling_Mean'] = combined_df['Queue_Size'].rolling(window=5, min_periods=1).mean()
combined_df['Queue_Size_Rolling_Std'] = combined_df['Queue_Size'].rolling(window=5, min_periods=1).std()
combined_df['IO_Time_Rolling_Mean'] = combined_df['IO_Time'].rolling(window=5, min_periods=1).mean()
combined_df['IO_Time_Rolling_Std'] = combined_df['IO_Time'].rolling(window=5, min_periods=1).std()

# Step 5: Additional feature engineering
combined_df['Average IO Lag 1'] = combined_df['Average_IO'].shift(1)
combined_df['Average IO Lag 2'] = combined_df['Average_IO'].shift(2)
combined_df['Queue Size Lag 2'] = combined_df['Queue_Size'].shift(2)
combined_df['IO Time Lag 1'] = combined_df['IO_Time'].shift(1)
combined_df['IO Time Lag 2'] = combined_df['IO_Time'].shift(2)
combined_df['Average IO Rolling Std'] = combined_df['Average_IO'].rolling(window=5, min_periods=1).std()

# Step 6: Select relevant features and target variable
selected_features = ['Average_IO', 'Queue_Size', 'IO_Time', 'Average IO Time Rolling Mean', 'Queue Size Lag 1', 'DayOfWeek', 'HourOfDay',
                     'IO_Average_Ratio', 'IO_Queue_Ratio', 'Average_IO_Queue_Ratio', 'IO_Average_Difference', 'Average_IO_Queue_Difference',
                     'Average_IO_Lag_1', 'Queue_Size_Lag_1', 'IO_Time_Lag_1', 'Average_IO_Rolling_Mean', 'Average_IO_Rolling_Std',
                     'Queue_Size_Rolling_Mean', 'Queue_Size_Rolling_Std', 'IO_Time_Rolling_Mean', 'IO_Time_Rolling_Std',
                     'Average IO Lag 1', 'Average IO Lag 2', 'Queue Size Lag 2', 'IO Time Lag 1', 'IO Time Lag 2', 'Average IO Rolling Std']

X = combined_df[selected_features]
y = combined_df[['Disk Health', 'Disk Average IO Label', 'Label Disk Queue Time']]

# Step 7: Scale the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 8: Train the XGBoost model
param_grid_xgb = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 4, 5],
    'learning_rate': [0.1, 0.01, 0.001]
}

grid_search_xgb = GridSearchCV(estimator=xgb.XGBClassifier(), param_grid=param_grid_xgb, cv=3)
grid_search_xgb.fit(X_scaled, y)

# Get the best parameters and best score
best_params_xgb = grid_search_xgb.best_params_
best_score_xgb = grid_search_xgb.best_score_

# Step 9: Train the XGBoost model with the best parameters
best_model_xgb = xgb.XGBClassifier(**best_params_xgb)
best_model_xgb.fit(X_scaled, y)

# Step 10: Calculate feature importances for XGBoost
feature_importances_xgb = best_model_xgb.feature_importances_

# Step 11: Select features with high importance for XGBoost (optional)
selector_xgb = SelectFromModel(best_model_xgb, threshold=0.05, prefit=True)
X_selected_xgb = selector_xgb.transform(X_scaled)
selected_features_xgb = X.columns[selector_xgb.get_support()].tolist()

# Step 12: Train the LSTM model
X_lstm = X_scaled.reshape(-1, 1, X_scaled.shape[1])
y_lstm = y

lstm_model = Sequential()
lstm_model.add(LSTM(64, input_shape=(1, X_scaled.shape[1])))
lstm_model.add(Dense(3))  # Adjust the output dimension to match the number of labels
lstm_model.compile(loss='mse', optimizer='adam')
lstm_model.fit(X_lstm, y_lstm, epochs=100, batch_size=32, verbose=0)

# Step 13: Calculate feature importances for LSTM
lstm_feature_importances = lstm_model.layers[0].get_weights()[0]
lstm_feature_importances = np.sum(lstm_feature_importances, axis=1)

# Step 14: Select features with high importance for LSTM (optional)
selector_lstm = SelectFromModel(lstm_model, threshold=0.05)
X_selected_lstm = selector_lstm.transform(X_scaled)
selected_features_lstm = X.columns[selector_lstm.get_support()].tolist()

# Step 15: Apply PCA for dimensionality reduction
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Step 16: Visualize the feature importances
plt.figure(figsize=(12, 6))
plt.bar(selected_features_xgb, feature_importances_xgb)
plt.xlabel('Features')
plt.ylabel('Importance')
plt.title('XGBoost Feature Importances')
plt.xticks(rotation=90)
plt.show()

plt.figure(figsize=(12, 6))
plt.bar(X.columns, lstm_feature_importances)
plt.xlabel('Features')
plt.ylabel('Importance')
plt.title('LSTM Feature Importances')
plt.xticks(rotation=90)
plt.show()


















combined_df['IO_Average_Ratio'] = np.where(combined_df['Average_IO'] != 0, combined_df['IO_Time'] / combined_df['Average_IO'], 0)
combined_df['IO_Queue_Ratio'] = np.where(combined_df['Queue_Size'] != 0, combined_df['IO_Time'] / combined_df['Queue_Size'], 0)
combined_df['Average_IO_Queue_Ratio'] = np.where(combined_df['Queue_Size'] != 0, combined_df['Average_IO'] / combined_df['Queue_Size'], 0)


combined_df.replace([np.inf, -np.inf], np.nan, inplace=True)
combined_df.dropna(inplace=True)
