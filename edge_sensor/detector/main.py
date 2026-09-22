import os
import json
import time
from .config import EVE_JSON_PATH
from .feature_extractor import FeatureExtractor
from .ml_detector import MLDetector
from .fusion_engine import FusionEngine

def follow(thefile):
    """Generator function that yields new lines in a file."""
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def run_pipeline():
    print("Starting MQPilot ML Detector Pipeline...")
    
    # Wait for EVE JSON to exist
    while not os.path.exists(EVE_JSON_PATH):
        print(f"Waiting for {EVE_JSON_PATH}...")
        time.sleep(2)
        
    extractor = FeatureExtractor(window_size=10)
    try:
        detector = MLDetector()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run `python -m detector.train_model` first.")
        return

    fusion = FusionEngine()

    with open(EVE_JSON_PATH, 'r') as logfile:
        for line in follow(logfile):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
                
            extractor.process_event(event)
            
            if event.get('event_type') == 'alert':
                fusion.add_suricata_alert(event)
                
            if extractor.is_window_ready():
                vector, features = extractor.get_features()
                ml_result = detector.detect(vector, features)
                
                sec_event = fusion.evaluate(ml_result)
                print(f"[{sec_event.timestamp}] {sec_event.classification} - Action: {sec_event.action}")
                
                extractor.reset_window()

if __name__ == '__main__':
    run_pipeline()
