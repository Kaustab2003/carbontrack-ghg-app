import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Dummy training data (simulate expected features from the web form)
data = {
    'Energy': np.random.randint(1000, 10000, 100),
    'Waste': np.random.randint(10, 100, 100),
    'Water': np.random.randint(100, 1000, 100),
    'Area': np.random.randint(500, 5000, 100),
    'CO2': np.random.uniform(50, 1000, 100)  # Target variable
}

df = pd.DataFrame(data)

# Feature-target split
X = df[['Energy', 'Waste', 'Water', 'Area']]
y = df['CO2']

# Save feature names
feature_names = X.columns.tolist()

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = RandomForestRegressor()
model.fit(X_train_scaled, y_train)

# Save model, scaler, and feature names
os.makedirs('model', exist_ok=True)
joblib.dump(model, 'model/emission_model.pkl')
joblib.dump(scaler, 'model/scaler.pkl')
joblib.dump(feature_names, 'model/feature_names.pkl')

print("✅ Model trained and saved with expected features:", feature_names)
