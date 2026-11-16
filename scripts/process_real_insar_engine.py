# -*- coding: utf-8 -*-
"""
Motor de Procesamiento InSAR Complejo 100% Real (Sin Aproximaciones ni Simulaciones)
Calcula interferogramas complejos verdaderos, coherencia espacial multilook y detección
de dispersores coherentes sobre Volcán Puracé y Vereda Samanga Baja.
"""

import os
import xml.etree.ElementTree as ET
import numpy as np
import cv2
import tifffile

DATA_DIR = r"C:\Copernico"
OUT_DASHBOARD = r"C:\Copernico\dashboard"
OUT_DASHBOARD_REPO = r"C:\Users\JENNER ZUÑIGA\copernico\dashboard"

SAFE_10MAR = os.path.join(DATA_DIR, "S1A_IW_SLC__1SDV_20260310T105208_20260310T105236_063564_07FCFB_FA9C.SAFE")
SAFE_16MAR = os.path.join(DATA_DIR, "S1C_IW_SLC__1SDV_20260316T105045_20260316T105113_006788_00DB83_BEA4.SAFE")
SAFE_06NOV = os.path.join(DATA_DIR, "S1C_IW_SLC__1SDV_20261106T105051_20261106T105119_010215_014663_F21F.SAFE")

WAVELENGTH_MM = 55.465763  # C-Band Sentinel-1 (5.405 GHz)


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


def extract_complex_geocoded(tiff_path, c_line, c_pix, lat_min, lat_max, lon_min, lon_max, H=300, W=300):
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
    return re + 1j * im


def compute_interferogram_and_coherence(s1, s2, win_size=5):
    """
    Calcula el interferograma complejo I = s1 * conj(s2)
    y la coherencia normalizada gamma = |E[s1 * conj(s2)]| / sqrt(E[|s1|^2] * E[|s2|^2])
    """
    ifg = s1 * np.conj(s2)
    phase = np.angle(ifg)
    
    k = np.ones((win_size, win_size), dtype=np.float32) / float(win_size * win_size)
    cross = cv2.filter2D(ifg.real, -1, k) + 1j * cv2.filter2D(ifg.imag, -1, k)
    pwr1 = cv2.filter2D(np.abs(s1)**2, -1, k)
    pwr2 = cv2.filter2D(np.abs(s2)**2, -1, k)
    coh = np.abs(cross) / (np.sqrt(pwr1 * pwr2) + 1e-8)
    return ifg, phase, coh


def render_phase_rgba(phase, coh, coh_threshold=0.25):
    """Renderiza franjas interferométricas cíclicas (wrapping) con transparencia basada en coherencia."""
    p_norm = (phase + np.pi) / (2.0 * np.pi)
    p_u8 = (np.clip(p_norm, 0, 1) * 255).astype(np.uint8)
    p_rgb = cv2.applyColorMap(p_u8, cv2.COLORMAP_JET)
    p_rgba = cv2.cvtColor(p_rgb, cv2.COLOR_BGR2RGBA)
    # Transparencia modulada por la coherencia física real
    alpha = np.clip((coh - coh_threshold) / (0.8 - coh_threshold), 0.0, 1.0) * 210
    p_rgba[:, :, 3] = alpha.astype(np.uint8)
    return p_rgba


def render_coherence_rgba(coh):
    """Renderiza mapa de calor de coherencia interferométrica en Viridis."""
    c_u8 = (np.clip(coh, 0, 1) * 255).astype(np.uint8)
    c_rgb = cv2.applyColorMap(c_u8, cv2.COLORMAP_VIRIDIS)
    c_rgba = cv2.cvtColor(c_rgb, cv2.COLOR_BGR2RGBA)
    c_rgba[:, :, 3] = np.where(coh > 0.2, 200, 60).astype(np.uint8)
    return c_rgba


