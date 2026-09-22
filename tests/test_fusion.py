import unittest
from edge_sensor.detector.fusion_engine import FusionEngine

class TestFusion(unittest.TestCase):
    def setUp(self):
        self.fusion = FusionEngine()
        
    def test_clean_clean(self):
        ml_res = {"is_anomaly": False, "anomaly_score": 0.5, "feature_snapshot": {}}
        event = self.fusion.evaluate(ml_res)
        self.assertEqual(event.classification, "NORMAL")
        self.assertEqual(event.action, "NONE")
        
    def test_alert_clean(self):
        self.fusion.add_suricata_alert({"src_ip": "1.1.1.1", "dest_ip": "2.2.2.2", "alert": {"signature": "test"}})
        ml_res = {"is_anomaly": False, "anomaly_score": 0.5, "feature_snapshot": {}}
        event = self.fusion.evaluate(ml_res)
        self.assertEqual(event.classification, "SIGNATURE_THREAT")
        self.assertEqual(event.action, "ALERT")
        
    def test_clean_anomaly(self):
        ml_res = {"is_anomaly": True, "anomaly_score": -0.5, "feature_snapshot": {}}
        event = self.fusion.evaluate(ml_res)
        self.assertEqual(event.classification, "BEHAVIORAL_ANOMALY")
        
    def test_correlated(self):
        self.fusion.add_suricata_alert({"src_ip": "1.1.1.1", "dest_ip": "2.2.2.2", "alert": {"signature": "test", "action": "dropped"}})
        ml_res = {"is_anomaly": True, "anomaly_score": -0.5, "feature_snapshot": {}}
        event = self.fusion.evaluate(ml_res)
        self.assertEqual(event.classification, "CORRELATED_THREAT")
        self.assertEqual(event.action, "ALERT")

if __name__ == '__main__':
    unittest.main()
