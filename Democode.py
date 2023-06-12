import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from statsmodels.tsa.seasonal import STL
from scipy.stats import skew, kurtosis
from statsmodels.tsa.arima.model import ARIMA
from sklearn.ensemble import ExtraTreesRegressor

# Read the dataset
df = pd.read_csv("dummy_dataset.csv")

# Split the data into features and labels
X = df.iloc[:, :-1]  # Features: all columns except the last one
y = df.iloc[:, -1]   # Labels: last column

# Normalize the features using Min-Max scaling
scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X)

# Feature extraction
lags = [1, 2, 3]  # Example lag intervals
window_sizes = [3, 5, 7]  # Example window sizes for rolling statistics
span_values = [3, 5, 7]  # Example span values for exponential moving average

X_features = pd.DataFrame(X_normalized)

# Lag features
for col in X.columns:
    for lag in lags:
        X_features[f"{col}_lag_{lag}"] = X[col].shift(lag)

# Rolling statistics
for col in X.columns:
    for window_size in window_sizes:
        X_features[f"{col}_mean_{window_size}"] = X[col].rolling(window=window_size).mean()
        X_features[f"{col}_std_{window_size}"] = X[col].rolling(window=window_size).std()
        X_features[f"{col}_min_{window_size}"] = X[col].rolling(window=window_size).min()
        X_features[f"{col}_max_{window_size}"] = X[col].rolling(window=window_size).max()

# Exponential moving average
for col in X.columns:
    for span in span_values:
        X_features[f"{col}_ema_{span}"] = X[col].ewm(span=span).mean()

# Seasonal decomposition
for col in X.columns:
    decomposition = STL(X[col]).fit()
    X_features[f"{col}_trend"] = decomposition.trend
    X_features[f"{col}_seasonal"] = decomposition.seasonal
    X_features[f"{col}_residual"] = decomposition.resid

# Trend Features
for col in X.columns:
    model = ExtraTreesRegressor(n_estimators=100)
    model.fit(np.arange(len(X)).reshape(-1, 1), X[col])
    X_features[f"{col}_trend"] = model.predict(np.arange(len(X)).reshape(-1, 1))

# Frequency Domain Features
for col in X.columns:
    fft_vals = np.fft.fft(X[col])
    X_features[f"{col}_fft_mean"] = np.mean(fft_vals)
    X_features[f"{col}_fft_std"] = np.std(fft_vals)
    X_features[f"{col}_fft_skew"] = skew(fft_vals)
    X_features[f"{col}_fft_kurtosis"] = kurtosis(fft_vals)

# Statistical Moments
for col in X.columns:
    X_features[f"{col}_skewness"] = skew(X[col])
    X_features[f"{col}_kurtosis"] = kurtosis(X[col])

# Cross-Correlation
for col1 in X.columns:
    for col2 in X.columns:
        if col1 != col2:
            cross_corr = np.correlate(X[col1], X[col2])
            X_features[f"{col1}_{col2}_cross_corr"] = cross_corr

# Entropy Measures
for col in X.columns:
    X_features[f"{col}_entropy"] = -np.sum(X[col] * np.log2(X[col]))

# Time Series Forecasting Features
for col in X.columns:
    model = ARIMA(X[col], order=(3, 0, 1))
    model_fit = model.fit()
    _, _, resid = model_fit.forecast(len(X))
    X_features[f"{col}_forecast_residual"] = resid

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_features, y, test_size=0.2, random_state=42)

# Train a Random Forest classifier
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Get feature importance scores
importance_scores = model.feature_importances_

# Create a dictionary to map each feature to its importance score
feature_importance = dict(zip(X_features.columns, importance_scores))

# Normalize the importance scores and calculate weights
total_importance = sum(importance_scores)
weights = {feature: score / total_importance for feature, score in feature_importance.items()}

# Compute the composite score for each sample
composite_scores = np.dot(X_features.values, list(weights.values()))

# Define the threshold to classify as healthy or not
threshold = 0.5

# Classify as healthy (0) or not (1) based on the composite score
predictions = np.where(composite_scores >= threshold, 1, 0)

# Calculate the accuracy
accuracy = accuracy_score(y, predictions)
print("Accuracy:", accuracy)
