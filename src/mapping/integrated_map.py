import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import xml.etree.ElementTree as ET
import numpy as np

def draw_gauge(ax, value, min_val, max_val, title, unit, color):

    wedge_bg = Wedge((0.5, 0.5), 0.4, 0, 180, width=0.08, color='#333333', alpha=0.3)
    ax.add_patch(wedge_bg)
    
    progress = (value - min_val) / (max_val - min_val)
    progress = np.clip(progress, 0, 1)
    wedge_fg = Wedge((0.5, 0.5), 0.4, 180 - (progress * 180), 180, width=0.08, color=color)
    ax.add_patch(wedge_fg)
    
    ax.text(0.5, 0.55, f"{value:.1f}", ha='center', va='center', color='white', fontsize=20, fontweight='bold')
    ax.text(0.5, 0.42, unit, ha='center', va='center', color='gray', fontsize=10)
    ax.text(0.5, 0.25, title, ha='center', va='center', color='white', fontsize=12, fontweight='bold')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0.2, 1)
    ax.axis('off')

def generate_advanced_dashboard(file_path):
    print(f"--- GENERATING PRO DASHBOARD: {file_path} ---")
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        data = {}
        for c in root.findall('.//container'):
            if c.text and c.get('init'):
                vals = []
                for x in c.get('init').split(','):
                    s = x.strip().lower()
                    vals.append(float(s) if s and s != 'nan' else 0.0)
                data[c.text] = vals

        lats = np.array(data.get('locLat', []))
        lons = np.array(data.get('locLon', []))
        t_gps = np.array(data.get('loc_time', []))
        v_ms = np.array(data.get('locV', []))
        roll = np.array(data.get('roll', []))
        t_roll = np.array(data.get('attT', []))

        mask = (lats != 0) & (lons != 0)
        lats, lons, t_gps, v_ms = lats[mask], lons[mask], t_gps[mask], v_ms[mask]

        sync_lean = 180 - np.abs(np.interp(t_gps, t_roll, roll))
        sync_lean = np.clip(sync_lean, 0, 90) 

        dt = np.diff(t_gps, prepend=t_gps[0])
        dt[dt <= 0] = 0.1
        accel = np.diff(v_ms, prepend=v_ms[0]) / dt

        idx_max_v = np.argmax(v_ms)
        idx_max_accel = np.argmax(accel)
        idx_max_braking = np.argmin(accel)

        fig = plt.figure(figsize=(16, 10), facecolor='#121212')
        gs = fig.add_gridspec(3, 4)
        
        ax_map = fig.add_subplot(gs[:, :3])
        ax_map.set_facecolor('#121212')
        ax_map.plot(lons, lats, color='white', alpha=0.1, linewidth=1, zorder=1)
        
        point_sizes = 20 + (np.abs(accel) * 100)
        sc = ax_map.scatter(lons, lats, c=sync_lean, s=point_sizes, cmap='plasma', alpha=0.7, zorder=2)
        
        ax_map.annotate(f'MAX SPEED\n{v_ms[idx_max_v]*3.6:.1f} km/h', 
                         xy=(lons[idx_max_v], lats[idx_max_v]), xytext=(15, 15),
                         textcoords='offset points', color='cyan', fontsize=10, fontweight='bold',
                         arrowprops=dict(arrowstyle='->', color='cyan'))
        
        ax_map.annotate(f'MAX ACCEL\n{accel[idx_max_accel]:.2f} m/s²', 
                         xy=(lons[idx_max_accel], lats[idx_max_accel]), xytext=(-50, 20),
                         textcoords='offset points', color='#39ff14', fontsize=10, fontweight='bold',
                         arrowprops=dict(arrowstyle='->', color='#39ff14'))

        ax_map.annotate(f'MAX BRAKING\n{abs(accel[idx_max_braking]):.2f} m/s²', 
                         xy=(lons[idx_max_braking], lats[idx_max_braking]), xytext=(15, -25),
                         textcoords='offset points', color='#ff3131', fontsize=10, fontweight='bold',
                         arrowprops=dict(arrowstyle='->', color='#ff3131'))

        ax_map.set_xlabel("Longitude", color='white')
        ax_map.set_ylabel("Latitude", color='white')
        ax_map.tick_params(colors='white')
        for s in ax_map.spines.values(): s.set_color('#333333')

        ax_speed = fig.add_subplot(gs[0, 3])
        draw_gauge(ax_speed, np.max(v_ms)*3.6, 0, 140, "MAX SPEED", "km/h", "cyan")
        
        ax_lean = fig.add_subplot(gs[1, 3])
        draw_gauge(ax_lean, np.max(sync_lean), 0, 60, "MAX LEAN", "Degrees", "#f1c40f")
        
        ax_stats = fig.add_subplot(gs[2, 3])
        ax_stats.axis('off')
        stats_txt = (f"STATS LOG\n\n"
                     f"● Accel: {np.max(accel):.2f} m/s²\n"
                     f"● Brake: {np.abs(np.min(accel)):.2f} m/s²\n"
                     f"● Lean: {np.max(sync_lean):.1f}°\n"
                     f"● Speed: {np.max(v_ms)*3.6:.1f} km/h")
        ax_stats.text(0.1, 0.5, stats_txt, color='white', fontsize=13, family='monospace', va='center',
                      bbox=dict(facecolor='#1a1a1a', alpha=0.8, edgecolor='#333333', pad=10))

        output_name = "exports/dashboard_telemetry.png" # <--- Añade 'exports/'
        plt.savefig(output_name, dpi=300, bbox_inches='tight')
        print("✅ DASHBOARD GENERATED: dashboard_telemetry.png")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_advanced_dashboard("data/moto 2026-03-25 17-29-24.phyphox")