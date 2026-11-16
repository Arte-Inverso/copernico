import os

for path in [
    r'C:\Users\JENNER ZUÑIGA\copernico\scripts\insar_mogi_seismic_inversion_v2.py',
    r'C:\Copernico\scripts\insar_mogi_seismic_inversion_v2.py'
]:
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Define POVA_LAT and POVA_LON near constants
    if "POVA_LAT = 2.378" not in code:
        code = code.replace("POISSON_RATIO = 0.25", "POISSON_RATIO = 0.25\nPOVA_LAT = 2.378\nPOVA_LON = -76.495\n")

    # Vectorize extract_insar_pixel_at_pova for speed
    fast_func = """def extract_insar_pixel_at_pova(disp_mm, coh, LAT, LON):
    # Distancia geodésica aproximada ultrarrápida: 1 deg lat ~ 110.574 km, 1 deg lon ~ 111.320 * cos(lat)
    dlat = (LAT - POVA_LAT) * 110.574
    dlon = (LON - POVA_LON) * (111.320 * np.cos(np.radians(POVA_LAT)))
    dist_km_grid = np.sqrt(dlat**2 + dlon**2)
    min_idx = np.unravel_index(np.argmin(dist_km_grid), dist_km_grid.shape)
    best_i, best_j = min_idx
    min_dist = float(dist_km_grid[min_idx])
    return {
        "disp_mm": round(float(disp_mm[best_i, best_j]), 2),
        "coherence": round(float(coh[best_i, best_j]), 3),
        "distance_km": round(min_dist, 2),
        "pixel_coords": {"lat": round(float(LAT[best_i, best_j]), 4), "lon": round(float(LON[best_i, best_j]), 4)},
        "pixel_idx": {"row": int(best_i), "col": int(best_j)}
    }
"""
    # Replace existing extract_insar_pixel_at_pova
    import re
    code = re.sub(r'def extract_insar_pixel_at_pova[\s\S]*?return \{[\s\S]*?\}', fast_func.strip(), code)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

print("Updated and fixed insar_mogi_seismic_inversion_v2.py!")
