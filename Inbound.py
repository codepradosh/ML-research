# Decompose metrics into seasonality, trend, and residual using STL
stl = STL(df['metrics'], seasonal=13)  # You can adjust the seasonal period as needed
result = stl.fit()
df['seasonality'] = result.seasonal
df['trend'] = result.trend
df['residual'] = result.resid

# Calculate simple moving averages (SMA) for each component
window_size = 3  # Adjust the window size as needed
components = ['metrics', 'seasonality', 'trend', 'residual']
for component in components:
    df[f'{component}_sma'] = df[component].rolling(window=window_size, min_periods=1).mean()

# Calculate exponential moving averages (EMA) for each component
alpha = 0.2  # Adjust the smoothing factor as needed
for component in components:
    df[f'{component}_ema'] = df[component].ewm(alpha=alpha, adjust=False).mean()

# Normalize the features
scaler = MinMaxScaler()
feature_columns = ['metrics', 'seasonality', 'trend', 'residual', 'metrics_sma', 'seasonality_sma', 'trend_sma', 'residual_sma', 'metrics_ema', 'seasonality_ema', 'trend_ema', 'residual_ema']
df[feature_columns] = scaler.fit_transform(df[feature_columns])
