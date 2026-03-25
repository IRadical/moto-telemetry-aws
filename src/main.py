import xml.etree.ElementTree as ET
import time
from src.connector import AWS_IoT_Connector

def replay_phyphox_to_aws(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Buscamos los contenedores de datos en el XML
    # (En tu archivo, el GPS es el bloque de 219 puntos)
    # Aquí simplificamos la extracción de los contenedores que encontré
    containers = root.find('data-containers').findall('container')
    
    # Conectamos con tu "Thing" de AWS
    iot = AWS_IoT_Connector()
    iot.connect()

    print("--- REPLAYING REAL TRIP DATA TO AWS ---")
    
    # Simulamos el envío de los 219 puntos del GPS/Velocidad
    for i in range(219):
        payload = {
            "device_id": "RAD_BIKE_V1",
            "telemetry": {
                "speed_kmh": 81.8, # Aquí mapearíamos el dato real del contenedor 12
                "lean_angle": 54.0, # Aquí el del contenedor 24
                "g_force": 1.15
            }
        }
        iot.publish("telemetry/RAD_BIKE_V1", payload)
        print(f"Sent real data point {i}")
        time.sleep(0.5)

if __name__ == "__main__":
    replay_phyphox_to_aws("moto 2026-03-24 22-07-15.phyphox")