import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

load_dotenv()

def fetch_recent_telemetry(bike_id, limit=5):
    print(f"--- FETCHING DATA FOR {bike_id} FROM DYNAMODB ---")
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('MotoTelemetry_Dev')
    
    try:
        response = table.query(
            KeyConditionExpression=Key('device_id').eq(bike_id),
            ScanIndexForward=False, 
            Limit=limit
        )
        
        items = response.get('Items', [])
        
        if not items:
            print("No data found for this bike.")
            return

        print(f"Successfully retrieved {len(items)} records:\n")
        
        for item in items:
            timestamp = item.get('timestamp')
            telemetry = item.get('telemetry', {})
            speed = telemetry.get('speed_kmh', 0)
            lean = telemetry.get('lean_angle', 0)
            g_force = telemetry.get('g_force', 0)
            
            print(f"[{timestamp}] | S: {speed} km/h | Lean: {lean}° | G-Force: {g_force}G")
            
    except Exception as e:
        print(f"Error querying DynamoDB: {e}")

if __name__ == "__main__":
    fetch_recent_telemetry("RAD_BIKE_V1")