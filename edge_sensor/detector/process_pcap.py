import os
import subprocess
import time

PCAP_DIR = "/pcaps"
LOG_DIR = "/edge_sensor/logs"
SURICATA_YAML = "/edge_sensor/suricata.yaml"

def process_pcap(pcap_filename):
    pcap_path = os.path.join(PCAP_DIR, pcap_filename)
    if not os.path.exists(pcap_path):
        print(f"Error: {pcap_path} not found.")
        return False
        
    print(f"\n--- Processing {pcap_filename} ---")
    
    # 1. Clear old EVE log
    eve_log = os.path.join(LOG_DIR, "eve.json")
    if os.path.exists(eve_log):
        os.remove(eve_log)
        
    # 2. Run Suricata in offline mode (-r)
    print("Running Suricata DPI (Offline Mode)...")
    cmd = [
        "suricata",
        "-c", SURICATA_YAML,
        "-r", pcap_path,
        "-l", LOG_DIR,
        "-k", "none"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Suricata finished processing {pcap_filename}.")
        if os.path.exists(eve_log):
            size = os.path.getsize(eve_log)
            print(f"Generated EVE JSON log: {size / 1024 / 1024:.2f} MB")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Suricata failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "capture_1w_short.pcap"
    process_pcap(target)
