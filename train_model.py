import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

# === Generate sample training data === #
data = pd.DataFrame({
    'facility_size': np.random.randint(500, 5000, size=100),
    'energy_consumption': np.random.uniform(1000, 10000, size=100),
    'waste_production': np.random.uniform(50, 500, size=100),
    'water_consumption': np.random.uniform(1000, 10000, size=100),
    'CO2_Emissions': np.random.uniform(100, 10000, size=100)
})

# === Split features and target === #
X = data[['energy_consumption', 'waste_production', 'water_consumption', 'facility_size']]
y = data['CO2_Emissions']

# === Train/Test Split === #
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Scaling === #
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# === Model === #
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# === Save model, scaler, and feature names === #
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/emission_model.pkl")
joblib.dump(scaler, "model/scaler.pkl")
joblib.dump(X.columns.tolist(), "model/feature_names.pkl")

print("✅ Model, Scaler, and Feature Names saved successfully!")
