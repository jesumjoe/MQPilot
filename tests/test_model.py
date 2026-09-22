import unittest
import numpy as np
import os
import csv
from edge_sensor.detector.train_model import load_data, train
from edge_sensor.detector.schemas import FEATURE_ORDER
from edge_sensor.detector.config import BASELINE_DATA_PATH, MODEL_PATH

class TestModel(unittest.TestCase):
    def setUp(self):
        # Create a mock baseline file
        os.makedirs(os.path.dirname(BASELINE_DATA_PATH), exist_ok=True)
        with open(BASELINE_DATA_PATH, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FEATURE_ORDER)
            writer.writeheader()
            for _ in range(20):
                row = {k: np.random.uniform(1, 100) for k in FEATURE_ORDER}
                writer.writerow(row)

    def tearDown(self):
        if os.path.exists(BASELINE_DATA_PATH):
            os.remove(BASELINE_DATA_PATH)

    def test_missing_data_raises_error(self):
        os.remove(BASELINE_DATA_PATH)
        with self.assertRaises(FileNotFoundError):
            load_data(BASELINE_DATA_PATH)
            
    def test_model_training(self):
        # Should not raise exception
        train()
        self.assertTrue(os.path.exists(MODEL_PATH))
        
if __name__ == '__main__':
    unittest.main()
