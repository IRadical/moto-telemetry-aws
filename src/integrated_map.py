import matplotlib
matplotlib.use('Agg') # Stable backend to prevent recursion errors and UI hangs
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import numpy as np

def generate_integrated_map(file_path):
    print(f"--- INITIALIZING INTEGRATED TELEMETRY ENGINE: {file_path} ---")
    
    try:
        # 1. XML DATA PARSING
        tree = ET.parse(file_path)
        root = tree.getroot()

        data = {}
        for c in root.findall('.//container'):
            if c.text and c.get('init'):
                # Clean 'nan' strings and convert to numerical values
                data[c.text] = [float(x) if x.strip().lower() != 'nan' else 0.0 for x in c.get('init').split(',') if x.strip()]

        # 2. DATA EXTRACTION & CLEANING
        lats = np.array(data.get('locLat', [])).flatten()
        lons = np.array(data.get('locLon', [])).flatten()
        t_gps = np.array(data.get('loc_time', [])).flatten()
        v_ms = np.nan_to_num(np.array(data.get('locV', []))).flatten() 
        roll = np.array(data.get('roll', [])).flatten()
        t_roll = np.array(data.get('attT', [])).flatten()

        if len(lats) < 2:
            print("Error: No valid GPS coordinates found.")
            return

        # 3. DOWNSAMPLING (To maintain performance)
        max_points = 5000
        if len(lats) > max_points:
            step = len(lats) // max_points
            lats, lons, t_gps, v_ms = lats[::step], lons[::step], t_gps[::step], v_ms[::step]
            print(f"Downsampling applied: Using 1 every {step} points.")

        # 4. SENSORS SYNC & PHYSICS CALCULATIONS
        # Sync Lean (Roll) to GPS timestamps
        sync_lean = np.interp(t_gps, t_roll, np.abs(roll))
        
        # Calculate Acceleration (dv/dt)
        dt = np.diff(t_gps, prepend=t_gps[0])
        dt[dt <= 0] = 0.1 # Prevent division by zero
        accel = np.diff(v_ms, prepend=v_ms[0]) / dt
        
        # Low Pass Filter (Smooths acceleration for point sizing)
        def low_pass_filter(signal, alpha=0.1):
            filtered = np.zeros_like(signal)
            filtered[0] = signal[0]
            for i in range(1, len(signal)):
                filtered[i] = alpha * signal[i] + (1 - alpha) * filtered[i-1]
            return filtered
        
        clean_accel = low_pass_filter(accel)

        # 5. VISUAL CONFIGURATION (DARK MODE)
        plt.figure(figsize=(14, 10), facecolor='#121212')
        ax = plt.gca()
        ax.set_facecolor('#121212')

        # Trajectory guide line (Subtle white line)
        plt.plot(lons, lats, color='white', alpha=0.15, linewidth=1, zorder=1)

        # Telemetry Scatter Plot
        # Size = G-Force Intensity | Color = Lean Angle
        point_sizes = 20 + (np.abs(clean_accel) * 80)
        scatter = ax.scatter(lons, lats,
                            c=sync_lean,
                            s=point_sizes,
                            cmap='plasma', 
                            alpha=0.85,
                            edgecolors='none',
                            zorder=2)
        
        # 6. AXES & LABELS (High Visibility)
        plt.title(f"RAD_BIKE_TELEMETRY: {file_path}", color='white', fontsize=16, pad=20)
        
        # Axis Labels
        plt.xlabel("Longitude (Decimal Degrees)", color='white', fontsize=12, labelpad=10)
        plt.ylabel("Latitude (Decimal Degrees)", color='white', fontsize=12, labelpad=10)

        # Ticks (White numbers)
        ax.tick_params(axis='x', colors='white', labelsize=10)
        ax.tick_params(axis='y', colors='white', labelsize=10)

        # Colorbar for Lean Angle
        cbar = plt.colorbar(scatter)
        cbar.set_label('Lean Angle (Degrees)', color='white', labelpad=15)
        cbar.ax.yaxis.set_tick_params(color='white', labelcolor='white')

        # Location Label (Bottom Left - Neon Cyan)
        plt.text(0.02, 0.05, "CHIHUAHUA CITY, MEX.", transform=ax.transAxes, 
                 color='#00f2ff', fontsize=14, fontweight='bold',
                 bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'))

        # Start/End Markers
        plt.scatter(lons[0], lats[0], color='#00f2ff', s=180, marker='P', label='Start (Work)')
        plt.scatter(lons[-1], lats[-1], color='#39ff14', s=180, marker='*', label='End (Home)')

        # Metadata Statistics Box
        stats_text = (f"Max Speed: {np.max(v_ms)*3.6:.1f} km/h\n"
                    f"Max Lean: {np.max(sync_lean):.1f}°\n"
                    f"Max Accel: {np.max(clean_accel):.2f} m/s²")
        
        plt.text(0.98, 0.02, stats_text, transform=ax.transAxes, color='white',
                ha='right', va='bottom', bbox=dict(facecolor='black', alpha=0.6, edgecolor='#00f2ff'))

        plt.grid(color='#333333', linestyle='--', alpha=0.3)
        plt.legend(facecolor='#1a1a1a', edgecolor='white', labelcolor='white')

        # 7. EXPORT & CLEANUP
        output_name = "integrated_ride_analysis_final.png"
        plt.savefig(output_name, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ FINAL ANALYSIS EXPORTED: {output_name}")

    except Exception as e:
        print(f"Critical error during mapping: {e}")

if __name__ == "__main__":
    generate_integrated_map("moto 2026-03-25 17-29-24.phyphox")