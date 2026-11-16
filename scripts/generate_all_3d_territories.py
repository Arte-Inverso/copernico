# -*- coding: utf-8 -*-
"""
Generador Maestro de Activos 3D Multi-Territorio:
1. Volcán Puracé (Cráter, Curiquinga, Cámara Mogi, Sismos VT)
2. Complejo Volcánico Sotará (Domo 4,405m, Retrodispersión SAR, Sismos)
3. Vereda Samanga Baja (Laderas Cafeteras, NDVI, Dispersores PS/SBAS, InSAR Desenrollado)
"""

import math
import requests
import json
import os
import cv2
import numpy as np

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

def fetch_tile_dem_and_optical(z, x, y):
    url_dem = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
    r_dem = requests.get(url_dem)
    arr_dem = np.frombuffer(r_dem.content, dtype=np.uint8)
    img_dem = cv2.imdecode(arr_dem, cv2.IMREAD_COLOR)
    B = img_dem[:, :, 0].astype(np.float32)
    G = img_dem[:, :, 1].astype(np.float32)
    R = img_dem[:, :, 2].astype(np.float32)
    elev = (R * 256.0 + G + B / 256.0) - 32768.0
    
    url_opt = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    r_opt = requests.get(url_opt)
    arr_opt = np.frombuffer(r_opt.content, dtype=np.uint8)
    img_opt = cv2.imdecode(arr_opt, cv2.IMREAD_COLOR)
    
    bounds = tile_bounds(z, x, y)
    return elev, img_opt, bounds

def save_both(filename, img):
    cv2.imwrite(os.path.join(OUT_DASHBOARD, filename), img)
    cv2.imwrite(os.path.join(OUT_DASHBOARD_REPO, filename), img)

