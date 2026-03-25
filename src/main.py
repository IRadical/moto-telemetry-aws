import time
import random
from src.brain import MotoTelemetry

def run_telemetry_sim():
    bike = MotoTelemetry("RAD_BIKE_V1")

    print("--- STARTING TELEMETRY SYSTEM (SIMULATION) ---")
    print("Press Ctrl+c to stop\n")

    try:
        while True:
            speed = 90 + random.uniform(-5, 5)
            ax = 0.1
            ay = random.uniform(2.0, 6.0)
            az = 8.5

            packet = bike.generate_packet(speed, ax, ay, az)

            t = packet["telemetry"]
            print(f"[{packet['timestamp']}] | S: {t['speed_kmh']:.1f} km/h | "
                  f"Lean Angle: {t['lean_angle']:>5}° | G-Force: {t['g_force']:.2f}G")
            
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n--- SIMULATION STOPPED BY USER ---")


if __name__ == "__main__":
    run_telemetry_sim()