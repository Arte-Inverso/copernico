# -*- coding: utf-8 -*-
"""
Motor InSAR Complejo Co-sísmico y Modelado Mogi (1958)
Procesamiento de los eventos sísmicos reales:
  1. Sismo Chocó (San José del Palmar) M 7.4 (10-Ago-2026):
     Par Sentinel-1: 08-Ago-2026 vs 14-Ago-2026 (dt = 6 días)
  2. Sismo Venezuela (Güiria / Paria) M 5.0 (02-Oct-2026):
     Par Sentinel-1: 01-Oct-2026 vs 07-Oct-2026 (dt = 6 días)
  3. Enjambre Sismos Tolima (Rioblanco M 5.4 / Chaparral M 4.5):
     Par Sentinel-1: 31-Oct-2026 vs 12-Nov-2026 (dt = 12 días) y vs 06-Nov-2026 (dt = 6 días)
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

DATA_EXTRACTED = r"C:\Copernico\data\sentinel1_extracted"
SAFE_06NOV_DIR = r"C:\Copernico\S1C_IW_SLC__1SDV_20261106T105051_20261106T105119_010215_014663_F21F.SAFE"
OUT_DASH_1 = r"C:\Copernico\dashboard"
OUT_DASH_2 = r"C:\Users\JENNER ZUÑIGA\copernico\dashboard"

WAVELENGTH_MM = 55.465763  # C-Band Sentinel-1 (5.405 GHz)
SHEAR_MODULUS_PA = 3.0e10  # 30 GPa
POISSON_RATIO = 0.25
PURACE_LAT = 2.318
PURACE_LON = -76.398
POVA_LAT = 2.378
POVA_LON = -76.495


def find_files_for_date(date_str, subswath="iw1"):
    """Busca los archivos .tiff y .xml para una fecha y sub-swath dados de forma ultrarrápida."""
    subswath = subswath.lower()
    
    if os.path.exists(DATA_EXTRACTED):
        for sdir in os.listdir(DATA_EXTRACTED):
            if date_str in sdir and sdir.endswith(".SAFE"):
                meas_dir = os.path.join(DATA_EXTRACTED, sdir, "measurement")
                ann_dir = os.path.join(DATA_EXTRACTED, sdir, "annotation")
                
                t_path, x_path = None, None
                if os.path.exists(meas_dir):
                    for f in os.listdir(meas_dir):
                        if subswath in f.lower() and "vv" in f.lower() and f.endswith(".tiff"):
                            t_path = os.path.join(meas_dir, f)
                            break
                            
                if os.path.exists(ann_dir):
                    for f in os.listdir(ann_dir):
                        if subswath in f.lower() and "vv" in f.lower() and f.endswith(".xml") and "calibration" not in f.lower() and "rfi" not in f.lower():
                            x_path = os.path.join(ann_dir, f)
                            break
                            
                if t_path and x_path:
                    return t_path, x_path
                    
    if date_str == "20261106" and os.path.exists(SAFE_06NOV_DIR):
        meas_dir = os.path.join(SAFE_06NOV_DIR, "measurement")
        ann_dir = os.path.join(SAFE_06NOV_DIR, "annotation")
        t_path, x_path = None, None
        if os.path.exists(meas_dir):
            for f in os.listdir(meas_dir):
                if subswath in f.lower() and "vv" in f.lower() and f.endswith(".tiff"):
                    t_path = os.path.join(meas_dir, f)
                    break
        if os.path.exists(ann_dir):
            for f in os.listdir(ann_dir):
                if subswath in f.lower() and "vv" in f.lower() and f.endswith(".xml") and "calibration" not in f.lower() and "rfi" not in f.lower():
                    x_path = os.path.join(ann_dir, f)
                    break
        if t_path and x_path:
            return t_path, x_path

    return None, None


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


def extract_complex_geocoded(tiff_path, c_line, c_pix, lat_min, lat_max, lon_min, lon_max, H=350, W=350):
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


def compute_interferogram_and_coherence(s1, s2, win_size=5):
    ifg = s1 * np.conj(s2)
    phase = np.angle(ifg)
    
    k = np.ones((win_size, win_size), dtype=np.float32) / float(win_size * win_size)
    cross = cv2.filter2D(ifg.real, -1, k) + 1j * cv2.filter2D(ifg.imag, -1, k)
    pwr1 = cv2.filter2D(np.abs(s1)**2, -1, k)
    pwr2 = cv2.filter2D(np.abs(s2)**2, -1, k)
    coh = np.abs(cross) / (np.sqrt(pwr1 * pwr2) + 1e-8)
    return ifg, phase, coh


def render_phase_rgba(phase, coh, coh_threshold=0.25):
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


def mogi_forward(delta_V, depth_m, r_m, inc_deg=35.0, heading_deg=-167.0, azim_grid=0.0):
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
    # Coordenadas radiales desde cráter Puracé
    dlat = (LAT - PURACE_LAT) * 110574.0
    dlon = (LON - PURACE_LON) * (111320.0 * np.cos(np.radians(PURACE_LAT)))
    r_m = np.sqrt(dlat**2 + dlon**2)
    azim_grid = np.arctan2(dlon, dlat)
    
    valid_mask = (coh > 0.35) & (r_m < 8000.0)
    if np.sum(valid_mask) < 50:
        valid_mask = (coh > 0.20) & (r_m < 9000.0)
        
    obs = disp_los_mm[valid_mask]
    r_sub = r_m[valid_mask]
    az_sub = azim_grid[valid_mask]
    
    def loss(params):
        dV_mcm, d_km = params
        pred = mogi_forward(dV_mcm * 1e6, d_km * 1000.0, r_sub, inc_deg=inc_mean, azim_grid=az_sub)
        return np.mean((obs - pred)**2)
    
    # Búsqueda inicial en grilla para anclar el régimen físico
    best_loss = 1e12
    best_init = [0.0, 2.0]
    for test_dV in [-3.0, -1.5, -0.5, 0.0, 0.5, 1.5, 3.0]:
        for test_d in [1.2, 2.0, 3.5, 5.0]:
            l_val = loss([test_dV, test_d])
            if l_val < best_loss:
                best_loss = l_val
                best_init = [test_dV, test_d]
                
    bounds = [(-10.0, 10.0), (0.6, 7.5)]
    res = minimize(loss, best_init, bounds=bounds, method="L-BFGS-B")
    best_dV = float(res.x[0] * 1e6)
    best_d = float(res.x[1] * 1000.0)
    pred_all = mogi_forward(best_dV, best_d, r_sub, inc_deg=inc_mean, azim_grid=az_sub)
    rmse = float(np.sqrt(np.mean((obs - pred_all)**2)))
    return best_dV, best_d, rmse


def process_coseismic_event(name, pre_date, post_date, dt_days, eq_info):
    print(f"\n{'='*70}\nPROCESANDO EVENTO CO-SÍSMICO: {name} (Δt = {dt_days} días)\n{'='*70}")
    
    # 1. Puracé (IW1)
    t_pre_1, x_pre_1 = find_files_for_date(pre_date, "iw1")
    t_post_1, x_post_1 = find_files_for_date(post_date, "iw1")
    
    if not t_pre_1 or not t_post_1:
        print(f"⚠️ Error: Faltan archivos TIFF/XML para IW1 en fechas {pre_date} / {post_date}")
        return None
        
    c_l_pre, c_p_pre, c_inc_pre = get_grid_transform(x_pre_1)
    c_l_post, c_p_post, c_inc_post = get_grid_transform(x_post_1)
    
    pur_lat_min, pur_lat_max = 2.270, 2.360
    pur_lon_min, pur_lon_max = -76.440, -76.350
    
    print(f"-> Extrayendo IW1 geocodificado para Puracé ({pre_date} vs {post_date})...")
    s_pre, lat_g, lon_g = extract_complex_geocoded(t_pre_1, c_l_pre, c_p_pre, pur_lat_min, pur_lat_max, pur_lon_min, pur_lon_max)
    s_post, _, _ = extract_complex_geocoded(t_post_1, c_l_post, c_p_post, pur_lat_min, pur_lat_max, pur_lon_min, pur_lon_max)
    
    ifg, phase, coh = compute_interferogram_and_coherence(s_post, s_pre, win_size=5)
    
    # Unwrapping 2D
    unwrapped = unwrap_phase(phase)
    # Anclaje de fase en esquina estable (referencia)
    ref_val = np.median(unwrapped[:15, :15])
    unwrapped_rel = unwrapped - ref_val
    # Desplazamiento LOS en mm (acercamiento al satélite = positivo)
    disp_los_mm = - (unwrapped_rel * (WAVELENGTH_MM / (4.0 * np.pi)))
    
    # Coherencia y estadísticas
    coh_mean = float(np.mean(coh))
    coh_max = float(np.max(coh))
    high_coh_px = int(np.count_nonzero(coh > 0.45))
    
    # Inversión Mogi
    mean_inc = float(np.mean(c_inc_post[0]))
    best_dV, best_d, mogi_rmse = invert_mogi(disp_los_mm, coh, lat_g, lon_g, mean_inc)
    
    # Desplazamiento en cráter Puracé
    dlat = (lat_g - PURACE_LAT) * 110574.0
    dlon = (lon_g - PURACE_LON) * (111320.0 * np.cos(np.radians(PURACE_LAT)))
    crater_mask = np.sqrt(dlat**2 + dlon**2) < 600.0
    crater_disp_mean = float(np.mean(disp_los_mm[crater_mask]))
    crater_disp_std = float(np.std(disp_los_mm[crater_mask]))
    
    print(f"  ✓ Coherencia Media Puracé: {coh_mean:.3f} (Píxeles coherentes >0.45: {high_coh_px:,})")
    print(f"  ✓ Desplazamiento Co-sísmico Cráter Puracé: {crater_disp_mean:+.2f} ± {crater_disp_std:.2f} mm")
    print(f"  ✓ Inversión Mogi: ΔV = {best_dV:+.0f} m³, Profundidad = {best_d:.0f} m (RMSE: {mogi_rmse:.2f} mm)")
    
    # Renderizar Overlays
    phase_rgba = render_phase_rgba(phase, coh, coh_threshold=0.22)
    coh_rgba = render_coherence_rgba(coh)
    
    prefix = name.lower().replace(" ", "_").replace("/", "_")
    for out_d in [OUT_DASH_1, OUT_DASH_2]:
        os.makedirs(out_d, exist_ok=True)
        cv2.imwrite(os.path.join(out_d, f"purace_ifg_{prefix}_overlay.png"), phase_rgba)
        cv2.imwrite(os.path.join(out_d, f"purace_coh_{prefix}_overlay.png"), coh_rgba)
        
    # 2. Samanga Baja (IW2)
    t_pre_2, x_pre_2 = find_files_for_date(pre_date, "iw2")
    t_post_2, x_post_2 = find_files_for_date(post_date, "iw2")
    sam_metrics = {}
    if t_pre_2 and t_post_2:
        c_l2_pre, c_p2_pre, _ = get_grid_transform(x_pre_2)
        c_l2_post, c_p2_post, _ = get_grid_transform(x_post_2)
        sam_lat_min, sam_lat_max = 2.380, 2.450
        sam_lon_min, sam_lon_max = -76.620, -76.540
        s2_pre, _, _ = extract_complex_geocoded(t_pre_2, c_l2_pre, c_p2_pre, sam_lat_min, sam_lat_max, sam_lon_min, sam_lon_max)
        s2_post, _, _ = extract_complex_geocoded(t_post_2, c_l2_post, c_p2_post, sam_lat_min, sam_lat_max, sam_lon_min, sam_lon_max)
        ifg_sam, phase_sam, coh_sam = compute_interferogram_and_coherence(s2_post, s2_pre, win_size=5)
        
        sam_phase_rgba = render_phase_rgba(phase_sam, coh_sam, coh_threshold=0.20)
        sam_coh_rgba = render_coherence_rgba(coh_sam)
        for out_d in [OUT_DASH_1, OUT_DASH_2]:
            cv2.imwrite(os.path.join(out_d, f"samanga_ifg_{prefix}_overlay.png"), sam_phase_rgba)
            cv2.imwrite(os.path.join(out_d, f"samanga_coh_{prefix}_overlay.png"), sam_coh_rgba)
            
        sam_metrics = {
            "coherence_mean": float(np.mean(coh_sam)),
            "high_coherence_pixels": int(np.count_nonzero(coh_sam > 0.45))
        }

    return {
        "event_name": name,
        "earthquake_info": eq_info,
        "pre_date": pre_date,
        "post_date": post_date,
        "dt_days": dt_days,
        "purace": {
            "coherence_mean": coh_mean,
            "coherence_max": coh_max,
            "high_coherence_pixels": high_coh_px,
            "crater_displacement_los_mm": crater_disp_mean,
            "crater_displacement_std_mm": crater_disp_std,
            "mogi_delta_v_m3": best_dV,
            "mogi_depth_m": best_d,
            "mogi_rmse_mm": mogi_rmse
        },
        "samanga": sam_metrics
    }


def main():
    events = [
        {
            "name": "Choco_M74",
            "pre_date": "20260808",
            "post_date": "20260814",
            "dt_days": 6,
            "eq_info": {
                "magnitude": 7.4,
                "date": "2026-08-10",
                "location": "San José del Palmar, Chocó",
                "depth_km": 116.0,
                "distance_purace_km": 293.0
            }
        },
        {
            "name": "Venezuela_M50",
            "pre_date": "20261001",
            "post_date": "20261007",
            "dt_days": 6,
            "eq_info": {
                "magnitude": 5.0,
                "date": "2026-10-02",
                "location": "Güiria, Golfo de Paria, Venezuela",
                "depth_km": 10.0,
                "distance_purace_km": 1450.0
            }
        },
        {
            "name": "Rioblanco_Chaparral_M54",
            "pre_date": "20261031",
            "post_date": "20261112",
            "dt_days": 12,
            "eq_info": {
                "magnitude": 5.4,
                "date": "2026-11-03",
                "location": "Rioblanco / Chaparral, Tolima",
                "depth_km": 10.0,
                "distance_purace_km": 175.0
            }
        }
    ]
    
    results = []
    for ev in events:
        res = process_coseismic_event(ev["name"], ev["pre_date"], ev["post_date"], ev["dt_days"], ev["eq_info"])
        if res:
            results.append(res)
            
    summary_path_1 = os.path.join(OUT_DASH_1, "coseismic_insar_summary.json")
    summary_path_2 = os.path.join(OUT_DASH_2, "coseismic_insar_summary.json")
    
    with open(summary_path_1, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    with open(summary_path_2, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print("\n" + "="*70)
    print(f"✓ Resumen co-sísmico guardado exitosamente en:")
    print(f"  -> {summary_path_1}")
    print(f"  -> {summary_path_2}")
    print("="*70)


if __name__ == "__main__":
    main()
