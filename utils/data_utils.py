import os
import pandas as pd
from datetime import datetime

HISTORY_FILE = 'history.csv'

# Ensure the history file exists
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w') as f:
        f.write('timestamp,username,industry,emission_data,energy_consumption,waste_production,water_consumption,facility_size,prediction\n')

def save_prediction(username, data):
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{datetime.now().isoformat()},{username},{data['industry']},{data['emission_data']},"
                f"{data['energy_consumption']},{data['waste_production']},{data['water_consumption']},"
                f"{data['facility_size']},{data['prediction']}\n")

def get_user_history(username):
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame()

    history_df = pd.read_csv(HISTORY_FILE)
    return history_df[history_df['username'] == username]
