import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import os

from src.analysis.performance import get_driver_role
from .components import draw_gauge

LEAN_REFERENCE_CAP = 64.0


def normalize_lean_for_display(raw_lean):
    return float(np.clip(raw_lean, 0.0, LEAN_REFERENCE_CAP))


def classify_lean_reference(lean_deg):
    if lean_deg < 5:
        return "0° Upright"
    elif lean_deg < 40:
        return "Below Scooter Range"
    elif lean_deg < 50:
        return "40° Scooter"
    elif lean_deg < 55:
        return "50° Street Bike"
    elif lean_deg < 61:
        return "55° Super Sport"
    elif lean_deg < 64:
        return "61° SBK"
    else:
        return "64° MotoGP"


def create_report(p, filename):

    m = p["metrics"]
    role = get_driver_role(m)

    display_lean_series = np.clip(np.array(p["lean"], dtype=float), 0.0, LEAN_REFERENCE_CAP)
    display_max_lean = normalize_lean_for_display(m["max_lean"])
    lean_reference_label = classify_lean_reference(display_max_lean)

    if len(display_lean_series) > 0:
        lean_min = float(np.min(display_lean_series))
        lean_max = float(np.max(display_lean_series))

        if lean_max - lean_min < 1.0:
            color_lean_series = np.linspace(0, 1, len(display_lean_series))
        else:
            color_lean_series = (display_lean_series - lean_min) / (lean_max - lean_min)
    else:
        color_lean_series = display_lean_series

    fig = plt.figure(figsize=(16, 10), facecolor='#121212')
    gs = fig.add_gridspec(3, 4)

    ax_map = fig.add_subplot(gs[:, :3])
    ax_map.set_facecolor('#121212')

    ax_map.plot(p["lons"], p["lats"], color='white', alpha=0.10, zorder=1)

    sc = ax_map.scatter(
        p["lons"],
        p["lats"],
        c=color_lean_series,
        s=30 + (p["g_force"] * 180),
        cmap='plasma',
        alpha=0.95,
        zorder=2
    )

    cbar = fig.colorbar(sc, ax=ax_map, fraction=0.03, pad=0.02)
    cbar.set_label("Lean Angle (relative to this ride)", color='white', fontsize=10)
    cbar.set_ticks([0.0, 0.25, 0.5, 0.75, 1.0])

    if len(display_lean_series) > 0:
        cbar.set_ticklabels([
            f"{lean_min:.1f}°",
            f"{lean_min + (lean_max - lean_min) * 0.25:.1f}°",
            f"{lean_min + (lean_max - lean_min) * 0.5:.1f}°",
            f"{lean_min + (lean_max - lean_min) * 0.75:.1f}°",
            f"{lean_max:.1f}°"
        ])

    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(cbar.ax.get_yticklabels(), color='white')
    cbar.outline.set_edgecolor('white')

    ax_map.tick_params(colors='white')
    ax_map.set_xlabel("Longitude (Decimal Degrees)", color='gray', fontsize=10)
    ax_map.set_ylabel("Latitude (Decimal Degrees)", color='gray', fontsize=10)

    ax_map.text(
        0.02, 0.05,
        "CHIHUAHUA CITY, MEX.",
        transform=ax_map.transAxes,
        color='#6dd5ed',
        fontsize=12,
        fontweight='bold',
        alpha=0.85
    )

    idx_max_v = int(np.argmax(p["v_kmh"]))
    idx_max_accel = int(np.argmax(p["accel"]))
    idx_max_braking = int(np.argmin(p["accel"]))
    idx_max_g = int(np.argmax(p["g_force"]))
    idx_max_lean = int(np.argmax(display_lean_series))

    ax_map.annotate(
        f'MAX ACCEL\n{p["accel"][idx_max_accel]:.2f} m/s²',
        xy=(p["lons"][idx_max_accel], p["lats"][idx_max_accel]),
        xytext=(-50, 25),
        textcoords='offset points',
        color='#39ff14',
        fontsize=9,
        fontweight='bold',
        arrowprops=dict(arrowstyle='->', color='#39ff14', alpha=0.8)
    )

    ax_map.annotate(
        f'MAX BRAKING\n{abs(p["accel"][idx_max_braking]):.2f} m/s²',
        xy=(p["lons"][idx_max_braking], p["lats"][idx_max_braking]),
        xytext=(15, -25),
        textcoords='offset points',
        color='#ff3131',
        fontsize=9,
        fontweight='bold',
        arrowprops=dict(arrowstyle='->', color='#ff3131', alpha=0.8)
    )

    ax_map.annotate(
        f'TOP SPEED\n{p["v_kmh"][idx_max_v]:.1f} km/h',
        xy=(p["lons"][idx_max_v], p["lats"][idx_max_v]),
        xytext=(15, 15),
        textcoords='offset points',
        color='cyan',
        fontsize=9,
        fontweight='bold',
        arrowprops=dict(arrowstyle='->', color='cyan', alpha=0.8)
    )

    ax_map.annotate(
        f'MAX G\n{p["g_force"][idx_max_g]:.2f}G',
        xy=(p["lons"][idx_max_g], p["lats"][idx_max_g]),
        xytext=(-45, -20),
        textcoords='offset points',
        color='white',
        fontsize=9,
        fontweight='bold',
        arrowprops=dict(arrowstyle='->', color='white', alpha=0.7)
    )

    ax_map.annotate(
        f'MAX LEAN\n{display_lean_series[idx_max_lean]:.1f}°\n{lean_reference_label}',
        xy=(p["lons"][idx_max_lean], p["lats"][idx_max_lean]),
        xytext=(-95, 45),
        textcoords='offset points',
        color='#f1c40f',
        fontsize=9,
        fontweight='bold',
        ha='left',
        va='bottom',
        arrowprops=dict(arrowstyle='->', color='#f1c40f', alpha=0.8)
    )


    draw_gauge(
        fig.add_subplot(gs[0, 3]),
        float(np.max(p["v_kmh"])),
        0,
        140,
        "TOP SPEED",
        "km/h",
        "cyan"
    )

    draw_gauge(
        fig.add_subplot(gs[1, 3]),
        display_max_lean,
        0,
        64,
        "MAX LEAN",
        "Degrees",
        "#f1c40f"
    )

    ax_stats = fig.add_subplot(gs[2, 3])
    ax_stats.axis('off')

    riding_style = (
        'Aggressive' if m['safety_score'] < 40
        else 'Moderate' if m['safety_score'] < 75
        else 'Safe'
    )

    box_txt = (
        f"PILOT PROFILE: {role}\n"
        f"--------------------------\n"
        f"SAFETY SCORE: {m['safety_score']:.1f}/100\n"
        f"STYLE: {riding_style}\n\n"
        f"LEAN CLASS: {lean_reference_label}\n\n"
        f"TELEMETRY LOG:\n"
        f"● Max Lean: {display_max_lean:.1f}°\n"
        f"● Max G-Force: {m['max_g']:.2f}G\n"
        f"● Avg Speed: {m['avg_speed']:.1f} km/h\n"
        f"● Volatility: {m['volatility']:.2f}"
    )

    ax_stats.text(
        0.05,
        0.5,
        box_txt,
        color='white',
        family='monospace',
        fontsize=11,
        va='center',
        bbox=dict(facecolor='#1a1a1a', pad=12, edgecolor='#333333')
    )

    plt.tight_layout()
    os.makedirs("exports", exist_ok=True)
    plt.savefig(f"exports/{filename}.png", facecolor='#121212')
    plt.close()