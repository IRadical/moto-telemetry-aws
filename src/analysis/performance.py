def get_driver_role(metrics):
    """Clasifica al piloto según su agresividad y técnica."""
    m = metrics
    l_idx = 0 if m['max_lean'] < 25 else (1 if m['max_lean'] < 45 else 2)
    g_idx = 0 if m['max_g'] < 0.8 else (1 if m['max_g'] < 1.2 else 2)
    s_idx = 0 if m['avg_speed'] < 40 else (1 if m['avg_speed'] < 90 else 2)
    
    matrix = {
        (0,0,0): "The Ghost", (0,1,0): "Cautious Learner", (1,0,0): "Smooth Cruiser",
        (1,1,1): "Twisty Hunter", (2,0,1): "Technical Carver", (1,2,1): "Street Fighter",
        (1,1,2): "Apex Predator", (2,1,2): "MotoGP Aspirant", (2,2,2): "The Radical Spirit",
        (0,0,2): "Highway Liner", (0,1,2): "Speed Merchant", (1,0,2): "Fast Lane Tourist"
    }
    
    role = matrix.get((l_idx, g_idx, s_idx), "Versatile Rider")
    if m['volatility'] > 15: role = f"Erratic {role}"
    return role