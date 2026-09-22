import unittest
from edge_sensor.detector.feature_extractor import FeatureExtractor

class TestFeatures(unittest.TestCase):
    def test_feature_extraction(self):
        extractor = FeatureExtractor(window_size=10.0)
        
        event1 = {
            "timestamp": "2026-09-21T18:00:00.000000+0000",
            "event_type": "mqtt",
            "src_ip": "10.0.0.1",
            "mqtt": {
                "publish": {"topic": "sensor/temp", "payload_len": 50}
            }
        }
        
        event2 = {
            "timestamp": "2026-09-21T18:00:05.000000+0000",
            "event_type": "mqtt",
            "src_ip": "10.0.0.1",
            "mqtt": {
                "publish": {"topic": "sensor/temp", "payload_len": 150}
            }
        }

        # Force window completion
        event3 = {
            "timestamp": "2026-09-21T18:00:11.000000+0000",
            "event_type": "flow"
        }
        
        extractor.process_event(event1)
        extractor.process_event(event2)
        
        self.assertFalse(extractor.is_window_ready())
        extractor.process_event(event3)
        self.assertTrue(extractor.is_window_ready())
        
        vector, features = extractor.get_features()
        
        self.assertEqual(features['packet_count'], 2) # Only 2 packets added so far before window trigger. 
        # Wait, event3 adds flow stats... let's just check the ones explicitly added
        self.assertEqual(features['publish_count'], 2)
        self.assertEqual(features['unique_topics'], 1)
        self.assertEqual(features['average_payload_size'], 100.0)
        self.assertEqual(features['maximum_payload_size'], 150.0)

    def test_malformed_event(self):
        extractor = FeatureExtractor(window_size=10.0)
        event = {"event_type": "mqtt", "mqtt": "invalid_string"}
        # Should handle without crashing
        try:
            extractor.process_event(event)
            success = True
        except Exception:
            success = False
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
