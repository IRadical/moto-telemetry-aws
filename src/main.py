import time
import random
from brain import MotoTelemetry
from connector import AWSConnector # Importamos nuestro nuevo puente

def run_telemetry_sim():
    # Initialize systems
    bike_id = "RAD_BIKE_V1"
    bike_brain = MotoTelemetry(bike_id)
    aws_link = AWSConnector()
    
    print("--- STARTING TELEMETRY SYSTEM ---")
    
    try:
        # Connect to AWS IoT Core
        aws_link.connect()
        print("\n--- BEGINNING DATA TRANSMISSION (Press Ctrl+C to stop) ---\n")

        while True:
            # 1. Simulate dynamic cornering sensor data
            speed = 90 + random.uniform(-5, 5) 
            ax = 0.1 
            ay = random.uniform(2.0, 6.0) 
            az = 8.5 
            
            # 2. Process physical data
            packet = bike_brain.generate_packet(speed, ax, ay, az)
            
            # 3. Display locally
            t = packet["telemetry"]
            print(f"[{packet['timestamp']}] | S: {t['speed_kmh']:.1f} km/h | "
                  f"Lean: {t['lean_angle']:>5}° | G: {t['g_force']:.2f}G")
            
            # 4. SEND TO CLOUD
            aws_link.publish_telemetry(packet)
            
            # Publish every 2 seconds for this test (real telemetry would be ~10Hz)
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print("\n--- USER INTERRUPTED SIMULATION ---")
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
    finally:
        # Always disconnect cleanly
        aws_link.disconnect()

if __name__ == "__main__":
    run_telemetry_sim()