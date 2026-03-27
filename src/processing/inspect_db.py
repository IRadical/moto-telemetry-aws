import os
import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

load_dotenv()

def inspect_latest_data(bike_id, limit=5):
    print(f"--- INSPECTING DYNAMODB: {bike_id} ---")
    
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-2',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    table = dynamodb.Table('MotoTelemetry_Dev')

    try:
        # Escaneamos la tabla para ver el conteo total y los últimos registros
        response = table.query(
            KeyConditionExpression=Key('device_id').eq(bike_id),
            Limit=limit,
            ScanIndexForward=False  # Trae los más recientes primero
        )
        
        items = response.get('Items', [])
        count = response.get('Count', 0)

        print(f"Total records found for this query: {count}")
        print("-" * 40)
        
        for item in items:
            ts = item.get('timestamp')
            tel = item.get('telemetry', {})
            print(f"TS: {ts} | Speed: {tel.get('speed_kmh')} km/h | Lean: {tel.get('lean_angle')}°")
        
        if not items:
            print("⚠️ Table is empty. The data is not hitting the database yet.")

    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    inspect_latest_data("RAD_BIKE_V1")