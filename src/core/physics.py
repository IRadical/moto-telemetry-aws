import numpy as np

LEAN_REFERENCE_CAP = 64.0


def smooth_signal(sig, window=3):
    if len(sig) < window:
        return sig
    return np.convolve(sig, np.ones(window) / window, mode='same')


def circular_mean_deg(angles_deg):
    angles_rad = np.deg2rad(angles_deg)
    s = np.mean(np.sin(angles_rad))
    c = np.mean(np.cos(angles_rad))
    return np.rad2deg(np.arctan2(s, c))


def angular_diff_deg(a, b):
    return (a - b + 180) % 360 - 180


def normalize_quaternions(w, x, y, z):
    norm = np.sqrt(w**2 + x**2 + y**2 + z**2)
    norm[norm == 0] = 1.0
    return w / norm, x / norm, y / norm, z / norm


def compute_lean_from_quaternion(data, t_gps):
    """
    Calcula la inclinación total respecto a la vertical usando cuaterniones.
    Es más estable que usar Euler roll.
    """
    t_att = np.array(data.get('attT', [])).flatten()
    att_w = np.array(data.get('attW', [])).flatten()
    att_x = np.array(data.get('attX', [])).flatten()
    att_y = np.array(data.get('attY', [])).flatten()
    att_z = np.array(data.get('attZ', [])).flatten()

    if not (
        len(t_att) > 1
        and len(att_w) == len(t_att)
        and len(att_x) == len(t_att)
        and len(att_y) == len(t_att)
        and len(att_z) == len(t_att)
    ):
        return None

    sync_w = np.interp(t_gps, t_att, att_w)
    sync_x = np.interp(t_gps, t_att, att_x)
    sync_y = np.interp(t_gps, t_att, att_y)
    sync_z = np.interp(t_gps, t_att, att_z)

    sync_w, sync_x, sync_y, sync_z = normalize_quaternions(sync_w, sync_x, sync_y, sync_z)

    # r33 = componente Z del eje vertical transformado
    r33 = 1 - 2 * (sync_x**2 + sync_y**2)

    # inclinación total respecto a vertical
    lean = np.degrees(np.arccos(np.clip(r33, -1.0, 1.0)))

    # Calibración con tramo inicial para quitar offset del soporte
    calib_count = min(10, len(lean))
    baseline = np.median(lean[:calib_count]) if calib_count > 0 else 0.0
    lean = np.abs(lean - baseline)

    return lean


def compute_lean_from_roll(data, t_gps):
    """
    Fallback si no hay cuaterniones:
    usa roll con media circular y diferencia angular corta.
    """
    roll = np.array(data.get('roll', [])).flatten()
    t_roll = np.array(data.get('attT', [])).flatten()

    if len(roll) < 2 or len(t_roll) < 2:
        return None

    sync_roll_raw = np.interp(t_gps, t_roll, roll)

    calib_count = min(10, len(sync_roll_raw))
    if calib_count > 0:
        baseline_roll = circular_mean_deg(sync_roll_raw[:calib_count])
    else:
        baseline_roll = circular_mean_deg(sync_roll_raw)

    diff_angle = angular_diff_deg(sync_roll_raw, baseline_roll)
    lean = np.abs(diff_angle)

    return lean


def process_physics(data):
    """
    Procesa telemetría física para mapa/dashboard.
    Prioriza cuaterniones para lean angle.
    """
    # GPS
    t_gps = np.array(data.get('loc_time', [])).flatten()
    lats = np.array(data.get('locLat', [])).flatten()
    lons = np.array(data.get('locLon', [])).flatten()
    v_ms = np.nan_to_num(np.array(data.get('locV', []))).flatten()

    # IMU lineal
    lin_x = np.array(data.get('linX', [])).flatten()
    lin_y = np.array(data.get('linY', [])).flatten()
    lin_z = np.array(data.get('linZ', [])).flatten()
    t_lin = np.array(data.get('lin_time', [])).flatten()

    if len(t_gps) < 2 or len(lats) < 2 or len(lons) < 2:
        return None

    # =========================================================================
    # 1. LEAN ANGLE
    # =========================================================================
    sync_lean_real = compute_lean_from_quaternion(data, t_gps)

    if sync_lean_real is None:
        sync_lean_real = compute_lean_from_roll(data, t_gps)

    if sync_lean_real is None:
        sync_lean_real = np.zeros_like(t_gps, dtype=float)

    # Cap físico/visual basado en tu referencia moto
    sync_lean_real = np.clip(sync_lean_real, 0.0, LEAN_REFERENCE_CAP)

    # =========================================================================
    # 2. VELOCIDAD Y ACELERACIÓN LONGITUDINAL
    # =========================================================================
    v_kmh = v_ms * 3.6

    dt_gps = np.diff(t_gps, prepend=t_gps[0])
    dt_gps[dt_gps <= 0] = 1.0

    raw_accel_gps = np.diff(v_ms, prepend=v_ms[0]) / dt_gps
    clean_accel_ms2 = smooth_signal(raw_accel_gps, window=3)

    # =========================================================================
    # 3. FUERZA G
    # =========================================================================
    if len(lin_x) > 0 and len(lin_y) > 0 and len(lin_z) > 0 and len(t_lin) > 1:
        raw_g_ms2 = np.sqrt(lin_x**2 + lin_y**2 + lin_z**2)
        clean_g_ms2 = smooth_signal(raw_g_ms2, window=10)
        sync_g = np.abs(np.interp(t_gps, t_lin, clean_g_ms2)) / 9.81
        max_g_linear = float(np.max(sync_g))
    else:
        sync_g = np.abs(clean_accel_ms2) / 9.81
        max_g_linear = float(np.max(sync_g))

    # =========================================================================
    # 4. MÉTRICAS
    # =========================================================================
    max_lean = float(np.max(sync_lean_real))
    avg_speed = float(np.mean(v_kmh))
    volatility = float(np.std(v_kmh))

    penalty = (max_lean * 0.6) + (max_g_linear * 12) + (avg_speed * 0.15)
    safety_score = float(max(0, min(100, 100 - penalty)))

    return {
        "lats": lats,
        "lons": lons,
        "v_kmh": v_kmh,
        "lean": sync_lean_real,
        "g_force": sync_g,
        "accel": clean_accel_ms2,
        "metrics": {
            "max_lean": max_lean,
            "max_g": max_g_linear,
            "avg_speed": avg_speed,
            "volatility": volatility,
            "safety_score": safety_score,
        }
    }