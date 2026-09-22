from dataclasses import dataclass, asdict
from typing import Optional

# Feature Schema
FEATURE_ORDER = [
    'packet_count',
    'byte_count',
    'packets_per_second',
    'bytes_per_second',
    'publish_count',
    'subscribe_count',
    'connect_count',
    'disconnect_count',
    'unique_topics',
    'average_payload_size',
    'maximum_payload_size',
    'mean_inter_arrival_time',
    'std_inter_arrival_time',
    'connection_rate'
]

@dataclass
class SecurityEvent:
    timestamp: str
    event_id: str
    source_ip: str
    destination_ip: str
    destination_port: int
    classification: str
    action: str
    
    signature: Optional[dict] = None
    behavioral: Optional[dict] = None

    def to_dict(self):
        return asdict(self)
