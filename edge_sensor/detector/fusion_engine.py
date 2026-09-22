import json
import time
from .schemas import SecurityEvent
from .config import SECURITY_EVENTS_PATH

class FusionEngine:
    def __init__(self):
        self.suricata_alerts = []
        
    def add_suricata_alert(self, alert_event):
        self.suricata_alerts.append(alert_event)
        
    def evaluate(self, ml_result):
        has_suricata = len(self.suricata_alerts) > 0
        has_ml = ml_result.get('is_anomaly', False)
        
        classification = "NORMAL"
        action = "NONE"
        
        if has_suricata and has_ml:
            classification = "CORRELATED_THREAT"
            action = "ALERT" # High confidence, might drop if configured
        elif has_suricata:
            classification = "SIGNATURE_THREAT"
            action = "DROP" if any(a.get('alert', {}).get('action') == 'dropped' for a in self.suricata_alerts) else "ALERT"
        elif has_ml:
            classification = "BEHAVIORAL_ANOMALY"
            action = "ALERT"
            
        # Compile signature dict
        sig_dict = None
        if has_suricata:
            # just take the first alert for simplicity in this event
            alert = self.suricata_alerts[0].get('alert', {})
            sig_dict = {
                "detected": True,
                "signature_id": alert.get('signature_id'),
                "signature": alert.get('signature'),
                "severity": alert.get('severity')
            }
            
        beh_dict = None
        if has_ml:
            beh_dict = {
                "detected": ml_result['is_anomaly'],
                "anomaly_score": ml_result['anomaly_score'],
                "feature_snapshot": ml_result['feature_snapshot']
            }
            
        event = SecurityEvent(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            event_id=f"evt_{int(time.time())}",
            source_ip=self.suricata_alerts[0]['src_ip'] if has_suricata else "multiple",
            destination_ip=self.suricata_alerts[0]['dest_ip'] if has_suricata else "broker",
            destination_port=1883,
            classification=classification,
            action=action,
            signature=sig_dict,
            behavioral=beh_dict
        )
        
        self._log_event(event)
        
        # Reset alerts for next window
        self.suricata_alerts = []
        return event

    def _log_event(self, event: SecurityEvent):
        with open(SECURITY_EVENTS_PATH, 'a') as f:
            f.write(json.dumps(event.to_dict()) + '\n')
