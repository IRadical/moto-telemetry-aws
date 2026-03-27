import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from src.analysis.performance import get_driver_role
import numpy as np
import os
from .components import draw_gauge

def create_report(p, filename):
    """
    Genera un dashboard fusionando el mapa de Chihuahua con hitos de rendimiento
    y la lógica de inteligencia de driver_profile.
    """
    # 1. Recuperar Métricas y Rol (Lógica de Driver Profile)
    m = p["metrics"]
    role = get_driver_role(m)
    
    # 2. Layout del Dashboard (16:10, Dark Mode)
    fig = plt.figure(figsize=(16, 10), facecolor='#121212')
    gs = fig.add_gridspec(3, 4)
    
    # --- MAIN MAP (Grid 3x3) ---
    ax_map = fig.add_subplot(gs[:, :3])
    ax_map.set_facecolor('#121212')
    ax_map.plot(p["lons"], p["lats"], color='white', alpha=0.1, zorder=1)
    
    # Los puntos ahora escalan por G-Force para mayor claridad visual
    scatter = ax_map.scatter(p["lons"], p["lats"], c=p["lean"], 
                             s=20 + (p["g_force"]*150), cmap='plasma', alpha=0.8, zorder=2)
    
    # Estética de Ejes (Blanco) y Etiquetas
    ax_map.tick_params(colors='white')
    ax_map.set_xlabel("Longitude (Decimal Degrees)", color='gray', fontsize=10)
    ax_map.set_ylabel("Latitude (Decimal Degrees)", color='gray', fontsize=10)
    
    # Etiqueta de Ubicación (Cian Neón)
    ax_map.text(0.02, 0.05, "CHIHUAHUA CITY, MEX.", transform=ax_map.transAxes, 
                color='#00f2ff', fontsize=12, fontweight='bold', alpha=0.8)

    # =========================================================================
    # 3. IDENTIFICACIÓN Y ANOTACIÓN DE HITOS DE RENDIMIENTO (Fusión Solicitada)
    # =========================================================================
    
    # Encontrar los índices (la ubicación exacta) de cada récord
    idx_max_v = np.argmax(p["v_kmh"])       # Mayor Velocidad
    idx_max_accel = np.argmax(p["accel"])   # Mayor Aceleración
    idx_max_braking = np.argmin(p["accel"]) # Mayor Frenada (mínima acel)
    idx_max_g = np.argmax(p["g_force"])     # Mayor Fuerza G
    idx_max_lean = np.argmax(p["lean"])     # Mayor Tumbada

    # -- Configuración de flechas y etiquetas --
    # Usamos colores vibrantes y legibles contra el fondo oscuro
    # NOTA: Los offsets (xytext) están ajustados para evitar que se amontonen
    
    # A. MAX ACCEL (Verde Neón)
    ax_map.annotate(f'MAX ACCEL\n{p["accel"][idx_max_accel]:.2f} m/s²', 
                     xy=(p["lons"][idx_max_accel], p["lats"][idx_max_accel]), 
                     xytext=(-50, 25), textcoords='offset points', 
                     color='#39ff14', fontsize=9, fontweight='bold',
                     arrowprops=dict(arrowstyle='->', color='#39ff14', alpha=0.8))
    
    # B. MAX BRAKING (Rojo Neón)
    ax_map.annotate(f'MAX BRAKING\n{abs(p["accel"][idx_max_braking]):.2f} m/s²', 
                     xy=(p["lons"][idx_max_braking], p["lats"][idx_max_braking]), 
                     xytext=(15, -25), textcoords='offset points', 
                     color='#ff3131', fontsize=9, fontweight='bold',
                     arrowprops=dict(arrowstyle='->', color='#ff3131', alpha=0.8))

    # C. TOP SPEED (Cian)
    ax_map.annotate(f'TOP SPEED\n{p["v_kmh"][idx_max_v]:.1f} km/h', 
                     xy=(p["lons"][idx_max_v], p["lats"][idx_max_v]), 
                     xytext=(15, 15), textcoords='offset points', 
                     color='cyan', fontsize=9, fontweight='bold',
                     arrowprops=dict(arrowstyle='->', color='cyan', alpha=0.8))

    # D. MAX G-FORCE (Blanco)
    ax_map.annotate(f'MAX G\n{p["g_force"][idx_max_g]:.2f}G', 
                     xy=(p["lons"][idx_max_g], p["lats"][idx_max_g]), 
                     xytext=(-45, -20), textcoords='offset points', 
                     color='white', fontsize=9, fontweight='bold',
                     arrowprops=dict(arrowstyle='->', color='white', alpha=0.7))

    # E. MAX LEAN (Oro)
    ax_map.annotate(f'MAX LEAN\n{p["lean"][idx_max_lean]:.1f}°', 
                     xy=(p["lons"][idx_max_lean], p["lats"][idx_max_lean]), 
                     xytext=(-15, 30), textcoords='offset points', 
                     color='#f1c40f', fontsize=9, fontweight='bold',
                     arrowprops=dict(arrowstyle='->', color='#f1c40f', alpha=0.8))
    
    # =========================================================================

    # 4. TACÓMETROS Y LOG (Derecha)
    
    # Tacómetros circulares (Gauges)
    draw_gauge(fig.add_subplot(gs[0, 3]), np.max(p["v_kmh"]), 0, 140, "TOP SPEED", "km/h", "cyan")
    draw_gauge(fig.add_subplot(gs[1, 3]), m["max_lean"], 0, 60, "MAX LEAN", "Degrees", "#f1c40f")

    # Stats Log (Integración de driver_profile)
    ax_stats = fig.add_subplot(gs[2, 3])
    ax_stats.axis('off')
    
    riding_style = 'Aggressive' if m['safety_score'] < 40 else 'Moderate' if m['safety_score'] < 75 else 'Safe'
    
    box_txt = (f"PILOT PROFILE: {role}\n"
               f"--------------------------\n"
               f"SAFETY SCORE: {m['safety_score']:.1f}/100\n"
               f"STYLE: {riding_style}\n\n"
               f"TELEMETRY LOG:\n"
               f"● Max Lean: {m['max_lean']:.1f}°\n"
               f"● Max G-Force: {m['max_g']:.2f}G\n"
               f"● Avg Speed: {m['avg_speed']:.1f} km/h\n"
               f"● Volatility: {m['volatility']:.2f}")
    
    ax_stats.text(0.05, 0.5, box_txt, color='white', family='monospace', fontsize=11,
                  va='center', bbox=dict(facecolor='#1a1a1a', pad=12, edgecolor='#333333'))

    # Finalizar y exportar
    plt.tight_layout()
    os.makedirs("exports", exist_ok=True)
    plt.savefig(f"exports/{filename}.png", facecolor='#121212')
    plt.close()