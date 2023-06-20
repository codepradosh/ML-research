import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.stats import genextreme

# Step 1: Load the dataset
df = pd.read_csv('disk_metrics.csv')

# Step 2: Preprocess the dataset
df['Disk Average IO Label'] = np.where(df['Average_IO'] > 10, 1, 0)
df['Label Disk Queue Time'] = np.where(df['Queue_Size'] > 10, 1, 0)

# Step 3: Combine the metrics
combined_df = df[['Time', 'Average_IO', 'Queue_Size', 'Disk Average IO Label', 'Label Disk Queue Time']]

# Step 4: Apply PCA
# Select the relevant columns for PCA
pca_columns = ['Average_IO', 'Queue_Size']

# Remove any rows with missing values
combined_df = combined_df.dropna(subset=pca_columns)

# Standardize the data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(combined_df[pca_columns])

# Apply PCA
pca = PCA(n_components=2)  # Set the number of components as per your requirement
principal_components = pca.fit_transform(scaled_data)

# Step 5: Calculate feature importances and normalize them
feature_importances = np.abs(pca.components_[0]) + np.abs(pca.components_[1])
weights = feature_importances / sum(feature_importances)

# Step 6: Calculate composite score
composite_scores = np.dot(scaled_data, weights)

# Step 7: Determine dynamic threshold using extreme value distribution theorem
threshold = genextreme.ppf(0.95, loc=np.mean(composite_scores), scale=np.std(composite_scores))

# Step 8: Determine disk health and busyness levels
disk_health = np.where(composite_scores <= threshold, 'Healthy', 'Unhealthy')
busyness_levels = np.where(composite_scores <= threshold, 'Low', 'High')

# Step 9: Plot the PCA visualization and composite function graph
plt.figure(figsize=(10, 6))
plt.scatter(principal_components[:, 0], principal_components[:, 1], c=disk_health)
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('PCA Components')
plt.colorbar(label='Disk Health')
plt.show()

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
