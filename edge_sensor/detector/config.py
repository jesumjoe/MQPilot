import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

EVE_JSON_PATH = os.path.join(LOG_DIR, 'eve.json')
SECURITY_EVENTS_PATH = os.path.join(LOG_DIR, 'security_events.json')
BASELINE_DATA_PATH = os.path.join(DATA_DIR, 'baseline', 'baseline_features.csv')
MODEL_PATH = os.path.join(MODEL_DIR, 'isolation_forest.joblib')

# ML Configuration
ML_WINDOW_SIZE = int(os.environ.get('ML_WINDOW_SIZE', 10))
ML_CONTAMINATION = float(os.environ.get('ML_CONTAMINATION', 0.05))
ANOMALY_THRESHOLD = float(os.environ.get('ANOMALY_THRESHOLD', 0.0))

# Networking
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