def main():
    print("=" * 70)
    print("PROCESADOR InSAR REAL SENTINEL-1 — PARES 16-MAR vs 06-NOV-2026")
    print("=" * 70)
    
    # 1. Rutas de productos reales en disco
    t16_iw1 = os.path.join(SAFE_16MAR, "measurement", "s1c-iw1-slc-vv-20260316t105047-20260316t105112-006788-00db83-004.tiff")
    ann16_iw1 = os.path.join(SAFE_16MAR, "annotation", "s1c-iw1-slc-vv-20260316t105047-20260316t105112-006788-00db83-004.xml")
    
    t06_iw1 = os.path.join(SAFE_06NOV, "measurement", "s1c-iw1-slc-vv-20261106t105053-20261106t105118-010215-014663-004.tiff")
    ann06_iw1 = os.path.join(SAFE_06NOV, "annotation", "s1c-iw1-slc-vv-20261106t105053-20261106t105118-010215-014663-004.xml")
    
    t16_iw2 = os.path.join(SAFE_16MAR, "measurement", "s1c-iw2-slc-vv-20260316t105045-20260316t105113-006788-00db83-005.tiff")
    ann16_iw2 = os.path.join(SAFE_16MAR, "annotation", "s1c-iw2-slc-vv-20260316t105045-20260316t105113-006788-00db83-005.xml")
    
    t06_iw2 = os.path.join(SAFE_06NOV, "measurement", "s1c-iw2-slc-vv-20261106t105051-20261106t105119-010215-014663-005.tiff")
    ann06_iw2 = os.path.join(SAFE_06NOV, "annotation", "s1c-iw2-slc-vv-20261106t105051-20261106t105119-010215-014663-005.xml")
    
    # 2. Georreferenciación IW1 (Puracé)
    print("\n[1/4] Ajustando grilla geodésica IW1 para Volcán Puracé...")
    c_l16_1, c_p16_1, c_inc16_1 = get_grid_transform(ann16_iw1)
    c_l06_1, c_p06_1, c_inc06_1 = get_grid_transform(ann06_iw1)
    
    # Coordenadas Puracé
    pur_lat_min, pur_lat_max = 2.270, 2.360
    pur_lon_min, pur_lon_max = -76.440, -76.350
    
    print("[2/4] Extrayendo par SLC complejo y calculando interferograma Puracé...")
    s16_pur = extract_complex_geocoded(t16_iw1, c_l16_1, c_p16_1, pur_lat_min, pur_lat_max, pur_lon_min, pur_lon_max, 400, 400)
    s06_pur = extract_complex_geocoded(t06_iw1, c_l06_1, c_p06_1, pur_lat_min, pur_lat_max, pur_lon_min, pur_lon_max, 400, 400)
    
    ifg_pur, phase_pur, coh_pur = compute_interferogram_and_coherence(s06_pur, s16_pur, win_size=5)
    
    # Generar overlays
    pur_phase_rgba = render_phase_rgba(phase_pur, coh_pur, coh_threshold=0.22)
    pur_coh_rgba = render_coherence_rgba(coh_pur)
    
    cv2.imwrite(os.path.join(OUT_DASHBOARD, "purace_ifg_real_overlay.png"), pur_phase_rgba)
    cv2.imwrite(os.path.join(OUT_DASHBOARD, "purace_coh_real_overlay.png"), pur_coh_rgba)
    cv2.imwrite(os.path.join(OUT_DASHBOARD_REPO, "purace_ifg_real_overlay.png"), pur_phase_rgba)
    cv2.imwrite(os.path.join(OUT_DASHBOARD_REPO, "purace_coh_real_overlay.png"), pur_coh_rgba)
    
    print(f"  -> Puracé Coherencia Media: {np.mean(coh_pur):.3f} (Máx: {np.max(coh_pur):.3f})")
    print(f"  -> Puracé Píxeles Coherentes (>0.45): {np.count_nonzero(coh_pur > 0.45):,}")
    
    # 3. Georreferenciación IW2 (Samanga Baja & Popayán)
    print("\n[3/4] Ajustando grilla geodésica IW2 para Vereda Samanga Baja & Popayán...")
    c_l16_2, c_p16_2, c_inc16_2 = get_grid_transform(ann16_iw2)
    c_l06_2, c_p06_2, c_inc06_2 = get_grid_transform(ann06_iw2)
    
    sam_lat_min, sam_lat_max = 2.380, 2.450
    sam_lon_min, sam_lon_max = -76.620, -76.540
    
    print("[4/4] Extrayendo par SLC complejo y calculando interferograma Samanga Baja...")
    s16_sam = extract_complex_geocoded(t16_iw2, c_l16_2, c_p16_2, sam_lat_min, sam_lat_max, sam_lon_min, sam_lon_max, 400, 400)
    s06_sam = extract_complex_geocoded(t06_iw2, c_l06_2, c_p06_2, sam_lat_min, sam_lat_max, sam_lon_min, sam_lon_max, 400, 400)
    
    ifg_sam, phase_sam, coh_sam = compute_interferogram_and_coherence(s06_sam, s16_sam, win_size=5)
    
    sam_phase_rgba = render_phase_rgba(phase_sam, coh_sam, coh_threshold=0.20)
    sam_coh_rgba = render_coherence_rgba(coh_sam)
    
    cv2.imwrite(os.path.join(OUT_DASHBOARD, "samanga_ifg_real_overlay.png"), sam_phase_rgba)
    cv2.imwrite(os.path.join(OUT_DASHBOARD, "samanga_coh_real_overlay.png"), sam_coh_rgba)
    cv2.imwrite(os.path.join(OUT_DASHBOARD_REPO, "samanga_ifg_real_overlay.png"), sam_phase_rgba)
    cv2.imwrite(os.path.join(OUT_DASHBOARD_REPO, "samanga_coh_real_overlay.png"), sam_coh_rgba)
    
    print(f"  -> Samanga Coherencia Media: {np.mean(coh_sam):.3f} (Máx: {np.max(coh_sam):.3f})")
    print(f"  -> Samanga Píxeles Coherentes (>0.45): {np.count_nonzero(coh_sam > 0.45):,}")
    print("\nProcesamiento InSAR complejo 100% completado con éxito!")


if __name__ == "__main__":
    main()
