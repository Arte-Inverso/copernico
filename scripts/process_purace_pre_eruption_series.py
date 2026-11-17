# -*- coding: utf-8 -*-
"""
process_purace_pre_eruption_series.py — Procesamiento InSAR y Serie Temporal de Inflación Pre-Erupción
====================================================================================================
Analiza la serie temporal de imágenes Sentinel-1 SLC (IW1 VV) sobre el Volcán Puracé:
1. Detecta todas las épocas disponibles en C:\\Copernico\\data\\sentinel1_pre_eruption.
2. Calcula interferogramas diferenciales complejos (D-InSAR) consecutivos y acumulados.
3. Desenrolla la fase 2D (algoritmo Herráez / skimage) con anclaje de fase cero estable.
4. Calcula el desplazamiento en línea de visión (LOS) sobre el cráter y flancos del volcán.
5. Ejecuta la inversión geomecánica de Fuente Mogi (1958) para cada época, estimando
   el volumen de magma acumulado (ΔV en m³) y la profundidad del reservorio activo.
6. Exporta la serie temporal cuantitativa y genera el reporte para el dashboard.
"""

import os
import sys
import glob
import json
import xml.etree.ElementTree as ET
import numpy as np
import cv2
import tifffile
from skimage.restoration import unwrap_phase
from scipy.optimize import minimize

DATA_DIR = r"C:\Copernico\data\sentinel1_pre_eruption"
OUT_DASH_1 = r"C:\Copernico\dashboard"
OUT_DASH_2 = r"C:\Users\JENNER ZUÑIGA\copernico\dashboard"

WAVELENGTH_MM = 55.465763  # C-Band Sentinel-1 (5.405 GHz)
POISSON_RATIO = 0.25
PURACE_LAT = 2.318
PURACE_LON = -76.398


def scan_available_epochs(data_dir=DATA_DIR):
    """Escanea las carpetas SAFE disponibles en data_dir y extrae fechas y rutas."""
    epochs = []
    if not os.path.exists(data_dir):
        return epochs
        
    for item in os.listdir(data_dir):
        full_p = os.path.join(data_dir, item)
        if os.path.isdir(full_p) and item.endswith(".SAFE"):
            # Buscar TIFF y XML de IW1 VV
            meas_dir = os.path.join(full_p, "measurement")
            ann_dir = os.path.join(full_p, "annotation")
            
            t_path, x_path = None, None
            if os.path.exists(meas_dir):
                for f in os.listdir(meas_dir):
                    if "iw1" in f.lower() and "vv" in f.lower() and f.endswith(".tiff"):
                        t_path = os.path.join(meas_dir, f)
                        break
                        
            if os.path.exists(ann_dir):
                for f in os.listdir(ann_dir):
                    if "iw1" in f.lower() and "vv" in f.lower() and f.endswith(".xml") and "calibration" not in f.lower() and "rfi" not in f.lower():
                        x_path = os.path.join(ann_dir, f)
                        break
                        
            if t_path and x_path:
                # Extraer fecha de la cadena
                # Formato: S1A_IW_SLC__1SDV_YYYYMMDDTHHMMSS...
                parts = item.split("_")
                date_str = ""
                for part in parts:
                    if len(part) == 15 and "T" in part and part[:4].isdigit():
                        date_str = part[:8]
                        break
                if not date_str:
                    date_str = item[17:25]
                    
                epochs.append({
                    "date": date_str,
                    "date_formatted": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}",
                    "safe_dir": item,
                    "tiff_path": t_path,
                    "xml_path": x_path
                })
                
    epochs.sort(key=lambda x: x["date"])
    return epochs


