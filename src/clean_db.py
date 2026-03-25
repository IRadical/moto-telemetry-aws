import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def purge_fake_data(bike_id):
    print(f"--- PURGING DATA FOR: {bike_id} ---")
    
    # Conexión a DynamoDB
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-2',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    table = dynamodb.Table('MotoTelemetry_Dev')

    try:
        # 1. Escaneamos para encontrar todas las llaves (device_id y timestamp)
        # Nota: Scan es costoso en tablas enormes, pero para nuestra Dev es perfecto.
        response = table.scan(
            ProjectionExpression="device_id, #ts",
            ExpressionAttributeNames={"#ts": "timestamp"},
            FilterExpression="device_id = :bid",
            ExpressionAttributeValues={":bid": bike_id}
        )
        items = response.get('Items', [])

        if not items:
            print("Database is already clean. No fake data found.")
            return

        print(f"Found {len(items)} fake records. Starting deletion...")

        # 2. Borrado masivo (Batch Delete)
        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(
                    Key={
                        'device_id': item['device_id'],
                        'timestamp': item['timestamp']
                    }
                )
        
        print(f"SUCCESS: {len(items)} records deleted. Your cloud is now pristine.")

    except Exception as e:
        print(f"Purge error: {e}")

if __name__ == "__main__":
    purge_fake_data("RAD_BIKE_V1")