import os
import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

load_dotenv()

def generate_session_report(bike_id):
    print(f"\n--- GENERATING PERFORMANCE REPORT: {bike_id} ---")
    
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-2',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    table = dynamodb.Table('MotoTelemetry_Dev')

    try:
        # Traemos TODOS los registros de esta moto
        response = table.query(
            KeyConditionExpression=Key('device_id').eq(bike_id)
        )
        items = response.get('Items', [])

        if not items:
            print("No data found to analyze.")
            return

        # Procesamiento de métricas
        speeds = [float(i['telemetry']['speed_kmh']) for i in items]
        leans = [abs(float(i['telemetry']['lean_angle'])) for i in items]
        gs = [float(i['telemetry']['g_force']) for i in items]

        print("==========================================")
        print(f" SESSION SUMMARY ({len(items)} data points)")
        print("==========================================")
        print(f" MAX SPEED:      {max(speeds):.1f} km/h")
        print(f" AVG SPEED:      {sum(speeds)/len(speeds):.1f} km/h")
        print(f" MAX LEAN ANGLE: {max(leans):.1f}°")
        print(f" MAX G-FORCE:    {max(gs):.2f}G")
        print("==========================================")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_session_report("RAD_BIKE_V1")