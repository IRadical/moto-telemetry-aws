import os
import csv
import boto3
from dotenv import load_dotenv

load_dotenv()

def export_to_csv(bike_id):
    print(f"--- EXPORTING TELEMETRY: {bike_id} ---")
    
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-2',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    table = dynamodb.Table('MotoTelemetry_Dev')

    try:
        response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key('device_id').eq(bike_id))
        items = response.get('Items', [])

        if not items:
            print("No data to export.")
            return

        filename = f"telemetry_{bike_id}.csv"
        
        # Definimos las columnas
        headers = ['timestamp', 'speed_kmh', 'lean_angle', 'g_force']

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for item in items:
                t = item.get('telemetry', {})
                writer.writerow({
                    'timestamp': item.get('timestamp'),
                    'speed_kmh': round(float(t.get('speed_kmh', 0)), 2),
                    'lean_angle': round(float(t.get('lean_angle', 0)), 2),
                    'g_force': round(float(t.get('g_force', 0)), 2)
                })

        print(f"SUCCESS: Data saved to {filename}")
        print(f"Total records exported: {len(items)}")

    except Exception as e:
        print(f"Export error: {e}")

if __name__ == "__main__":
    export_to_csv("RAD_BIKE_V1")