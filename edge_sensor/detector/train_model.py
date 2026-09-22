import os
import csv
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from .config import BASELINE_DATA_PATH, MODEL_PATH, ML_CONTAMINATION
from .schemas import FEATURE_ORDER

def load_data(filepath):
    data = []
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Baseline data not found at {filepath}. Please run baseline collection first.")

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            vector = [float(row[k]) for k in FEATURE_ORDER]
            data.append(vector)
            
    if not data:
        raise ValueError(f"Baseline data at {filepath} is empty.")
        
    return np.array(data)

def train():
    print(f"Loading data from {BASELINE_DATA_PATH}...")
    X = load_data(BASELINE_DATA_PATH)
    
    print(f"Training Isolation Forest with contamination {ML_CONTAMINATION}...")
    # Add scaler to standardize features before isolation forest
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('iforest', IsolationForest(
            n_estimators=100,
            contamination=ML_CONTAMINATION,
            random_state=42
        ))
    ])
    
    pipeline.fit(X)
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == '__main__':
    train()
