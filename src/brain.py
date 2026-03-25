import math
from datetime import datetime

class MotoTelemetry:
    def __init__(self, device_id):
        self.device_id = device_id

    def calculate_metrics(self, ax, ay, az):
        g_force = math.sqrt(ax**2 + ay**2 + az**2) / 9.81
        lean_angle = math.degrees(math.atan2(ay, az))

        return round(g_force, 2), round(lean_angle, 2)
    
    def generate_packet(self, speed, ax, ay, az):
        g, lean = self.calculate_metrics(ax, ay, az)
        return{
            "device_id": self.device_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "telemetry": {
                "speed_kmh": speed,
                "lean_angle": lean,
                "g_force": g,
                "imu_raw": {"x": ax, "y": ay, "z": az}
            }
        }
        