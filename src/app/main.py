import os
from src.core.parser import parse_phyphox
from src.core.physics import process_physics
from src.visuals.dashboard import create_report

def main():
    # Define el archivo de entrada y salida
    file_name = "moto 2026-03-25 17-29-24.phyphox"
    input_path = os.path.join("data", file_name)
    output_name = "analisis_dinamo_400"
    
    if not os.path.exists(input_path):
        print(f"❌ Error: No se encuentra el archivo {input_path}")
        return

    print(f"🚀 Iniciando procesamiento de telemetría: {file_name}")
    
    # 1. Extraer
    raw_data = parse_phyphox(input_path)
    
    # 2. Calcular (Física + Driver Profile)
    physics_data = process_physics(raw_data)
    
    if physics_data:
        # 3. Visualizar
        create_report(physics_data, output_name)
        print(f"✅ Dashboard generado con éxito en: exports/{output_name}.png")
    else:
        print("❌ Error: No se pudieron procesar los datos físicos.")

if __name__ == "__main__":
    main()