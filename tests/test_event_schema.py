import unittest
from edge_sensor.detector.schemas import SecurityEvent

class TestSchema(unittest.TestCase):
    def test_schema_validity(self):
        event = SecurityEvent(
            timestamp="2026-09-21T18:00:00Z",
            event_id="test_1",
            source_ip="1.1.1.1",
            destination_ip="2.2.2.2",
            destination_port=1883,
            classification="NORMAL",
            action="NONE"
        )
        d = event.to_dict()
        self.assertTrue('timestamp' in d)
        self.assertTrue('classification' in d)
        
if __name__ == '__main__':
    unittest.main()
