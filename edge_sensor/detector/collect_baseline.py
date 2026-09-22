import os
import json
import csv
from .config import EVE_JSON_PATH, BASELINE_DATA_PATH
from .schemas import FEATURE_ORDER
from .feature_extractor import FeatureExtractor

def collect():
    if not os.path.exists(EVE_JSON_PATH):
        print(f"Error: EVE JSON log not found at {EVE_JSON_PATH}.")
        print("Please ensure Suricata has run with baseline traffic.")
        return

    os.makedirs(os.path.dirname(BASELINE_DATA_PATH), exist_ok=True)
    
    extractor = FeatureExtractor(window_size=10.0)
    
    with open(EVE_JSON_PATH, 'r') as f_in, open(BASELINE_DATA_PATH, 'w', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=FEATURE_ORDER)
        writer.writeheader()
        
        for line in f_in:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
                
            # Filter out alert/drop events from baseline to ensure clean dataset
            if event.get('event_type') in ('alert', 'drop'):
                continue
                
            extractor.process_event(event)
            
            if extractor.is_window_ready():
                vector, features = extractor.get_features()
                writer.writerow(features)
                extractor.reset_window()

    print(f"Baseline feature extraction complete. Output saved to {BASELINE_DATA_PATH}")

if __name__ == '__main__':
    collect()
