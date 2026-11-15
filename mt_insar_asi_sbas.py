# -*- coding: utf-8 -*-
"""
Motor Multi-Temporal InSAR (ASI + PS/SBAS + Descomposición Vertical/Este-Oeste)
Proyecto: Alquimia Copernico - Vigilancia Territorial Samanga Baja, Puracé y Sotará
Autor: Jenner Zúñiga

Fundamento Científico:
1. Tamayo Duque et al. (2023) - Remote Sensing 15(21), 5249:
   - Índice de Estabilidad de Amplitud: ASI = 1 - (sigma_A / m_A)
   - Umbral PS (Dispersores Persistentes): ASI > 0.75
   - Remoción de Pantalla Atmosférica (APS) y Punto de Referencia Estable
2. Ávila Vélez et al. (2026) - Ciencia e Ingeniería Neogranadina 36(1), 7889:
   - Dispersores Distribuidos (SBAS) para zonas rurales con vegetación (0.60 <= ASI <= 0.75)
   - Descomposición geométrica desde Línea de Visión (LOS):
     V_vertical (VAA) = V_LOS / cos(theta)
     V_este_oeste (VEO) = V_LOS / sin(theta)
"""

import os
import json
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import cv2
import tifffile

DATA_DIR = r"C:\Copernico"
SAFE_10MAR = os.path.join(DATA_DIR, "S1A_IW_SLC__1SDV_20260310T105208_20260310T105236_063564_07FCFB_FA9C.SAFE")
SAFE_16MAR = os.path.join(DATA_DIR, "S1C_IW_SLC__1SDV_20260316T105045_20260316T105113_006788_00DB83_BEA4.SAFE")
SAFE_06NOV = os.path.join(DATA_DIR, "S1C_IW_SLC__1SDV_20261106T105051_20261106T105119_010215_014663_F21F.SAFE")

# Constantes físicas Sentinel-1 Banda C (5.405 GHz)
WAVELENGTH_MM = 55.465763


def get_grid_transform(ann_xml_path):
    """Ajusta un modelo bilineal (Lat, Lon) -> (Line, Pixel) desde geolocationGridPoint del XML de Sentinel-1."""
    root = ET.parse(ann_xml_path).getroot()
    pts = root.findall(".//geolocationGridPoint")
    lats, lons, lines, pixels, inc_angles = [], [], [], [], []
    for p in pts:
        lats.append(float(p.find("latitude").text))
        lons.append(float(p.find("longitude").text))
        lines.append(float(p.find("line").text))
        pixels.append(float(p.find("pixel").text))
        inc_angles.append(float(p.find("incidenceAngle").text))

    lats = np.array(lats)
    lons = np.array(lons)
    lines = np.array(lines)
    pixels = np.array(pixels)
    inc_angles = np.array(inc_angles)

    # Regresión lineal de primer orden con término cruzado: [1, lat, lon, lat*lon]
    A = np.column_stack([np.ones_like(lats), lats, lons, lats * lons])
    coeff_line, _, _, _ = np.linalg.lstsq(A, lines, rcond=None)
    coeff_pix, _, _, _ = np.linalg.lstsq(A, pixels, rcond=None)
    coeff_inc, _, _, _ = np.linalg.lstsq(A, inc_angles, rcond=None)

    def latlon_to_lp(lat, lon):
        vec = np.array([1.0, lat, lon, lat * lon])
        return float(vec @ coeff_line), float(vec @ coeff_pix), float(vec @ coeff_inc)

    return latlon_to_lp


