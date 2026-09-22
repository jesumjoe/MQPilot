import joblib
import os
import time
from .config import MODEL_PATH, ANOMALY_THRESHOLD

class MLDetector:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please train the model first.")
        self.model = joblib.load(MODEL_PATH)
        self.threshold = ANOMALY_THRESHOLD

    def detect(self, feature_vector, features_dict):
        """
        Returns anomaly score and boolean is_anomaly
        """
        # pipeline's decision_function returns lower for anomalies (negative = anomaly)
        score = self.model.decision_function([feature_vector])[0]
        
        # is_anomaly based on threshold
        is_anomaly = score < self.threshold
        
        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "feature_snapshot": features_dict,
            "anomaly_score": float(score),
            "is_anomaly": bool(is_anomaly)
        }
