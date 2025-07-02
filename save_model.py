import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Example dummy data
X = pd.DataFrame([10, 20, 30, 40, 50], columns=["Substance_Emission"])
y = [15, 30, 45, 60, 75]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "model.pkl")