def main():
    print("=" * 70)
    print("GENERANDO MODELOS 3D PARA PURACÉ, SOTARÁ Y SAMANGA BAJA")
    print("=" * 70)
    
    # Cargar Sismicidad SGC
    with open(os.path.join(DATA_DIR, "sgc_data.json"), "r", encoding="utf-8") as f:
        sgc_events = json.load(f)
        
    # Cargar Inversión Mogi
    with open(os.path.join(OUT_DASHBOARD, "geophysics_inversion_data.js"), "r", encoding="utf-8") as f:
        raw_inv = f.read().replace("var geophysicsInversionData = ", "").rstrip(";\n")
        inversion = json.loads(raw_inv)
    mogi = inversion["mogi_inversion"]
    
    # Cargar datos de dispersores PS/SBAS
    with open(os.path.join(OUT_DASHBOARD, "mt_insar_data.js"), "r", encoding="utf-8") as f:
        raw_mt = f.read().replace("var mtInsarData = ", "").rstrip(";\n")
        mt_data = json.loads(raw_mt)
        
    territories = {}
    
    # -------------------------------------------------------------
    # 1. VOLCÁN PURACÉ (z=12, x=1178, y=2021)
    # -------------------------------------------------------------
    print("\n[1/3] Procesando Volcán Puracé...")
    elev_p, opt_p, b_p = fetch_tile_dem_and_optical(12, 1178, 2021)
    save_both("purace_3d_texture_optical.jpg", opt_p)
    
    ifg_p = cv2.imread(os.path.join(OUT_DASHBOARD, "purace_ifg_real_overlay.png"), cv2.IMREAD_UNCHANGED)
    coh_p = cv2.imread(os.path.join(OUT_DASHBOARD, "purace_coh_real_overlay.png"), cv2.IMREAD_UNCHANGED)
    disp_p = cv2.imread(os.path.join(OUT_DASHBOARD, "purace_disp_los_unwrapped.png"), cv2.IMREAD_UNCHANGED)
    
    H, W = elev_p.shape
    if ifg_p is not None:
        ifg_p_res = cv2.resize(ifg_p, (W, H))
        a = ifg_p_res[:, :, 3:4] / 255.0
        save_both("purace_3d_texture_ifg.jpg", (ifg_p_res[:, :, :3] * a + opt_p * (1.0 - a)).astype(np.uint8))
    if coh_p is not None:
        coh_p_res = cv2.resize(coh_p, (W, H))
        a = coh_p_res[:, :, 3:4] / 255.0
        save_both("purace_3d_texture_coh.jpg", (coh_p_res[:, :, :3] * a + opt_p * (1.0 - a)).astype(np.uint8))
    if disp_p is not None:
        disp_p_res = cv2.resize(disp_p, (W, H))
        a = disp_p_res[:, :, 3:4] / 255.0
        save_both("purace_3d_texture_disp.jpg", (disp_p_res[:, :, :3] * a + opt_p * (1.0 - a)).astype(np.uint8))
        
    elev_p_128 = cv2.resize(elev_p, (128, 128), interpolation=cv2.INTER_AREA)
    
    territories["purace"] = {
        "id": "purace",
        "name": "Volcán Puracé",
        "subtitle": "Edificio Volcánico Activo & Cadena Los Coconucos",
        "bounds": {"lat_min": round(b_p[0], 5), "lat_max": round(b_p[1], 5), "lon_min": round(b_p[2], 5), "lon_max": round(b_p[3], 5)},
        "dem": {
            "width": 128, "height": 128,
            "elev_min": round(float(elev_p.min()), 1),
            "elev_max": round(float(elev_p.max()), 1),
            "elev_mean": round(float(elev_p.mean()), 1),
            "elevations": [[round(float(v), 1) for v in row] for row in elev_p_128]
        },
        "camera": {"x": 0, "y": 140, "z": 210, "target_y": 20},
        "textures": [
            {"id": "optical", "name": "🌍 Óptico (10m)", "file": "purace_3d_texture_optical.jpg"},
            {"id": "disp", "name": "📏 Deformación mm", "file": "purace_3d_texture_disp.jpg"},
            {"id": "ifg", "name": "💥 Fase D-InSAR", "file": "purace_3d_texture_ifg.jpg"},
            {"id": "coh", "name": "📶 Coherencia γ", "file": "purace_3d_texture_coh.jpg"}
        ],
        "magma_chamber": {
            "name": "Cámara Magmática Puracé (Mogi 1958)",
            "lat": mogi["source_lat"], "lon": mogi["source_lon"],
            "depth_km": mogi["depth_km"], "depth_m": mogi["depth_m"],
            "delta_v_mcm": mogi["delta_v_mcm"], "delta_v_m3": mogi["delta_v_m3"]
        },
        "landmarks": [
            {"name": "Cráter Activo Puracé", "lat": 2.317, "lon": -76.398, "elevation": 4643.0, "color": "#ef4444"},
            {"name": "Fumarolas Curiquinga", "lat": 2.324, "lon": -76.405, "elevation": 4380.0, "color": "#facc15"}
        ],
        "seismic_events": [
            {"lat": a.get("LATITUD"), "lon": a.get("LONGITUD"), "depth_km": a.get("PROFUNDIDAD"), "mag": a.get("MAGNITUD"), "lugar": a.get("LUGAR"), "fecha": a.get("FECHA_UTC")}
            for ev in sgc_events if (a := ev.get("attributes", {})) and "Puracé" in a.get("VOLCAN_ASOCIADO", "")
        ],
        "info": {
            "cota": "4,643 m s.n.m. (Borde del cráter)",
            "magma": "3.87 km prof. (ΔV: +1.21 × 10⁶ m³)",
            "dinamica": "Inflación magmático-hidrotermal asísmica (99.99%)",
            "metodo": "Mogi (1958) + InSAR SLC Banda C"
        }
    }
    
    # -------------------------------------------------------------
    # 2. VOLCÁN SOTARÁ (z=12, x=1176, y=2023)
    # -------------------------------------------------------------
    print("\n[2/3] Procesando Complejo Volcánico Sotará...")
    elev_s, opt_s, b_s = fetch_tile_dem_and_optical(12, 1176, 2023)
    save_both("sotara_3d_texture_optical.jpg", opt_s)
    
    # Textura SAR y Heatmap
    sar_s = cv2.imread(os.path.join(DATA_DIR, "sotara_sar_overlay.png"), cv2.IMREAD_UNCHANGED)
    if sar_s is not None:
        sar_s_res = cv2.resize(sar_s, (W, H))
        a = sar_s_res[:, :, 3:4] / 255.0
        save_both("sotara_3d_texture_sar.jpg", (sar_s_res[:, :, :3] * a + opt_s * (1.0 - a)).astype(np.uint8))
        
    elev_s_128 = cv2.resize(elev_s, (128, 128), interpolation=cv2.INTER_AREA)
    
    territories["sotara"] = {
        "id": "sotara",
        "name": "Complejo Volcánico Sotará",
        "subtitle": "Estratovolcán Andino & Domos Láviscos Paletará",
        "bounds": {"lat_min": round(b_s[0], 5), "lat_max": round(b_s[1], 5), "lon_min": round(b_s[2], 5), "lon_max": round(b_s[3], 5)},
        "dem": {
            "width": 128, "height": 128,
            "elev_min": round(float(elev_s.min()), 1),
            "elev_max": round(float(elev_s.max()), 1),
            "elev_mean": round(float(elev_s.mean()), 1),
            "elevations": [[round(float(v), 1) for v in row] for row in elev_s_128]
        },
        "camera": {"x": 0, "y": 130, "z": 200, "target_y": 18},
        "textures": [
            {"id": "optical", "name": "🌍 Óptico (10m)", "file": "sotara_3d_texture_optical.jpg"},
            {"id": "sar", "name": "⛰️ Retrodispersión SAR", "file": "sotara_3d_texture_sar.jpg"}
        ],
        "landmarks": [
            {"name": "Cúpula Volcánica Sotará", "lat": 2.110, "lon": -76.590, "elevation": 4405.0, "color": "#a855f7"},
            {"name": "Caldera de Paletará", "lat": 2.150, "lon": -76.620, "elevation": 3200.0, "color": "#38bdf8"}
        ],
        "seismic_events": [
            {"lat": a.get("LATITUD"), "lon": a.get("LONGITUD"), "depth_km": a.get("PROFUNDIDAD"), "mag": a.get("MAGNITUD"), "lugar": a.get("LUGAR"), "fecha": a.get("FECHA_UTC")}
            for ev in sgc_events if (a := ev.get("attributes", {})) and "Sotará" in a.get("VOLCAN_ASOCIADO", "")
        ],
        "info": {
            "cota": "4,405 m s.n.m. (Cúpula principal)",
            "magma": "Focos sismogénicos VT someros a 2.5–5 km",
            "dinamica": "Estabilidad relativa con actividad fumarólica residual",
            "metodo": "Retrodispersión SAR Calibrada Sentinel-1"
        }
    }
    
    # -------------------------------------------------------------
    # 3. VEREDA SAMANGA BAJA (z=12, x=1176, y=2020)
    # -------------------------------------------------------------
    print("\n[3/3] Procesando Vereda Samanga Baja (Caficultura & Laderas)...")
    elev_m, opt_m, b_m = fetch_tile_dem_and_optical(12, 1176, 2020)
    save_both("samanga_3d_texture_optical.jpg", opt_m)
    
    # Texturas NDVI y ASI
    ndvi_m = cv2.imread(os.path.join(DATA_DIR, "samanga_ndvi_overlay.png"), cv2.IMREAD_UNCHANGED)
    asi_m = cv2.imread(os.path.join(DATA_DIR, "samanga_asi_ps_sbas.png"), cv2.IMREAD_UNCHANGED)
    disp_m = cv2.imread(os.path.join(OUT_DASHBOARD, "samanga_disp_los_unwrapped.png"), cv2.IMREAD_UNCHANGED)
    
    if ndvi_m is not None:
        ndvi_m_res = cv2.resize(ndvi_m, (W, H))
        a = ndvi_m_res[:, :, 3:4] / 255.0
        save_both("samanga_3d_texture_ndvi.jpg", (ndvi_m_res[:, :, :3] * a + opt_m * (1.0 - a)).astype(np.uint8))
    if asi_m is not None:
        asi_m_res = cv2.resize(asi_m, (W, H))
        a = asi_m_res[:, :, 3:4] / 255.0
        save_both("samanga_3d_texture_asi.jpg", (asi_m_res[:, :, :3] * a + opt_m * (1.0 - a)).astype(np.uint8))
    if disp_m is not None:
        disp_m_res = cv2.resize(disp_m, (W, H))
        a = disp_m_res[:, :, 3:4] / 255.0
        save_both("samanga_3d_texture_disp.jpg", (disp_m_res[:, :, :3] * a + opt_m * (1.0 - a)).astype(np.uint8))
        
    elev_m_128 = cv2.resize(elev_m, (128, 128), interpolation=cv2.INTER_AREA)
    
    # Extraer dispersores PS y SBAS en Samanga
    samanga_scatterers = [
        pt for pt in mt_data.get("scatterers", [])
        if "Samanga" in pt.get("zone", "")
    ][:60]
    
    territories["samanga"] = {
        "id": "samanga",
        "name": "Vereda Samanga Baja",
        "subtitle": "Geodesia Rural, Caficultura & Dinámica de Laderas",
        "bounds": {"lat_min": round(b_m[0], 5), "lat_max": round(b_m[1], 5), "lon_min": round(b_m[2], 5), "lon_max": round(b_m[3], 5)},
        "dem": {
            "width": 128, "height": 128,
            "elev_min": round(float(elev_m.min()), 1),
            "elev_max": round(float(elev_m.max()), 1),
            "elev_mean": round(float(elev_m.mean()), 1),
            "elevations": [[round(float(v), 1) for v in row] for row in elev_m_128]
        },
        "camera": {"x": 0, "y": 100, "z": 180, "target_y": 12},
        "textures": [
            {"id": "optical", "name": "🌍 Óptico (10m)", "file": "samanga_3d_texture_optical.jpg"},
            {"id": "ndvi", "name": "🌿 NDVI Cafetalero", "file": "samanga_3d_texture_ndvi.jpg"},
            {"id": "asi", "name": "📡 Estabilidad ASI", "file": "samanga_3d_texture_asi.jpg"},
            {"id": "disp", "name": "📏 Deformación mm", "file": "samanga_3d_texture_disp.jpg"}
        ],
        "landmarks": [
            {"name": "Beneficiadero Central Samanga", "lat": 2.401, "lon": -76.570, "elevation": 1880.0, "color": "#00ff88"},
            {"name": "Anclaje APS Estable (Fase=0)", "lat": 2.395, "lon": -76.573, "elevation": 1820.0, "color": "#00d2ff"}
        ],
        "scatterers": samanga_scatterers,
        "info": {
            "cota": "1,645 – 2,439 m s.n.m. (Franja cafetera)",
            "ndvi": "Media: 0.817 (Bosque de galería & sombrío)",
            "dispersores": "78,231 PS (Vías/Techos) | 37,802 SBAS (Cultivos)",
            "metodo": "SBAS + PS (Ávila Vélez et al., 2026)"
        }
    }
    
    # Exportar archivo JS unificado
    out_js = f"var territories3DData = {json.dumps(territories, indent=2)};\n"
    with open(os.path.join(OUT_DASHBOARD, "territories_3d_data.js"), "w", encoding="utf-8") as f:
        f.write(out_js)
    with open(os.path.join(OUT_DASHBOARD_REPO, "territories_3d_data.js"), "w", encoding="utf-8") as f:
        f.write(out_js)
        
    print("\nTodos los territorios 3D procesados y exportados exitosamente a territories_3d_data.js!")

if __name__ == "__main__":
    main()
