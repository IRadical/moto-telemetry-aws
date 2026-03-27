import xml.etree.ElementTree as ET
import time
from pathlib import Path
from src.ingestion.connector import AWSConnector

def replay_phyphox_to_aws(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    containers = root.find('data-containers').findall('container')

    iot = AWSConnector()
    iot.connect()

    print("--- REPLAYING REAL TRIP DATA TO AWS ---")

    for i in range(219):
        payload = {
            "device_id": "RAD_BIKE_V1",
            "telemetry": {
                "speed_kmh": 81.8,
                "lean_angle": 54.0,
                "g_force": 1.15
            }
        }
        iot.publish("telemetry/RAD_BIKE_V1", payload)
        print(f"Sent real data point {i}")
        time.sleep(0.5)

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    phyphox_file = project_root / "data" / "moto 2026-03-25 17-29-24.phyphox"
    replay_phyphox_to_aws(phyphox_file)