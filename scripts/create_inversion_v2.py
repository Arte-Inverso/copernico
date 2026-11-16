import os

with open(r'C:\Users\JENNER ZUÑIGA\copernico\scripts\insar_mogi_seismic_inversion.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add POVA constants
pova_defs = """
# Coordenadas POVA (Popayán, IGAC GeoRED)
POVA_LAT = 2.378
POVA_LON = -76.495
"""
if 'POVA_LAT' not in code:
    code = code.replace('REF_LON_GNSS = -76.495', 'REF_LON_GNSS = -76.495\n' + pova_defs)

# 2. Add extract_insar_pixel_at_pova function
func_def = """
def extract_insar_pixel_at_pova(disp_mm, coh, LAT, LON):
    from geopy.distance import geodesic
    H, W = LAT.shape
    min_dist = float('inf')
    best_i, best_j = 0, 0
    for i in range(H):
        for j in range(W):
            d = geodesic((LAT[i, j], LON[i, j]), (POVA_LAT, POVA_LON)).km
            if d < min_dist:
                min_dist = d
                best_i, best_j = i, j
    return {
        "disp_mm": round(float(disp_mm[best_i, best_j]), 2),
        "coherence": round(float(coh[best_i, best_j]), 3),
        "distance_km": round(float(min_dist), 2),
        "pixel_coords": {"lat": round(float(LAT[best_i, best_j]), 4), "lon": round(float(LON[best_i, best_j]), 4)},
        "pixel_idx": {"row": int(best_i), "col": int(best_j)}
    }
"""
if 'def extract_insar_pixel_at_pova' not in code:
    code = code.replace('def unwrap_and_calibrate', func_def + '\ndef unwrap_and_calibrate')

# 3. Update Samanga bounding box to include POVA: lat [2.350, 2.450], lon [-76.620, -76.470] and size 400x500
code = code.replace('sam_lat_min, sam_lat_max = 2.380, 2.450', 'sam_lat_min, sam_lat_max = 2.350, 2.450')
code = code.replace('sam_lon_min, sam_lon_max = -76.620, -76.540', 'sam_lon_min, sam_lon_max = -76.620, -76.470')
code = code.replace('extract_complex_patch(t16_iw2, c_l16_2, c_p16_2, sam_lat_min, sam_lat_max, sam_lon_min, sam_lon_max, 350, 350)', 'extract_complex_patch(t16_iw2, c_l16_2, c_p16_2, sam_lat_min, sam_lat_max, sam_lon_min, sam_lon_max, 400, 500)')
code = code.replace('extract_complex_patch(t06_iw2, c_l06_2, c_p06_2, sam_lat_min, sam_lat_max, sam_lon_min, sam_lon_max, 350, 350)', 'extract_complex_patch(t06_iw2, c_l06_2, c_p06_2, sam_lat_min, sam_lat_max, sam_lon_min, sam_lon_max, 400, 500)')

# 4. Call extract_insar_pixel_at_pova and include in JSON
pova_call = """
    print("\\n[Paso 2.5] Extrayendo desplazamiento InSAR en el píxel más cercano a POVA...")
    pova_pixel = extract_insar_pixel_at_pova(disp_sam_los, coh_sam, LAT_sam, LON_sam)
    print(f"  -> Coordenadas Píxel POVA: Lat {pova_pixel['pixel_coords']['lat']} N, Lon {pova_pixel['pixel_coords']['lon']} W (Distancia a POVA: {pova_pixel['distance_km']} km)")
    print(f"  -> Desplazamiento LOS Píxel POVA: {pova_pixel['disp_mm']} mm (Coherencia gamma: {pova_pixel['coherence']})")
"""
if '[Paso 2.5]' not in code:
    code = code.replace('mogi_res = invert_mogi_source', pova_call + '\n    mogi_res = invert_mogi_source')

json_field = """        "samanga_disp_stats": {
            "min_mm": round(float(disp_sam_los.min()), 2),
            "max_mm": round(float(disp_sam_los.max()), 2),
            "mean_mm": round(float(disp_sam_los.mean()), 2),
            "std_mm": round(float(disp_sam_los.std()), 2),
        },
        "pova_validation": {
            "station_coords": {"lat": POVA_LAT, "lon": POVA_LON},
            "insar_pixel": pova_pixel,
            "period": {"start": "2026-03-16", "end": "2026-11-06", "days": 235},
            "method": "Extracción directa del píxel InSAR más cercano a POVA",
            "validation_ready": bool(pova_pixel["distance_km"] < 1.0)
        }"""
code = code.replace("""        "samanga_disp_stats": {
            "min_mm": round(float(disp_sam_los.min()), 2),
            "max_mm": round(float(disp_sam_los.max()), 2),
            "mean_mm": round(float(disp_sam_los.mean()), 2),
            "std_mm": round(float(disp_sam_los.std()), 2),
        }""", json_field)

with open(r'C:\Users\JENNER ZUÑIGA\copernico\scripts\insar_mogi_seismic_inversion_v2.py', 'w', encoding='utf-8') as out1:
    out1.write(code)
with open(r'C:\Copernico\scripts\insar_mogi_seismic_inversion_v2.py', 'w', encoding='utf-8') as out2:
    out2.write(code)

print("Created insar_mogi_seismic_inversion_v2.py successfully in both locations!")
