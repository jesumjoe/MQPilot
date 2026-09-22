import json
from collections import defaultdict
from .schemas import FEATURE_ORDER
from datetime import datetime
import numpy as np

class FeatureExtractor:
    def __init__(self, window_size=10.0):
        self.window_size = float(window_size)
        self.reset_window()

    def reset_window(self):
        self.packet_count = 0
        self.byte_count = 0
        self.publish_count = 0
        self.subscribe_count = 0
        self.connect_count = 0
        self.disconnect_count = 0
        self.topics = set()
        self.payload_sizes = []
        self.arrival_times = []
        
        self.start_time = None
        self.current_time = None

    def _parse_timestamp(self, ts_str):
        if not ts_str:
            return 0.0
        try:
            # Handle typical Suricata timestamp: 2026-09-21T18:00:00.000000+0000
            # Replace +0000 with +00:00 for python fromisoformat
            if '+' in ts_str and ':' not in ts_str.split('+')[-1]:
                parts = ts_str.rsplit('+', 1)
                ts_str = f"{parts[0]}+{parts[1][:2]}:{parts[1][2:]}"
            return datetime.fromisoformat(ts_str).timestamp()
        except Exception:
            return 0.0

    def process_event(self, event):
        """Process a single EVE JSON event"""
        ts_str = event.get('timestamp')
        event_time = self._parse_timestamp(ts_str)
        
        # Initialize window start on first event
        if self.start_time is None and event_time > 0:
            self.start_time = event_time
            
        if event_time > 0:
            self.current_time = event_time
            self.arrival_times.append(event_time)

        event_type = event.get('event_type')
        if event_type == 'flow':
            flow = event.get('flow', {})
            self.packet_count += flow.get('pkts_toclient', 0) + flow.get('pkts_toserver', 0)
            self.byte_count += flow.get('bytes_toclient', 0) + flow.get('bytes_toserver', 0)
        
        elif event_type == 'mqtt':
            self.packet_count += 1
            mqtt = event.get('mqtt', {})
            if not isinstance(mqtt, dict):
                mqtt = {}
            
            if mqtt.get('publish'):
                self.publish_count += 1
                pub = mqtt['publish']
                if 'topic' in pub:
                    self.topics.add(pub['topic'])
                # Some suricata versions might not give payload_len, fallback to 0
                payload_len = pub.get('payload_len', 0)
                self.payload_sizes.append(payload_len)
            elif mqtt.get('subscribe'):
                self.subscribe_count += 1
            elif mqtt.get('connect'):
                self.connect_count += 1
            elif mqtt.get('disconnect'):
                self.disconnect_count += 1
            
        elif event_type == 'alert':
            self.packet_count += 1
            
        elif event_type == 'stats':
            stats = event.get('stats', {})
            decoder = stats.get('decoder', {})
            app_layer = stats.get('app_layer', {}).get('tx', {})
            
            # Since stats are cumulative, we need to track the last seen values
            if not hasattr(self, 'last_stats'):
                self.last_stats = {
                    'pkts': decoder.get('pkts', 0),
                    'bytes': decoder.get('bytes', 0),
                    'mqtt_tx': app_layer.get('mqtt', 0)
                }
                return # Skip processing this event as it's just setting the baseline
                
            current_pkts = decoder.get('pkts', 0)
            current_bytes = decoder.get('bytes', 0)
            current_mqtt_tx = app_layer.get('mqtt', 0)
            
            pkts_diff = current_pkts - self.last_stats['pkts']
            bytes_diff = current_bytes - self.last_stats['bytes']
            mqtt_diff = current_mqtt_tx - self.last_stats['mqtt_tx']
            
            if pkts_diff > 0:
                self.packet_count += pkts_diff
                self.byte_count += bytes_diff
                # Approximate publishes from mqtt tx diff
                self.publish_count += mqtt_diff
                
            self.last_stats = {
                'pkts': current_pkts,
                'bytes': current_bytes,
                'mqtt_tx': current_mqtt_tx
            }

    def get_features(self):
        """Return the calculated features for the current window"""
        elapsed = 0.0
        if self.start_time and self.current_time:
            elapsed = self.current_time - self.start_time
        # avoid division by zero
        elapsed = elapsed if elapsed > 0 else 1.0

        avg_payload = float(np.mean(self.payload_sizes)) if self.payload_sizes else 0.0
        max_payload = float(np.max(self.payload_sizes)) if self.payload_sizes else 0.0
        
        # Inter-arrival times
        if len(self.arrival_times) > 1:
            diffs = np.diff(sorted(self.arrival_times))
            mean_iat = float(np.mean(diffs))
            std_iat = float(np.std(diffs))
        else:
            mean_iat = 0.0
            std_iat = 0.0

        features = {
            'packet_count': self.packet_count,
            'byte_count': self.byte_count,
            'packets_per_second': self.packet_count / elapsed,
            'bytes_per_second': self.byte_count / elapsed,
            'publish_count': self.publish_count,
            'subscribe_count': self.subscribe_count,
            'connect_count': self.connect_count,
            'disconnect_count': self.disconnect_count,
            'unique_topics': len(self.topics),
            'average_payload_size': avg_payload,
            'maximum_payload_size': max_payload,
            'mean_inter_arrival_time': mean_iat,
            'std_inter_arrival_time': std_iat,
            'connection_rate': self.connect_count / elapsed
        }
        
        # Format as array in order
        feature_vector = [features[k] for k in FEATURE_ORDER]
        return feature_vector, features

    def is_window_ready(self):
        if not self.start_time or not self.current_time:
            return False
        return (self.current_time - self.start_time) >= self.window_size
