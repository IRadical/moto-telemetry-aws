from matplotlib.patches import Wedge
import numpy as np

def draw_gauge(ax, value, min_val, max_val, title, unit, color):
    """Dibuja un tacómetro estilizado."""
    # Fondo
    ax.add_patch(Wedge((0.5, 0.5), 0.4, 0, 180, width=0.08, color='#333333', alpha=0.3))
    
    # Nivel
    progress = np.clip((value - min_val) / (max_val - min_val), 0, 1)
    ax.add_patch(Wedge((0.5, 0.5), 0.4, 180 - (progress * 180), 180, width=0.08, color=color))
    
    # Textos
    ax.text(0.5, 0.55, f"{value:.1f}", ha='center', va='center', color='white', fontsize=18, fontweight='bold')
    ax.text(0.5, 0.42, unit, ha='center', va='center', color='gray', fontsize=9)
    ax.text(0.5, 0.25, title, ha='center', va='center', color='white', fontsize=11, fontweight='bold')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0.2, 1)
    ax.axis('off')