import json
import random
import numpy as np
import pandas as pd
from pathlib import Path
from locust import HttpUser, between, task
from credit_risk.features import load_splits, AFTER_EDA
from credit_risk.monitoring.prediction_logger import RAW_INPUT_COLUMNS
from credit_risk.monitoring.log_loader import NULLABLE_NUMERIC_COLS

# loading the payload
cwd = Path(__file__).parent

# with open(cwd / 'test_payload.json', 'r') as f:
#     payload = json.load(f)

_, _, test_df, _ = load_splits(path=AFTER_EDA)

REQUIRED_COLS = [c for c in RAW_INPUT_COLUMNS if c not in NULLABLE_NUMERIC_COLS]
test_df = test_df.dropna(subset=REQUIRED_COLS)

def skew_row(row: pd.Series) -> pd.Series:
    row = row.copy()
    row['annual_inc'] = row['annual_inc'] * random.uniform(0.7, 0.85)
    row['dti'] = row['dti'] * random.uniform(1.2, 1.4)
    return row

def row_to_payload(row:pd.Series) -> dict:
    s_row = row[RAW_INPUT_COLUMNS].to_dict()
    s_row['earliest_cr_line'] = row['earliest_cr_line'].date().isoformat()
    
    for key, val in s_row.items():
        if pd.isna(val):
            s_row[key] = None
        elif isinstance(val, np.generic):
            s_row[key] = val.item()
            
    return s_row

class User(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def predict(self):
        row = test_df.sample(n=1).iloc[0]
        if random.random() < 0.3:
            row = skew_row(row)
        payload = row_to_payload(row)
        self.client.post('/predict', json=payload)