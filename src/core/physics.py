import numpy as np

def process_physics(data):
    """
    Física depurada: 
    - Wrap-around handling para evitar ángulos imposibles (>90°).
    - GPS suavizado para Aceleración/Frenada (ignora baches).
    - IMU pura para Fuerza G total (Torque + Curvas).
    """
    t_gps = np.array(data.get('loc_time', [])).flatten()
    lats = np.array(data.get('locLat', [])).flatten()
    lons = np.array(data.get('locLon', [])).flatten()
    v_ms = np.nan_to_num(np.array(data.get('locV', []))).flatten()
    roll = np.array(data.get('roll', [])).flatten()
    t_roll = np.array(data.get('attT', [])).flatten()

    lin_x = np.array(data.get('linX', [])).flatten()
    lin_y = np.array(data.get('linY', [])).flatten()
    lin_z = np.array(data.get('linZ', [])).flatten()
    t_lin = np.array(data.get('lin_time', [])).flatten()

    if len(lats) < 2: return None

    # 1. ÁNGULO REAL (Solución al bug de 227° mediante Módulo 360)
    sync_roll_raw = np.interp(t_gps, t_roll, roll)
    baseline_roll = np.median(sync_roll_raw) 
    
    # Esta fórmula evita que un salto de -179 a 180 se sume como 359 grados
    diff_angle = (sync_roll_raw - baseline_roll + 180) % 360 - 180
    sync_lean_real = np.abs(diff_angle)
    # Sin limitador artificial. Lo que marque, es lo real.

    # 2. ACELERACIÓN Y FRENADA LONGITUDINAL (Solución al bug de 7.57 m/s²)
    # Aislamos el movimiento hacia adelante/atrás usando el GPS para ignorar los baches (eje Z)
    v_kmh = v_ms * 3.6
    dt_gps = np.diff(t_gps, prepend=t_gps[0])
    dt_gps[dt_gps <= 0] = 1.0 
    
    raw_accel_gps = np.diff(v_ms, prepend=v_ms[0]) / dt_gps
    
    # Filtro de media móvil simple (3 segundos) para estabilizar la lectura del GPS
    def smooth_gps(sig, window=3):
        if len(sig) < window: return sig
        return np.convolve(sig, np.ones(window)/window, mode='same')
        
    clean_accel_ms2 = smooth_gps(raw_accel_gps)

    # 3. FUERZA G TOTAL (Usando la IMU para el "Impacto" general)
    if len(lin_x) > 0:
        raw_g_ms2 = np.sqrt(lin_x**2 + lin_y**2 + lin_z**2)
        clean_g_ms2 = smooth_gps(raw_g_ms2, window=10) # 10 muestras a 100Hz
        sync_g = np.abs(np.interp(t_gps, t_lin, clean_g_ms2)) / 9.81
        max_g_linear = np.max(sync_g)
    else:
        sync_g = np.abs(clean_accel_ms2) / 9.81
        max_g_linear = np.max(sync_g)

    # 4. Métricas Driver Profile
    max_lean = np.max(sync_lean_real)
    avg_speed = np.mean(v_kmh)
    
    penalty = (max_lean * 0.6) + (max_g_linear * 12) + (avg_speed * 0.15)
    safety_score = max(0, min(100, 100 - penalty))

    return {
        "lats": lats, "lons": lons, "v_kmh": v_kmh, "lean": sync_lean_real, 
        "g_force": sync_g, "accel": clean_accel_ms2, "metrics": {
            "max_lean": max_lean, "max_g": max_g_linear,
            "avg_speed": avg_speed, "volatility": np.std(v_kmh),
            "safety_score": safety_score
        }
    }