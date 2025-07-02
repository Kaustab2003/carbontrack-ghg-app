import joblib

model = joblib.load("model/emission_model.pkl")

try:
    print("Model expects these features:")
    print(model.feature_names_in_)
except AttributeError:
    print("❌ Model does NOT have feature names. Retrain it using a DataFrame with named columns.")
