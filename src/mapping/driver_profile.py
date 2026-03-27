import os
import boto3
import numpy as np
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

load_dotenv()

def get_detailed_role(lean, g_force, speed, volatility):
    # Definición de rangos para la matriz
    # Lean: Safe (<20), Sport (20-45), Extreme (>45)
    # G-Force: Smooth (<0.8), Active (0.8-1.2), Violent (>1.2)
    # Speed: Slow (<40), Mid (40-90), Fast (>90)
    
    matrix = {
        # LOW SPEED ROLES (<40 km/h)
        (0,0,0): "The Ghost (Ultra-Safe)", (0,1,0): "Cautious Learner", (0,2,0): "Urban Gymkhana Novice",
        (1,0,0): "Smooth Cruiser", (1,1,0): "Traffic Weaver", (1,2,0): "Low-Speed Stuntman",
        (2,0,0): "Lean Specialist", (2,1,0): "The Acrobat", (2,2,0): "Parking Lot Scientist",
        
        # MID SPEED ROLES (40-90 km/h)
        (0,0,1): "Steady Commuter", (0,1,1): "Efficient Courier", (0,2,1): "Aggressive Delivery",
        (1,0,1): "Weekend Tourer", (1,1,1): "Twisty Hunter", (1,2,1): "Street Fighter",
        (2,0,1): "Technical Carver", (2,1,1): "Knee Slider", (2,2,1): "Urban Renegade",
        
        # HIGH SPEED ROLES (>90 km/h)
        (0,0,2): "Highway Liner", (0,1,2): "Speed Merchant", (0,2,2): "Interstate Interceptor",
        (1,0,2): "Fast Lane Tourist", (1,1,2): "Apex Predator", (1,2,2): "Midnight Express",
        (2,0,2): "Track Day Warrior", (2,1,2): "MotoGP Aspirant", (2,2,2): "The Radical Spirit",
        
        # SPECIAL ROLES (Based on Volatility/Erratic behavior)
        "erratic": "Chaos Rider", "smooth": "Zen Master", "stunt": "The Wheelie King"
    }

    # Asignar índices (0, 1, 2)
    l_idx = 0 if lean < 25 else (1 if lean < 45 else 2)
    g_idx = 0 if g_force < 0.8 else (1 if g_force < 1.2 else 2)
    s_idx = 0 if speed < 40 else (1 if speed < 90 else 2)
    
    role = matrix.get((l_idx, g_idx, s_idx), "Versatile Rider")
    if volatility > 15: role = f"Erratic {role}"
    return role

def analyze_driver_style(bike_id):
    print(f"\n--- DEEP DRIVER ANALYSIS: {bike_id} ---")
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('MotoTelemetry_Dev')

    try:
        response = table.query(KeyConditionExpression=Key('device_id').eq(bike_id))
        items = response.get('Items', [])
        if not items: return

        # Métricas extraídas
        speeds = [float(i['telemetry']['speed_kmh']) for i in items]
        leans = [abs(float(i['telemetry']['lean_angle'])) for i in items]
        gs = [float(i['telemetry']['g_force']) for i in items]
        
        max_lean = max(leans)
        max_g = max(gs)
        avg_speed = np.mean(speeds)
        speed_volatility = np.std(speeds) # Desviación estándar para medir "nerviosismo"

        # Cálculo de SAFETY SCORE (0-100)
        # Penalizamos inclinación extrema, fuerzas G violentas y exceso de velocidad
        penalty = (max_lean * 0.6) + (max_g * 12) + (avg_speed * 0.15)
        safety_score = max(0, min(100, 100 - penalty))

        # Determinar Rol de entre los 30+ disponibles
        role = get_detailed_role(max_lean, max_g, avg_speed, speed_volatility)

        print("==========================================")
        print(f"        PILOT PROFILE: {role}")
        print("==========================================")
        print(f" > SAFETY SCORE: {safety_score:.1f} / 100")
        print(f" > RIDING STYLE: {'Aggressive' if safety_score < 40 else 'Moderate' if safety_score < 75 else 'Safe'}")
        print("------------------------------------------")
        print(f" STATS:")
        print(f" - Max Lean:    {max_lean:.1f}°")
        print(f" - Max G-Force: {max_g:.2f}G")
        print(f" - Avg Speed:   {avg_speed:.1f} km/h")
        print(f" - Volatility:  {speed_volatility:.2f} (Speed std)")
        print("==========================================")

    except Exception as e:
        print(f"Analysis error: {e}")

if __name__ == "__main__":
    analyze_driver_style("RAD_BIKE_V1")