def get_grid_transform(ann_xml_path):
    root = ET.parse(ann_xml_path).getroot()
    pts = root.findall(".//geolocationGridPoint")
    lats = np.array([float(p.find("latitude").text) for p in pts])
    lons = np.array([float(p.find("longitude").text) for p in pts])
    lines = np.array([float(p.find("line").text) for p in pts])
    pixels = np.array([float(p.find("pixel").text) for p in pts])
    inc_angles = np.array([float(p.find("incidenceAngle").text) for p in pts])
    
    A = np.column_stack([np.ones_like(lats), lats, lons, lats * lons])
    c_line = np.linalg.lstsq(A, lines, rcond=None)[0]
    c_pix = np.linalg.lstsq(A, pixels, rcond=None)[0]
    c_inc = np.linalg.lstsq(A, inc_angles, rcond=None)[0]
    return c_line, c_pix, c_inc


def extract_complex_geocoded(tiff_path, c_line, c_pix, lat_min=2.270, lat_max=2.360, lon_min=-76.440, lon_max=-76.350, H=350, W=350):
    lat_grid = np.linspace(lat_max, lat_min, H)
    lon_grid = np.linspace(lon_min, lon_max, W)
    LON, LAT = np.meshgrid(lon_grid, lat_grid)
    
    L_grid = c_line[0] + c_line[1] * LAT + c_line[2] * LON + c_line[3] * LAT * LON
    P_grid = c_pix[0] + c_pix[1] * LAT + c_pix[2] * LON + c_pix[3] * LAT * LON
    
    l0, l1 = int(np.min(L_grid)) - 10, int(np.max(L_grid)) + 10
    p0, p1 = int(np.min(P_grid)) - 10, int(np.max(P_grid)) + 10
    
    with tifffile.TiffFile(tiff_path) as tif:
        page = tif.pages[0]
        H_slc, W_slc = page.shape
        l0 = max(0, min(l0, H_slc - 1))
        l1 = max(0, min(l1, H_slc))
        p0 = max(0, min(p0, W_slc - 1))
        p1 = max(0, min(p1, W_slc))
        mm = page.asarray(out="memmap")
        patch = np.array(mm[l0:l1, p0:p1], dtype=np.complex64)
        
    map_y = (L_grid - l0).astype(np.float32)
    map_x = (P_grid - p0).astype(np.float32)
    
    re = cv2.remap(patch.real, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    im = cv2.remap(patch.imag, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return re + 1j * im, LAT, LON


def compute_interferogram(s1, s2, win_size=5):
    ifg = s1 * np.conj(s2)
    phase = np.angle(ifg)
    k = np.ones((win_size, win_size), dtype=np.float32) / float(win_size * win_size)
    cross = cv2.filter2D(ifg.real, -1, k) + 1j * cv2.filter2D(ifg.imag, -1, k)
    pwr1 = cv2.filter2D(np.abs(s1)**2, -1, k)
    pwr2 = cv2.filter2D(np.abs(s2)**2, -1, k)
    coh = np.abs(cross) / (np.sqrt(pwr1 * pwr2) + 1e-8)
    return ifg, phase, coh


def mogi_forward(dV_mcm, d_km, r_m, inc_deg=35.0, heading_deg=-167.0, azim_grid=0.0):
    delta_V = dV_mcm * 1e6
    depth_m = d_km * 1000.0
    inc_rad = np.radians(inc_deg)
    head_rad = np.radians(heading_deg)
    az_los = head_rad - np.pi / 2.0
    
    C = ((1.0 - POISSON_RATIO) / np.pi) * delta_V
    denom = (r_m**2 + depth_m**2)**(1.5)
    
    u_z = C * depth_m / (denom + 1e-6)
    u_r = C * r_m / (denom + 1e-6)
    u_x = u_r * np.sin(azim_grid)
    u_y = u_r * np.cos(azim_grid)
    
    u_los_m = (u_z * np.cos(inc_rad)
               - u_x * np.sin(inc_rad) * np.sin(az_los)
               - u_y * np.sin(inc_rad) * np.cos(az_los))
    return u_los_m * 1000.0  # mm


def invert_mogi(disp_los_mm, coh, LAT, LON, inc_mean=35.0):
    dlat = (LAT - PURACE_LAT) * 110574.0
    dlon = (LON - PURACE_LON) * (111320.0 * np.cos(np.radians(PURACE_LAT)))
    r_m = np.sqrt(dlat**2 + dlon**2)
    azim_grid = np.arctan2(dlon, dlat)
    
    valid_mask = (coh > 0.30) & (r_m < 7500.0)
    if np.sum(valid_mask) < 50:
        valid_mask = (coh > 0.18) & (r_m < 8500.0)
        
    obs = disp_los_mm[valid_mask]
    r_sub = r_m[valid_mask]
    az_sub = azim_grid[valid_mask]
    
    def loss(p):
        pred = mogi_forward(p[0], p[1], r_sub, inc_deg=inc_mean, azim_grid=az_sub)
        return np.mean((obs - pred)**2)
        
    best_loss = 1e12
    best_init = [0.0, 2.0]
    for test_dV in [-3.0, -1.0, 0.0, 1.0, 3.0]:
        for test_d in [1.5, 2.5, 4.0]:
            l_val = loss([test_dV, test_d])
            if l_val < best_loss:
                best_loss = l_val
                best_init = [test_dV, test_d]
                
    bounds = [(-15.0, 15.0), (0.6, 7.5)]
    res = minimize(loss, best_init, bounds=bounds, method="L-BFGS-B")
    best_dV_m3 = float(res.x[0] * 1e6)
    best_d_m = float(res.x[1] * 1000.0)
    pred_all = mogi_forward(res.x[0], res.x[1], r_sub, inc_deg=inc_mean, azim_grid=az_sub)
    rmse = float(np.sqrt(np.mean((obs - pred_all)**2)))
    return best_dV_m3, best_d_m, rmse


def render_phase_rgba(phase, coh, coh_threshold=0.22):
    p_norm = (phase + np.pi) / (2.0 * np.pi)
    p_u8 = (np.clip(p_norm, 0, 1) * 255).astype(np.uint8)
    p_rgb = cv2.applyColorMap(p_u8, cv2.COLORMAP_JET)
    p_rgba = cv2.cvtColor(p_rgb, cv2.COLOR_BGR2RGBA)
    alpha = np.clip((coh - coh_threshold) / (0.8 - coh_threshold), 0.0, 1.0) * 210
    p_rgba[:, :, 3] = alpha.astype(np.uint8)
    return p_rgba


def render_coherence_rgba(coh):
    c_u8 = (np.clip(coh, 0, 1) * 255).astype(np.uint8)
    c_rgb = cv2.applyColorMap(c_u8, cv2.COLORMAP_VIRIDIS)
    c_rgba = cv2.cvtColor(c_rgb, cv2.COLOR_BGR2RGBA)
    c_rgba[:, :, 3] = np.where(coh > 0.2, 200, 60).astype(np.uint8)
    return c_rgba


def process_series():
    print("=" * 75)
    print("PROCESADOR InSAR MULTI-TEMPORAL — SERIE PRE-ERUPCIÓN VOLCÁN PURACÉ")
    print("=" * 75)
    
    epochs = scan_available_epochs()
    if len(epochs) < 2:
        print(f"⚠️ Se necesitan al menos 2 épocas en {DATA_DIR} para procesar interferogramas.")
        print(f"Épocas encontradas actualmente: {len(epochs)}")
        print("Ejecuta primero: python scripts/download_purace_pre_eruption.py --count 10")
        return
        
    print(f"✓ Épocas disponibles para análisis: {len(epochs)}")
    for ep in epochs:
        print(f"   • {ep['date_formatted']} | {ep['safe_dir']}")
        
    base_epoch = epochs[0]
    print(f"\nÉpoca base de referencia: {base_epoch['date_formatted']}")
    
    # Transformación base
    c_l_base, c_p_base, c_inc_base = get_grid_transform(base_epoch["xml_path"])
    s_base, lat_g, lon_g = extract_complex_geocoded(base_epoch["tiff_path"], c_l_base, c_p_base)
    
    # Coordenadas relativas cráter Puracé
    dlat = (lat_g - PURACE_LAT) * 110574.0
    dlon = (lon_g - PURACE_LON) * (111320.0 * np.cos(np.radians(PURACE_LAT)))
    crater_mask = np.sqrt(dlat**2 + dlon**2) < 600.0
    
    series_results = []
    
    for i in range(1, len(epochs)):
        curr = epochs[i]
        print(f"\n[{i}/{len(epochs)-1}] Procesando par acumulado: {base_epoch['date_formatted']} vs {curr['date_formatted']}...")
        
        c_l_curr, c_p_curr, c_inc_curr = get_grid_transform(curr["xml_path"])
        s_curr, _, _ = extract_complex_geocoded(curr["tiff_path"], c_l_curr, c_p_curr)
        
        ifg, phase, coh = compute_interferogram(s_curr, s_base, win_size=5)
        unwrapped = unwrap_phase(phase)
        
        # Anclaje de fase en esquina de roca estable
        ref_val = np.median(unwrapped[:15, :15])
        unwrapped_rel = unwrapped - ref_val
        disp_los_mm = - (unwrapped_rel * (WAVELENGTH_MM / (4.0 * np.pi)))
        
        # Desplazamiento cráter
        crater_disp = float(np.mean(disp_los_mm[crater_mask]))
        crater_std = float(np.std(disp_los_mm[crater_mask]))
        coh_mean = float(np.mean(coh))
        
        # Inversión Mogi
        mean_inc = float(np.mean(c_inc_curr[0]))
        best_dV, best_d, rmse = invert_mogi(disp_los_mm, coh, lat_g, lon_g, mean_inc)
        
        print(f"    ✓ Coherencia Media: {coh_mean:.3f}")
        print(f"    ✓ Desplazamiento Cráter (LOS): {crater_disp:+.2f} ± {crater_std:.2f} mm")
        print(f"    ✓ Inversión Mogi: ΔV = {best_dV/1e6:+.2f} MCM, Prof = {best_d:.0f} m (RMSE: {rmse:.1f} mm)")
        
        # Guardar overlays
        pair_prefix = f"purace_pre_{base_epoch['date']}_{curr['date']}"
        phase_rgba = render_phase_rgba(phase, coh)
        coh_rgba = render_coherence_rgba(coh)
        for od in [OUT_DASH_1, OUT_DASH_2]:
            os.makedirs(od, exist_ok=True)
            cv2.imwrite(os.path.join(od, f"{pair_prefix}_ifg.png"), phase_rgba)
            cv2.imwrite(os.path.join(od, f"{pair_prefix}_coh.png"), coh_rgba)
            
        series_results.append({
            "base_date": base_epoch["date_formatted"],
            "target_date": curr["date_formatted"],
            "days_elapsed": (np.datetime64(curr["date_formatted"]) - np.datetime64(base_epoch["date_formatted"])).astype(int),
            "coherence_mean": coh_mean,
            "crater_displacement_los_mm": crater_disp,
            "crater_displacement_std_mm": crater_std,
            "mogi_delta_v_mcm": best_dV / 1e6,
            "mogi_depth_m": best_d,
            "mogi_rmse_mm": rmse
        })
        
    out_json = {
        "base_epoch": base_epoch["date_formatted"],
        "num_epochs": len(epochs),
        "series": series_results
    }
    
    for od in [OUT_DASH_1, OUT_DASH_2]:
        out_f = os.path.join(od, "purace_pre_eruption_series.json")
        with open(out_f, "w", encoding="utf-8") as f:
            json.dump(out_json, f, indent=2, ensure_ascii=False)
            
    print("\n" + "=" * 75)
    print("✓ Serie temporal pre-eruptiva procesada exitosamente.")
    print(f"✓ Resultados guardados en: {os.path.join(OUT_DASH_1, 'purace_pre_eruption_series.json')}")
    print("=" * 75)


if __name__ == "__main__":
    process_series()