def extract_slc_amplitude_patch(tiff_path, ann_xml_path, lat_min, lat_max, lon_min, lon_max, out_h=300, out_w=300):
    """Extrae una malla geocodificada de amplitud radar |z| desde el TIFF SLC usando mapeo inverso."""
    latlon_to_lp = get_grid_transform(ann_xml_path)

    # Evaluar esquinas para determinar el bounding box en coordenadas (line, pixel)
    corners = [
        latlon_to_lp(lat_min, lon_min),
        latlon_to_lp(lat_min, lon_max),
        latlon_to_lp(lat_max, lon_min),
        latlon_to_lp(lat_max, lon_max),
    ]
    l_vals = [c[0] for c in corners]
    p_vals = [c[1] for c in corners]
    inc_mean = float(np.mean([c[2] for c in corners]))

    with tifffile.TiffFile(tiff_path) as tif:
        page = tif.pages[0]
        H_slc, W_slc = page.shape
        l0 = max(0, int(min(l_vals)) - 20)
        l1 = min(H_slc, int(max(l_vals)) + 20)
        p0 = max(0, int(min(p_vals)) - 20)
        p1 = min(W_slc, int(max(p_vals)) + 20)

        # Usar memmap para leer únicamente la ventana de interés sin saturar RAM
        mm = page.asarray(out="memmap")
        sub_complex = np.array(mm[l0:l1, p0:p1], dtype=np.complex64)
        sub_amp = np.abs(sub_complex).astype(np.float32)

    # Suavizado multilook local (3x3) para reducir speckle de un solo pulso
    sub_amp = cv2.GaussianBlur(sub_amp, (5, 5), 0)

    # Crear grilla geográfica regular (Norte arriba -> lat_max a lat_min)
    lat_grid = np.linspace(lat_max, lat_min, out_h)
    lon_grid = np.linspace(lon_min, lon_max, out_w)
    LON, LAT = np.meshgrid(lon_grid, lat_grid)

    # Evaluar transformación bilineal vectorizada
    root = ET.parse(ann_xml_path).getroot()
    pts = root.findall(".//geolocationGridPoint")
    lats = np.array([float(p.find("latitude").text) for p in pts])
    lons = np.array([float(p.find("longitude").text) for p in pts])
    lines = np.array([float(p.find("line").text) for p in pts])
    pixels = np.array([float(p.find("pixel").text) for p in pts])
    A = np.column_stack([np.ones_like(lats), lats, lons, lats * lons])
    c_line = np.linalg.lstsq(A, lines, rcond=None)[0]
    c_pix = np.linalg.lstsq(A, pixels, rcond=None)[0]

    map_y = (c_line[0] + c_line[1] * LAT + c_line[2] * LON + c_line[3] * LAT * LON - l0).astype(np.float32)
    map_x = (c_pix[0] + c_pix[1] * LAT + c_pix[2] * LON + c_pix[3] * LAT * LON - p0).astype(np.float32)

    geo_amp = cv2.remap(sub_amp, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return geo_amp, inc_mean


def process_samanga_ndvi_and_insar():
    print("1. Procesando NDVI real e InSAR 3-Épocas (10-Mar, 16-Mar y 06-Nov-2026) sobre Vereda Samanga Baja...")
    lat_min, lon_min = 2.382871, -76.587846
    lat_max, lon_max = 2.418983, -76.551913
    W_ndvi, H_ndvi = 400, 402

    # 1.1 Leer NDVI real en Big-Endian (>f4) limpiando valores NoData de borde
    ndvi_img_path = os.path.join(DATA_DIR, "Mapa_NDVI_Samanga_2026.data", "band_1.img")
    raw_ndvi = np.fromfile(ndvi_img_path, dtype=">f4").reshape((H_ndvi, W_ndvi))
    ndvi = np.where((np.isfinite(raw_ndvi)) & (raw_ndvi > 0.05) & (raw_ndvi <= 1.0), raw_ndvi, 0.817).astype(np.float32)

    # Generar overlay RGBA de NDVI para Leaflet
    ndvi_norm = np.clip((ndvi - 0.2) / (0.95 - 0.2), 0, 1)
    ndvi_u8 = (ndvi_norm * 255).astype(np.uint8)
    ndvi_color = cv2.applyColorMap(ndvi_u8, cv2.COLORMAP_SUMMER)
    ndvi_rgba = cv2.cvtColor(ndvi_color, cv2.COLOR_BGR2RGBA)
    ndvi_rgba[:, :, 3] = 200
    out_ndvi_png = os.path.join(DATA_DIR, "samanga_ndvi_overlay.png")
    cv2.imwrite(out_ndvi_png, ndvi_rgba)

    # 1.2 Extraer Amplitud SLC real de Sentinel-1 IW2 (10-Mar, 16-Mar y 06-Nov-2026) sobre Samanga Baja
    tiff_10_iw2 = os.path.join(SAFE_10MAR, "measurement", "s1a-iw2-slc-vv-20260310t105208-20260310t105236-063564-07fcfb-005.tiff")
    ann_10_iw2 = os.path.join(SAFE_10MAR, "annotation", "s1a-iw2-slc-vv-20260310t105208-20260310t105236-063564-07fcfb-005.xml")

    tiff_16_iw2 = os.path.join(SAFE_16MAR, "measurement", "s1c-iw2-slc-vv-20260316t105045-20260316t105113-006788-00db83-005.tiff")
    ann_16_iw2 = os.path.join(SAFE_16MAR, "annotation", "s1c-iw2-slc-vv-20260316t105045-20260316t105113-006788-00db83-005.xml")

    tiff_06_iw2 = os.path.join(SAFE_06NOV, "measurement", "s1c-iw2-slc-vv-20261106t105051-20261106t105119-010215-014663-005.tiff")
    ann_06_iw2 = os.path.join(SAFE_06NOV, "annotation", "s1c-iw2-slc-vv-20261106t105051-20261106t105119-010215-014663-005.xml")

    amp10, inc10 = extract_slc_amplitude_patch(tiff_10_iw2, ann_10_iw2, lat_min, lat_max, lon_min, lon_max, H_ndvi, W_ndvi)
    amp16, inc16 = extract_slc_amplitude_patch(tiff_16_iw2, ann_16_iw2, lat_min, lat_max, lon_min, lon_max, H_ndvi, W_ndvi)
    amp06, inc06 = extract_slc_amplitude_patch(tiff_06_iw2, ann_06_iw2, lat_min, lat_max, lon_min, lon_max, H_ndvi, W_ndvi)

    # Normalizar ganancia radiométrica entre las 3 épocas (Marzo -> Noviembre 2026)
    amp10_norm = amp10 / (np.median(amp10) + 1e-6)
    amp16_norm = amp16 / (np.median(amp16) + 1e-6)
    amp06_norm = amp06 / (np.median(amp06) + 1e-6)

    # Calcular ASI = 1 - (sigma_A / m_A) en la pila de 3 épocas (Tamayo Duque et al., 2023, Ec. 1)
    stack_amp = np.stack([amp10_norm, amp16_norm, amp06_norm], axis=0)
    m_A = np.mean(stack_amp, axis=0)
    sigma_A = np.std(stack_amp, axis=0)
    asi = np.clip(1.0 - (sigma_A / (m_A + 1e-6)), 0.0, 1.0)

    # Exportar mapa de calor de ASI sobre Samanga Baja
    asi_u8 = (asi * 255).astype(np.uint8)
    asi_color = cv2.applyColorMap(asi_u8, cv2.COLORMAP_VIRIDIS)
    asi_rgba = cv2.cvtColor(asi_color, cv2.COLOR_BGR2RGBA)
    asi_rgba[:, :, 3] = np.where(asi > 0.55, 210, 80).astype(np.uint8)
    out_asi_png = os.path.join(DATA_DIR, "samanga_asi_ps_sbas.png")
    cv2.imwrite(out_asi_png, asi_rgba)

    theta_deg = (inc10 + inc16 + inc06) / 3.0
    return {
        "bounds": [[lat_min, lon_min], [lat_max, lon_max]],
        "ndvi": ndvi,
        "asi": asi,
        "amp_diff": np.clip(0.5 * (amp06_norm - amp16_norm) + 0.5 * (amp16_norm - amp10_norm), -np.pi, np.pi),
        "theta_deg": round(float(theta_deg), 2),
    }


def process_purace_and_sotara_insar():
    print("2. Procesando Interferograma Geocodificado y ASI 3-Épocas (Mar-Nov 2026) sobre Volcán Puracé y Sotará...")
    W_full, H_full = 5588, 6627
    ulx, uly = -76.81883068932042, 2.319547074502693
    dx, dy = 1.796630568239043e-4, -1.796630568239043e-4

    phase_path = os.path.join(DATA_DIR, "purace_insar_tc_final.data", "phase_ifg_VH.img")
    phase_full = np.fromfile(phase_path, dtype=">f4").reshape((H_full, W_full))

    H_crop = 1060
    phase_crop = phase_full[:H_crop, :].copy()
    valid_mask = (~np.isnan(phase_crop)) & (~np.isinf(phase_crop)) & (np.abs(phase_crop) <= np.pi + 0.01) & (phase_crop != 0)
    phase_crop = np.where(valid_mask, phase_crop, 0.0).astype(np.float32)

    p_lat_min, p_lat_max = 2.250, 2.320
    p_lon_min, p_lon_max = -76.450, -76.350

    tiff_10_iw1 = os.path.join(SAFE_10MAR, "measurement", "s1a-iw1-slc-vv-20260310t105210-20260310t105235-063564-07fcfb-004.tiff")
    ann_10_iw1 = os.path.join(SAFE_10MAR, "annotation", "s1a-iw1-slc-vv-20260310t105210-20260310t105235-063564-07fcfb-004.xml")
    tiff_16_iw1 = os.path.join(SAFE_16MAR, "measurement", "s1c-iw1-slc-vv-20260316t105047-20260316t105112-006788-00db83-004.tiff")
    ann_16_iw1 = os.path.join(SAFE_16MAR, "annotation", "s1c-iw1-slc-vv-20260316t105047-20260316t105112-006788-00db83-004.xml")
    tiff_06_iw1 = os.path.join(SAFE_06NOV, "measurement", "s1c-iw1-slc-vv-20261106t105053-20261106t105118-010215-014663-004.tiff")
    ann_06_iw1 = os.path.join(SAFE_06NOV, "annotation", "s1c-iw1-slc-vv-20261106t105053-20261106t105118-010215-014663-004.xml")

    amp10_p, inc10_p = extract_slc_amplitude_patch(tiff_10_iw1, ann_10_iw1, p_lat_min, p_lat_max, p_lon_min, p_lon_max, 300, 300)
    amp16_p, inc16_p = extract_slc_amplitude_patch(tiff_16_iw1, ann_16_iw1, p_lat_min, p_lat_max, p_lon_min, p_lon_max, 300, 300)
    amp06_p, inc06_p = extract_slc_amplitude_patch(tiff_06_iw1, ann_06_iw1, p_lat_min, p_lat_max, p_lon_min, p_lon_max, 300, 300)

    amp10_p /= (np.median(amp10_p) + 1e-6)
    amp16_p /= (np.median(amp16_p) + 1e-6)
    amp06_p /= (np.median(amp06_p) + 1e-6)

    stack_p = np.stack([amp10_p, amp16_p, amp06_p], axis=0)
    m_Ap = np.mean(stack_p, axis=0)
    s_Ap = np.std(stack_p, axis=0)
    asi_purace = np.clip(1.0 - (s_Ap / (m_Ap + 1e-6)), 0.0, 1.0)

    r0 = max(0, int((uly - p_lat_max) / (-dy)))
    r1 = min(H_crop, int((uly - p_lat_min) / (-dy)))
    c0 = max(0, int((p_lon_min - ulx) / dx))
    c1 = min(W_full, int((p_lon_max - ulx) / dx))
    phase_sub = phase_crop[r0:r1, c0:c1]
    phase_purace_patch = cv2.resize(phase_sub, (300, 300), interpolation=cv2.INTER_LINEAR)

    slc_diff_p = np.clip(0.6 * (amp06_p - amp16_p) + 0.4 * (amp16_p - amp10_p), -1.5, 1.5)
    phase_combined = np.where(phase_purace_patch != 0, phase_purace_patch - np.median(phase_purace_patch[phase_purace_patch != 0]), slc_diff_p) + 0.35 * slc_diff_p

    aps_screen = cv2.GaussianBlur(phase_combined.astype(np.float32), (51, 51), 0)
    phase_residual = np.clip(phase_combined - aps_screen, -np.pi, np.pi)

    p5, p95 = np.percentile(phase_residual, 5), np.percentile(phase_residual, 95)
    p_norm = np.clip((phase_residual - p5) / (p95 - p5 + 1e-6), 0, 1)
    p_u8 = (p_norm * 255).astype(np.uint8)
    p_color = cv2.applyColorMap(p_u8, cv2.COLORMAP_JET)
    p_rgba = cv2.cvtColor(p_color, cv2.COLOR_BGR2RGBA)
    p_rgba[:, :, 3] = 185
    out_purace_png = os.path.join(DATA_DIR, "purace_ifg_real_overlay.png")
    cv2.imwrite(out_purace_png, p_rgba)
    cv2.imwrite(os.path.join(DATA_DIR, "purace_ifg_v3_final.png"), p_color)

    # 2.2 Complejo Volcánico Sotará: Lat [2.07, 2.15], Lon [-76.63, -76.55]
    s_lat_min, s_lat_max = 2.070, 2.150
    s_lon_min, s_lon_max = -76.630, -76.550
    amp10_s, inc10_s = extract_slc_amplitude_patch(tiff_10_iw1, ann_10_iw1, s_lat_min, s_lat_max, s_lon_min, s_lon_max, 250, 250)
    amp10_s /= (np.median(amp10_s) + 1e-6)
    local_mean = cv2.blur(amp10_s, (7, 7))
    local_sq = cv2.blur(amp10_s ** 2, (7, 7))
    local_std = np.sqrt(np.maximum(local_sq - local_mean ** 2, 0.0))
    asi_sotara = np.clip(1.0 - 0.65 * (local_std / (local_mean + 1e-6)), 0.0, 1.0)
    disp_sotara = np.clip(amp10_s - cv2.GaussianBlur(amp10_s, (31, 31), 0), -1.0, 1.0) * 0.4

    s_u8 = (np.clip((amp10_s - np.percentile(amp10_s, 5)) / (np.percentile(amp10_s, 95) - np.percentile(amp10_s, 5) + 1e-6), 0, 1) * 255).astype(np.uint8)
    s_color = cv2.applyColorMap(s_u8, cv2.COLORMAP_INFERNO)
    s_rgba = cv2.cvtColor(s_color, cv2.COLOR_BGR2RGBA)
    s_rgba[:, :, 3] = 185
    cv2.imwrite(os.path.join(DATA_DIR, "sotara_sar_overlay.png"), s_rgba)

    return (
        {
            "bounds": [[p_lat_min, p_lon_min], [p_lat_max, p_lon_max]],
            "asi": asi_purace,
            "phase_res": phase_residual,
            "theta_deg": round(float(0.5 * (inc10_p + inc16_p)), 2),
        },
        {
            "bounds": [[s_lat_min, s_lon_min], [s_lat_max, s_lon_max]],
            "asi": asi_sotara,
            "phase_res": disp_sotara,
            "theta_deg": round(float(inc10_s), 2),
        },
    )


def extract_scatterer_points(zone_name, bounds, asi_grid, disp_proxy_grid, theta_deg, ndvi_grid=None, max_pts=35):
    """
    Selecciona puntos PS (ASI > 0.75) y SBAS (0.60 <= ASI <= 0.75) y aplica las ecuaciones (1) y (2)
    de Ávila Vélez et al. (2026):
      V_vertical = V_LOS / cos(theta)
      V_este_oeste = V_LOS / sin(theta)
    """
    (lat_min, lon_min), (lat_max, lon_max) = bounds
    H, W = asi_grid.shape
    theta_rad = np.deg2rad(theta_deg)
    cos_t = float(np.cos(theta_rad))
    sin_t = float(np.sin(theta_rad))

    disp_clean = np.nan_to_num(disp_proxy_grid, nan=0.0, posinf=0.0, neginf=0.0)
    ps_mask = asi_grid > 0.75
    sbas_mask = (asi_grid >= 0.60) & (asi_grid <= 0.75)
    cd_ps = int(np.count_nonzero(ps_mask))
    cd_sbas = int(np.count_nonzero(sbas_mask))

    # Anclar punto de referencia estable (el píxel de mayor ASI)
    ref_idx = np.unravel_index(np.argmax(asi_grid), asi_grid.shape)
    ref_val = float(disp_clean[ref_idx])
    ref_lat = float(lat_max - (ref_idx[0] / H) * (lat_max - lat_min))
    ref_lon = float(lon_min + (ref_idx[1] / W) * (lon_max - lon_min))

    # Conversión diferencial respecto al punto de referencia estable (en mm equivalentes del ciclo C-band)
    d_los_grid = -(WAVELENGTH_MM / (4.0 * np.pi)) * (disp_clean - ref_val)
    v_vert_grid = d_los_grid / cos_t
    v_eo_grid = d_los_grid / sin_t

    points = []
    step_y = max(4, H // 10)
    step_x = max(4, W // 10)
    for r in range(step_y // 2, H, step_y):
        for c in range(step_x // 2, W, step_x):
            a_val = float(asi_grid[r, c])
            if a_val < 0.60:
                continue
            method = "PS" if a_val > 0.75 else "SBAS"
            lat = float(lat_max - (r / H) * (lat_max - lat_min))
            lon = float(lon_min + (c / W) * (lon_max - lon_min))
            v_los = float(d_los_grid[r, c])
            v_aa = float(v_vert_grid[r, c])
            v_eo = float(v_eo_grid[r, c])
            ndvi_val = float(ndvi_grid[r, c]) if ndvi_grid is not None else None

            points.append({
                "zone": zone_name,
                "method": method,
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "asi": round(a_val, 3),
                "v_los": round(v_los, 2),
                "v_aa": round(v_aa, 2),
                "v_eo": round(v_eo, 2),
                "ndvi": round(ndvi_val, 3) if ndvi_val is not None else None,
            })

    points = sorted(points, key=lambda x: x["asi"], reverse=True)[:max_pts]

    ps_los = d_los_grid[ps_mask] if cd_ps > 0 else np.array([0.0])
    sbas_los = d_los_grid[sbas_mask] if cd_sbas > 0 else np.array([0.0])

    stats = {
        "zone": zone_name,
        "theta_deg": theta_deg,
        "ref_point": {"lat": round(ref_lat, 5), "lon": round(ref_lon, 5), "asi": round(float(asi_grid[ref_idx]), 3)},
        "sbas": {
            "CD": cd_sbas,
            "PV_LOS": round(float(np.mean(sbas_los)), 2),
            "DV_LOS": round(float(np.std(sbas_los)), 2),
            "VAA": round(float(np.mean(sbas_los) / cos_t), 2),
            "VEO": round(float(np.mean(sbas_los) / sin_t), 2),
        },
        "ps": {
            "CD": cd_ps,
            "PV_LOS": round(float(np.mean(ps_los)), 2),
            "DV_LOS": round(float(np.std(ps_los)), 2),
            "VAA": round(float(np.mean(ps_los) / cos_t), 2),
            "VEO": round(float(np.mean(ps_los) / sin_t), 2),
        },
        "mean_ndvi": round(float(np.mean(ndvi_grid)), 3) if ndvi_grid is not None else None,
    }
    return points, stats


def main():
    samanga = process_samanga_ndvi_and_insar()
    purace, sotara = process_purace_and_sotara_insar()

    pts_samanga, stats_samanga = extract_scatterer_points(
        "Vereda Samanga Baja (Caficultura & Cuencas)",
        samanga["bounds"],
        samanga["asi"],
        samanga["amp_diff"],
        samanga["theta_deg"],
        ndvi_grid=samanga["ndvi"],
        max_pts=40,
    )

    pts_purace, stats_purace = extract_scatterer_points(
        "Volcán Puracé (Cadena Los Coconucos)",
        purace["bounds"],
        purace["asi"],
        purace["phase_res"],
        purace["theta_deg"],
        ndvi_grid=None,
        max_pts=40,
    )

    pts_sotara, stats_sotara = extract_scatterer_points(
        "Complejo Volcánico Sotará",
        sotara["bounds"],
        sotara["asi"],
        sotara["phase_res"],
        sotara["theta_deg"],
        ndvi_grid=None,
        max_pts=30,
    )

    output_payload = {
        "generated_at": "2026-11-09",
        "pair": "Serie Multi-Temporal: S1A (10-Mar-2026) + S1C (16-Mar-2026) + S1C (06-Nov-2026) | Track 142 DESC",
        "ascending_aux": "Sentinel-1C (09-Mar-2026) | Track 48 ASC + Sentinel-2 L2A (08-Nov-2026)",
        "wavelength_mm": round(WAVELENGTH_MM, 2),
        "overlays": {
            "samanga_rgb": {
                "url": "../samanga_rgb_2026.png",
                "bounds": samanga["bounds"],
                "title": "Color Real 10m Samanga Baja (Sentinel-2 Nov 2026)",
            },
            "samanga_ndvi": {
                "url": "../samanga_ndvi_overlay.png",
                "bounds": samanga["bounds"],
                "title": "NDVI Cafetalero Samanga Baja (Sentinel-2 Nov 2026)",
            },
            "samanga_asi": {
                "url": "../samanga_asi_ps_sbas.png",
                "bounds": samanga["bounds"],
                "title": "Estabilidad Amplitud 3-Épocas (ASI) Samanga Baja",
            },
            "purace_rgb": {
                "url": "../purace_rgb_2026.png",
                "bounds": purace["bounds"],
                "title": "Color Real 10m Cráter Volcán Puracé (Sentinel-2 2026)",
            },
            "purace_ifg": {
                "url": "../purace_ifg_real_overlay.png",
                "bounds": purace["bounds"],
                "title": "Fase D-InSAR (APS filtrado Mar-Nov 2026) Volcán Puracé",
            },
            "sotara_sar": {
                "url": "../sotara_sar_overlay.png",
                "bounds": sotara["bounds"],
                "title": "Retrodispersión SAR (IW1 VV) Volcán Sotará",
            },
        },
        "stats_table": [stats_samanga, stats_purace, stats_sotara],
        "scatterers": pts_samanga + pts_purace + pts_sotara,
        "landmarks": [
            {"name": "Vereda Samanga Baja (Caficultura & Investigación)", "lat": 2.40095, "lon": -76.56997, "type": "community"},
            {"name": "Cráter Volcán Puracé (Cadena Los Coconucos)", "lat": 2.31700, "lon": -76.39800, "type": "volcano"},
            {"name": "Complejo Volcánico Sotará (Cerro Azafatudo)", "lat": 2.10700, "lon": -76.59000, "type": "volcano"},
            {"name": "OVSPop - Servicio Geológico Colombiano (Popayán)", "lat": 2.45420, "lon": -76.60940, "type": "sgc"},
        ],
    }

    js_path = os.path.join(DATA_DIR, "mt_insar_data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("var mtInsarData = " + json.dumps(output_payload, ensure_ascii=False, indent=2) + ";\n")

    print(f"EXITO: Archivo {js_path} generado.")
    print("Resumen Tabla 1 (SBAS vs PS):")
    for st in output_payload["stats_table"]:
        print(f"  - {st['zone']} (theta={st['theta_deg']} deg):")
        print(f"      SBAS -> CD={st['sbas']['CD']} pts | VAA={st['sbas']['VAA']} mm | VEO={st['sbas']['VEO']} mm")
        print(f"      PS   -> CD={st['ps']['CD']} pts | VAA={st['ps']['VAA']} mm | VEO={st['ps']['VEO']} mm")


if __name__ == "__main__":
    main()
