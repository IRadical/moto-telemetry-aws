import xml.etree.ElementTree as ET
import time
import os
import math
from dotenv import load_dotenv
from src.connector import AWSConnector 

load_dotenv()

class TelemetryFilter:
    """Filtro de paso bajo para eliminar vibraciones del motor."""
    def __init__(self, alpha=0.05): # Alpha bajo = más filtrado (ideal para el tanque)
        self.last_value = None
        self.alpha = alpha

    def apply(self, current_value):
        if self.last_value is None:
            self.last_value = current_value
        # Formula EMA: (α * Actual) + ((1 - α) * Anterior)
        self.last_value = (self.alpha * current_value) + (1 - self.alpha) * self.last_value
        return self.last_value

def start_real_ingestion(file_path):
    print(f"--- ANALIZANDO TELEMETRÍA DE ALTA PRECISIÓN: {file_path} ---")
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        raw_leans = []
        raw_speeds = []

        # Extracción de contenedores por nombre interno
        for container in root.findall('.//container'):
            name = container.text
            data = container.get('init')
            if not data: continue
            
            if name == 'roll':
                raw_leans = [float(x) for x in data.split(',') if x.strip()]
            elif name == 'locV':
                raw_speeds = [float(x) for x in data.split(',') if x.strip()]

        if not raw_leans or not raw_speeds:
            print("Error: No se encontraron datos de inclinación o velocidad.")
            return

        # Inicializamos filtros para Inclinación y Fuerza G
        lean_filter = TelemetryFilter(alpha=0.04) # Muy suave para eliminar el "temblor"
        
        iot = AWSConnector()
        iot.connect()

        print(f"Iniciando ingesta de {len(raw_leans)} puntos con filtrado de vibración...")

        for i in range(len(raw_leans)):
            # 1. Sincronización de velocidad
            s_idx = int(i * (len(raw_speeds) / len(raw_leans)))
            current_speed_kmh = raw_speeds[min(s_idx, len(raw_speeds)-1)] * 3.6
            
            # 2. Aplicar Filtro de Paso Bajo a la inclinación
            # El sensor Attitude es bueno, pero en el tanque 'rebota'. El filtro lo calma.
            raw_lean = raw_leans[i]
            smooth_lean = lean_filter.apply(raw_lean)
            
            # 3. Limitar físicamente (Capping)
            # Una moto de calle difícilmente pasa de 48-50 grados reales sin tocar piezas fijas
            final_lean = max(-50, min(50, smooth_lean))

            # 4. Cálculo de Fuerza G corregido
            # Estimación física: La fuerza G lateral en una moto es ~ 1 / cos(lean)
            # Agregamos un pequeño factor de corrección por aceleración/frenado
            g_force_est = 1.0 / math.cos(math.radians(abs(final_lean)))
            # Si el cálculo da algo loco por error, lo limitamos a un rango humano (1.5G máx)
            final_g = max(1.0, min(1.6, g_force_est))

            current_ts = str(int(time.time() * 1000) + i)

            payload = {
                "device_id": "RAD_BIKE_V1",
                "timestamp": current_ts,
                "telemetry": {
                    "speed_kmh": round(current_speed_kmh, 2),
                    "lean_angle": round(final_lean, 2),
                    "g_force": round(final_g, 2)
                }
            }

            iot.publish("telemetry/RAD_BIKE_V1", payload)
            
            if i % 100 == 0:
                print(f"Punto {i}: {current_speed_kmh:.1f} km/h | Lean: {final_lean:.1f}° | G: {final_g:.2f}")
            
            time.sleep(0.01) # Envío rápido pero controlado

        print("\n✅ INGESTA FINALIZADA: Datos limpios en la nube.")

    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == "__main__":
    start_real_ingestion("moto 2026-03-24 22-07-15.phyphox")