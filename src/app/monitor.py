import os
import time
import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv


load_dotenv()

def clear_screen():

    os.system('cls' if os.name == 'nt' else 'clear')

def get_status_color(lean_angle):

    if abs(lean_angle) < 25:
        return "SAFE (Green)"
    elif abs(lean_angle) < 40:
        return "CAUTION (Yellow)"
    else:
        return "DANGER (Red) - LEAN LIMIT REACHED!"

def start_monitor(bike_id):

    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-2',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    table = dynamodb.Table('MotoTelemetry_Dev')

    print(f"--- STARTING LIVE MONITOR FOR {bike_id} ---")
    
    try:
        while True:

            response = table.query(
                KeyConditionExpression=Key('device_id').eq(bike_id),
                ScanIndexForward=False, 
                Limit=1
            )
            
            items = response.get('Items', [])
            
            if items:
                item = items[0]
                t = item.get('telemetry', {})
                timestamp = item.get('timestamp')
                speed = round(float(t.get('speed_kmh', 0)), 1)
                lean = round(float(t.get('lean_angle', 0)), 2)
                g_force = round(float(t.get('g_force', 0)), 2)
                
                status = get_status_color(lean)

                clear_screen()
                print("==========================================")
                print(f"   MOTO TELEMETRY DASHBOARD - {bike_id}")
                print("==========================================")
                print(f" LAST UPDATE: {timestamp}")
                print(f" STATUS:      {status}")
                print("------------------------------------------")
                print(f" SPEED:       {speed} km/h")
                print(f" LEAN ANGLE:  {lean}°")
                print(f" G-FORCE:     {g_force}G")
                print("==========================================")
                print(" Press Ctrl+C to exit monitor")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nMonitor stopped.")

if __name__ == "__main__":
    start_monitor("RAD_BIKE_V1")