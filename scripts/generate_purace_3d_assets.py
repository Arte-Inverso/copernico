# -*- coding: utf-8 -*-
"""
Generador de Activos 3D para el Volcán Puracé
Descarga DEM real (AWS Terrarium / SRTM 30m), genera ortomosaicos alineados (óptico + InSAR)
y exporta la geometría tridimensional para renderizado WebGL (Three.js).
"""

import math
import requests
import json
import os
import cv2
import numpy as np
import tifffile

DATA_DIR = r"C:\Copernico"
OUT_DASHBOARD = r"C:\Copernico\dashboard"
OUT_DASHBOARD_REPO = r"C:\Users\JENNER ZUÑIGA\copernico\dashboard"

def tile_bounds(z, x, y):
    n = 2.0 ** z
    lon_w = (x / n) * 360.0 - 180.0
    lon_e = ((x + 1) / n) * 360.0 - 180.0
    lat_n = math.degrees(math.atan(math.sinh(math.pi * (1.0 - 2.0 * y / n))))
    lat_s = math.degrees(math.atan(math.sinh(math.pi * (1.0 - 2.0 * (y + 1) / n))))
    return lat_s, lat_n, lon_w, lon_e

def fetch_dem_and_optical():
    print("1. Descargando DEM real y mosaico óptico (Zoom 12)...")
    z = 12
    x = 1178
    y = 2021
    lat_s, lat_n, lon_w, lon_e = tile_bounds(z, x, y)
    
    # DEM Terrarium
    url_dem = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
    r_dem = requests.get(url_dem)
    arr_dem = np.frombuffer(r_dem.content, dtype=np.uint8)
    img_dem = cv2.imdecode(arr_dem, cv2.IMREAD_COLOR)
    B = img_dem[:, :, 0].astype(np.float32)
    G = img_dem[:, :, 1].astype(np.float32)
    R = img_dem[:, :, 2].astype(np.float32)
    elev = (R * 256.0 + G + B / 256.0) - 32768.0
    
    # Ortofoto Esri
    url_opt = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    r_opt = requests.get(url_opt)
    arr_opt = np.frombuffer(r_opt.content, dtype=np.uint8)
    img_opt = cv2.imdecode(arr_opt, cv2.IMREAD_COLOR)
    
    return elev, img_opt, (lat_s, lat_n, lon_w, lon_e)

