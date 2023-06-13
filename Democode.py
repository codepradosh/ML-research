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


X = df.iloc[:, :-1]  
y = df.iloc[:, -1]   


scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X)


lags = [1, 2, 3]  
window_sizes = [3, 5, 7]  
span_values = [3, 5, 7]  
X_features = pd.DataFrame(X_normalized)


for col in X.columns:
    for lag in lags:
        X_features[f"{col}_lag_{lag}"] = X[col].shift(lag)


for col in X.columns:
    for window_size in window_sizes:
        X_features[f"{col}_mean_{window_size}"] = X[col].rolling(window=window_size).mean()
        X_features[f"{col}_std_{window_size}"] = X[col].rolling(window=window_size).std()
        X_features[f"{col}_min_{window_size}"] = X[col].rolling(window=window_size).min()
        X_features[f"{col}_max_{window_size}"] = X[col].rolling(window=window_size).max()


for col in X.columns:
    for span in span_values:
        X_features[f"{col}_ema_{span}"] = X[col].ewm(span=span).mean()


for col in X.columns:
    decomposition = STL(X[col]).fit()
    X_features[f"{col}_trend"] = decomposition.trend
    X_features[f"{col}_seasonal"] = decomposition.seasonal
    X_features[f"{col}_residual"] = decomposition.resid


for col in X.columns:
    model = ExtraTreesRegressor(n_estimators=100)
    model.fit(np.arange(len(X)).reshape(-1, 1), X[col])
    X_features[f"{col}_trend"] = model.predict(np.arange(len(X)).reshape(-1, 1))


for col in X.columns:
    fft_vals = np.fft.fft(X[col])
    X_features[f"{col}_fft_mean"] = np.mean(fft_vals)
    X_features[f"{col}_fft_std"] = np.std(fft_vals)
    X_features[f"{col}_fft_skew"] = skew(fft_vals)
    X_features[f"{col}_fft_kurtosis"] = kurtosis(fft_vals)


for col in X.columns:
    X_features[f"{col}_skewness"] = skew(X[col])
    X_features[f"{col}_kurtosis"] = kurtosis(X[col])


for col1 in X.columns:
    for col2 in X.columns:
        if col1 != col2:
            cross_corr = np.correlate(X[col1], X[col2])
            X_features[f"{col1}_{col2}_cross_corr"] = cross_corr


for col in X.columns:
    X_features[f"{col}_entropy"] = -np.sum(X[col] * np.log2(X[col]))


for col in X.columns:
    model = ARIMA(X[col], order=(3, 0, 1))
    model_fit = model.fit()
    _, _, resid = model_fit.forecast(len(X))
    X_features[f"{col}_forecast_residual"] = resid


X_train, X_test, y_train, y_test = train_test_split(X_features, y, test_size=0.2, random_state=42)


model = RandomForestClassifier()
model.fit(X_train, y_train)


importance_scores = model.feature_importances_


feature_importance = dict(zip(X_features.columns, importance_scores))


total_importance = sum(importance_scores)
weights = {feature: score / total_importance for feature, score in feature_importance.items()}


composite_scores = np.dot(X_features.values, list(weights.values()))


threshold = 0.5


predictions = np.where(composite_scores >= threshold, 1, 0)


accuracy = accuracy_score(y, predictions)
print("Accuracy:", accuracy)