def main():
    elev, img_opt, bounds = fetch_dem_and_optical()
    lat_s, lat_n, lon_w, lon_e = bounds
    H, W = elev.shape
    
    print(f"  -> Cobertura geográfica: Lat [{lat_s:.4f}, {lat_n:.4f}], Lon [{lon_w:.4f}, {lon_e:.4f}]")
    print(f"  -> Elevación Puracé: Mín={elev.min():.1f} m, Máx={elev.max():.1f} m, Media={elev.mean():.1f} m")
    
    # Guardar textura óptica
    cv2.imwrite(os.path.join(OUT_DASHBOARD, "purace_3d_texture_optical.jpg"), img_opt)
    cv2.imwrite(os.path.join(OUT_DASHBOARD_REPO, "purace_3d_texture_optical.jpg"), img_opt)
    
    # 2. Alinear y recortar las capas InSAR reales existentes (Fase, Coherencia, Desplazamiento métrico)
    print("2. Remapeando capas InSAR reales a la grilla DEM 3D...")
    
    # Leer capas generadas previamente
    ifg_rgba = cv2.imread(os.path.join(OUT_DASHBOARD, "purace_ifg_real_overlay.png"), cv2.IMREAD_UNCHANGED)
    coh_rgba = cv2.imread(os.path.join(OUT_DASHBOARD, "purace_coh_real_overlay.png"), cv2.IMREAD_UNCHANGED)
    disp_rgba = cv2.imread(os.path.join(OUT_DASHBOARD, "purace_disp_los_unwrapped.png"), cv2.IMREAD_UNCHANGED)
    
    # Redimensionar al tamaño del DEM (256x256)
    ifg_tex = cv2.resize(ifg_rgba, (W, H), interpolation=cv2.INTER_LINEAR)
    coh_tex = cv2.resize(coh_rgba, (W, H), interpolation=cv2.INTER_LINEAR)
    disp_tex = cv2.resize(disp_rgba, (W, H), interpolation=cv2.INTER_LINEAR)
    
    # Para textura sobre Three.js mesh, mezclar con mapa base para mejor apariencia visual
    alpha_ifg = ifg_tex[:, :, 3:4] / 255.0
    blend_ifg = (ifg_tex[:, :, :3] * alpha_ifg + img_opt * (1.0 - alpha_ifg)).astype(np.uint8)
    
    alpha_coh = coh_tex[:, :, 3:4] / 255.0
    blend_coh = (coh_tex[:, :, :3] * alpha_coh + img_opt * (1.0 - alpha_coh)).astype(np.uint8)
    
    alpha_disp = disp_tex[:, :, 3:4] / 255.0
    blend_disp = (disp_tex[:, :, :3] * alpha_disp + img_opt * (1.0 - alpha_disp)).astype(np.uint8)
    
    cv2.imwrite(os.path.join(OUT_DASHBOARD, "purace_3d_texture_ifg.jpg"), blend_ifg)
    cv2.imwrite(os.path.join(OUT_DASHBOARD, "purace_3d_texture_coh.jpg"), blend_coh)
    cv2.imwrite(os.path.join(OUT_DASHBOARD, "purace_3d_texture_disp.jpg"), blend_disp)
    
    cv2.imwrite(os.path.join(OUT_DASHBOARD_REPO, "purace_3d_texture_ifg.jpg"), blend_ifg)
    cv2.imwrite(os.path.join(OUT_DASHBOARD_REPO, "purace_3d_texture_coh.jpg"), blend_coh)
    cv2.imwrite(os.path.join(OUT_DASHBOARD_REPO, "purace_3d_texture_disp.jpg"), blend_disp)
    
    # 3. Cargar sismicidad y cámara magmática
    with open(os.path.join(DATA_DIR, "sgc_data.json"), "r", encoding="utf-8") as f:
        sgc_events = json.load(f)
        
    with open(os.path.join(OUT_DASHBOARD, "geophysics_inversion_data.js"), "r", encoding="utf-8") as f:
        raw_inv = f.read().replace("var geophysicsInversionData = ", "").rstrip(";\n")
        inversion = json.loads(raw_inv)
        
    mogi = inversion["mogi_inversion"]
    
    # Downsample suave a 128x128 para rendimiento Three.js fluido
    elev_128 = cv2.resize(elev, (128, 128), interpolation=cv2.INTER_AREA)
    
    purace_3d_dataset = {
        "bounds": {
            "lat_min": round(lat_s, 5),
            "lat_max": round(lat_n, 5),
            "lon_min": round(lon_w, 5),
            "lon_max": round(lon_e, 5),
        },
        "dem": {
            "width": 128,
            "height": 128,
            "elev_min": round(float(elev.min()), 1),
            "elev_max": round(float(elev.max()), 1),
            "elev_mean": round(float(elev.mean()), 1),
            "elevations": [[round(float(val), 1) for val in row] for row in elev_128]
        },
        "crater": {
            "name": "Cráter Activo Puracé",
            "lat": 2.317,
            "lon": -76.398,
            "elevation": 4643.0
        },
        "curiquinga": {
            "name": "Campo Fumarólico Curiquinga",
            "lat": 2.324,
            "lon": -76.405,
            "elevation": 4380.0
        },
        "gnss_pova": {
            "id": "POVA",
            "name": "Estación GNSS Continua GeoRED Puracé",
            "lat": 2.378,
            "lon": -76.495,
            "elevation": 3210.0
        },
        "magma_chamber": {
            "lat": mogi["source_lat"],
            "lon": mogi["source_lon"],
            "depth_km": mogi["depth_km"],
            "depth_m": mogi["depth_m"],
            "delta_v_mcm": mogi["delta_v_mcm"],
            "delta_v_m3": mogi["delta_v_m3"]
        },
        "seismic_events": []
    }
    
    # Procesar hipocentros sísmicos proyectados al volumen 3D
    for ev in sgc_events:
        a = ev.get("attributes", {})
        purace_3d_dataset["seismic_events"].append({
            "lat": a.get("LATITUD"),
            "lon": a.get("LONGITUD"),
            "depth_km": a.get("PROFUNDIDAD"),
            "mag": a.get("MAGNITUD"),
            "lugar": a.get("LUGAR"),
            "fecha": a.get("FECHA_UTC"),
            "rms": a.get("RMS_SEC")
        })
        
    js_content = f"var purace3DData = {json.dumps(purace_3d_dataset, indent=2)};\n"
    with open(os.path.join(OUT_DASHBOARD, "purace_3d_data.js"), "w", encoding="utf-8") as f:
        f.write(js_content)
    with open(os.path.join(OUT_DASHBOARD_REPO, "purace_3d_data.js"), "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print("3. Dataset 3D exportado exitosamente a purace_3d_data.js!")

if __name__ == "__main__":
    main()
