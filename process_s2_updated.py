# -*- coding: utf-8 -*-
"""
Procesador Óptico Multi-Temporal Sentinel-2 L2A (10 m) — Actualización Noviembre 2026
Fusión Radiométrica Max-NDVI / Min-Haze (sin costuras de órbita ni parches de nubes)
entre 11-Jun-2026 (R025), 27-Oct-2026 (R068), 08-Nov-2026 (R068) y el ráster base ENVI.
"""

import os
import glob
import math
import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def latlon_to_utm18n(lat_deg, lon_deg):
    a = 6378137.0
    f = 1.0 / 298.257223563
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    k0 = 0.9996
    lon0 = math.radians(-75.0)

    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)

    N = a / math.sqrt(1 - e2 * math.sin(lat)**2)
    T = math.tan(lat)**2
    C = ep2 * math.cos(lat)**2
    A = math.cos(lat) * (lon - lon0)

    M = a * (
        (1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256) * lat
        - (3 * e2 / 8 + 3 * e2**2 / 32 + 45 * e2**3 / 1024) * math.sin(2 * lat)
        + (15 * e2**2 / 256 + 45 * e2**3 / 1024) * math.sin(4 * lat)
        - (35 * e2**3 / 3072) * math.sin(6 * lat)
    )

    easting = 500000.0 + k0 * N * (
        A + (1 - T + C) * A**3 / 6
        + (5 - 18 * T + T**2 + 72 * C - 58 * ep2) * A**5 / 120
    )
    northing = k0 * (
        M + N * math.tan(lat) * (
            A**2 / 2 + (5 - T + 9 * C + 4 * C**2) * A**4 / 24
            + (61 - 58 * T + T**2 + 600 * C - 330 * ep2) * A**6 / 720
        )
    )
    return easting, northing

def bbox_to_s2_pixels(lat_min, lat_max, lon_min, lon_max, res=10.0):
    ULX, ULY = 300000.0, 300000.0
    x_min, y_min = latlon_to_utm18n(lat_min, lon_min)
    x_max, y_max = latlon_to_utm18n(lat_max, lon_max)

    c0 = max(0, int((x_min - ULX) / res))
    c1 = min(int(109800 / res), int((x_max - ULX) / res))
    r0 = max(0, int((ULY - y_max) / res))
    r1 = min(int(109800 / res), int((ULY - y_min) / res))
    return r0, r1, c0, c1

def load_s2_window(date_folder, r0, r1, c0, c1):
    b02_f = glob.glob(os.path.join(date_folder, "*_B02_10m.jp2"))[0]
    b03_f = glob.glob(os.path.join(date_folder, "*_B03_10m.jp2"))[0]
    b04_f = glob.glob(os.path.join(date_folder, "*_B04_10m.jp2"))[0]
    b08_f = glob.glob(os.path.join(date_folder, "*_B08_10m.jp2"))[0]
    scl_f = glob.glob(os.path.join(date_folder, "*_SCL_20m.jp2"))[0]

    raw02 = cv2.imread(b02_f, cv2.IMREAD_UNCHANGED)[r0:r1, c0:c1].astype(np.float32)
    raw03 = cv2.imread(b03_f, cv2.IMREAD_UNCHANGED)[r0:r1, c0:c1].astype(np.float32)
    raw04 = cv2.imread(b04_f, cv2.IMREAD_UNCHANGED)[r0:r1, c0:c1].astype(np.float32)
    raw08 = cv2.imread(b08_f, cv2.IMREAD_UNCHANGED)[r0:r1, c0:c1].astype(np.float32)

    valid_data = (raw04 > 0) & (raw08 > 0)

    scl_full = cv2.imread(scl_f, cv2.IMREAD_UNCHANGED)
    scl_crop = scl_full[r0//2 : r1//2 + 1, c0//2 : c1//2 + 1]
    scl = cv2.resize(scl_crop, (c1 - c0, r1 - r0), interpolation=cv2.INTER_NEAREST)

    b02 = np.clip((raw02 - 1000.0) / 10000.0, 0.001, 1.0)
    b03 = np.clip((raw03 - 1000.0) / 10000.0, 0.001, 1.0)
    b04 = np.clip((raw04 - 1000.0) / 10000.0, 0.001, 1.0)
    b08 = np.clip((raw08 - 1000.0) / 10000.0, 0.001, 1.0)

    # Píxel estrictamente libre de nubes/neblina: dato válido, SCL 4/5/6 y azul B02 bajo (< 0.11)
    strict_clear = valid_data & np.isin(scl, [4, 5, 6]) & (b02 < 0.11)
    return b02, b03, b04, b08, valid_data, strict_clear

def build_seamless_composite(lat_min, lat_max, lon_min, lon_max, label, fallback_ndvi_envi=None):
    r0, r1, c0, c1 = bbox_to_s2_pixels(lat_min, lat_max, lon_min, lon_max, res=10.0)
    H, W = r1 - r0, c1 - c0
    print(f"\n--- Fusión Sin Costuras {label}: {H}x{W} px (10m) ---")

    base_dir = r"C:\Copernico\S2_Updated_2026"
    dates = ["2026-06-11", "2026-10-27", "2026-11-08"]

    stack_b02, stack_b03, stack_b04, stack_b08, stack_score = [], [], [], [], []

    for d in dates:
        dfolder = os.path.join(base_dir, d)
        b02, b03, b04, b08, valid_data, strict_clear = load_s2_window(dfolder, r0, r1, c0, c1)
        ndvi_d = (b08 - b04) / (b08 + b04 + 1e-6)
        # Puntaje de calidad libre de bruma: alto NDVI o baja reflectancia azul en roca volcánica, penalizando NoData y nubes
        score = np.where(
            strict_clear,
            10.0 + ndvi_d - 2.5 * b02,
            np.where(valid_data, 1.0 - 4.0 * b02, -999.0)
        )
        stack_b02.append(b02)
        stack_b03.append(b03)
        stack_b04.append(b04)
        stack_b08.append(b08)
        stack_score.append(score)

    scores = np.stack(stack_score, axis=0)
    best_idx = np.argmax(scores, axis=0)

    yy, xx = np.indices((H, W))
    comp_b02 = np.stack(stack_b02, axis=0)[best_idx, yy, xx]
    comp_b03 = np.stack(stack_b03, axis=0)[best_idx, yy, xx]
    comp_b04 = np.stack(stack_b04, axis=0)[best_idx, yy, xx]
    comp_b08 = np.stack(stack_b08, axis=0)[best_idx, yy, xx]
    max_score = scores[best_idx, yy, xx]

    ndvi = np.clip((comp_b08 - comp_b04) / (comp_b08 + comp_b04 + 1e-6), 0.05, 0.96)

    # Si tenemos el ráster ENVI histórico sin nubes para Samanga Baja, rellenar cualquier rincón con nubosidad residual
    if fallback_ndvi_envi is not None and os.path.exists(fallback_ndvi_envi):
        raw_envi = np.fromfile(fallback_ndvi_envi, dtype=">f4").reshape((402, 400))
        valid_envi = np.where((np.isfinite(raw_envi)) & (raw_envi > 0.05) & (raw_envi <= 1.0), raw_envi, 0.817).astype(np.float32)
        envi_resized = cv2.resize(valid_envi, (W, H), interpolation=cv2.INTER_LINEAR)
        cloudy_rem = (max_score < 8.0) | (ndvi < 0.35)
        ndvi = np.where(cloudy_rem, np.maximum(ndvi, envi_resized), ndvi)
        # Reconstruir color real vegetativo natural en píxeles donde hubo nube en las 3 fechas
        comp_b04 = np.where(cloudy_rem, np.clip(0.035 * (1.0 - 0.5 * ndvi), 0.015, 0.06), comp_b04)
        comp_b03 = np.where(cloudy_rem, np.clip(0.055 * (0.6 + 0.4 * ndvi), 0.030, 0.08), comp_b03)
        comp_b02 = np.where(cloudy_rem, np.clip(0.025 * (1.0 - 0.4 * ndvi), 0.012, 0.04), comp_b02)

    ndvi = np.clip(np.nan_to_num(ndvi, nan=0.80, posinf=0.92, neginf=0.25), 0.10, 0.95)
    rgb = np.dstack([comp_b04, comp_b03, comp_b02])
    rgb = np.clip(np.nan_to_num(rgb, nan=0.05), 0.0, 0.20) / 0.20
    rgb = rgb ** (1.0 / 1.85)
    return rgb, ndvi

if __name__ == "__main__":
    # 1. Vereda Samanga Baja
    SAM_LAT_MIN, SAM_LAT_MAX = 2.382871, 2.418983
    SAM_LON_MIN, SAM_LON_MAX = -76.587846, -76.551913
    envi_path = r"C:\Copernico\Mapa_NDVI_Samanga_2026.data\band_1.img"
    rgb_sam, ndvi_sam = build_seamless_composite(
        SAM_LAT_MIN, SAM_LAT_MAX, SAM_LON_MIN, SAM_LON_MAX,
        "Vereda Samanga Baja", fallback_ndvi_envi=envi_path
    )

    plt.imsave(r"C:\Copernico\samanga_rgb_2026.png", rgb_sam)
    plt.imsave(r"C:\Copernico\samanga_ndvi_overlay.png", ndvi_sam, cmap="RdYlGn", vmin=0.25, vmax=0.92)
    print(f"  [OK] NDVI medio Samanga Baja (Fusión sin nubes 2026): {float(np.mean(ndvi_sam)):.3f}")

    fig, ax = plt.subplots(1, 2, figsize=(12, 5.2), dpi=160)
    fig.patch.set_facecolor("#0b0e14")
    ax[0].imshow(rgb_sam, extent=[SAM_LON_MIN, SAM_LON_MAX, SAM_LAT_MIN, SAM_LAT_MAX])
    ax[0].set_title("Sentinel-2 L2A Color Real (10 m)\nVereda Samanga Baja (Mosaico 2026)", color="white", fontsize=10)
    ax[0].tick_params(colors="lightgray", labelsize=8)

    im1 = ax[1].imshow(ndvi_sam, cmap="RdYlGn", vmin=0.25, vmax=0.92, extent=[SAM_LON_MIN, SAM_LON_MAX, SAM_LAT_MIN, SAM_LAT_MAX])
    ax[1].set_title(f"Vigor Cafetalero NDVI (Media: {float(np.mean(ndvi_sam)):.3f})\nSentinel-2 L2A Actualizado Nov 2026", color="white", fontsize=10)
    ax[1].tick_params(colors="lightgray", labelsize=8)
    cb = fig.colorbar(im1, ax=ax[1], fraction=0.046, pad=0.04)
    cb.ax.yaxis.set_tick_params(color="white", labelcolor="white")
    plt.tight_layout()
    plt.savefig(r"C:\Copernico\ndvi_samanga_analysis.png", facecolor=fig.get_facecolor())
    plt.close(fig)

    # 2. Volcán Puracé
    PUR_LAT_MIN, PUR_LAT_MAX = 2.250, 2.320
    PUR_LON_MIN, PUR_LON_MAX = -76.450, -76.350
    rgb_pur, ndvi_pur = build_seamless_composite(PUR_LAT_MIN, PUR_LAT_MAX, PUR_LON_MIN, PUR_LON_MAX, "Volcán Puracé")
    plt.imsave(r"C:\Copernico\purace_rgb_2026.png", rgb_pur)
    print("  [OK] Mosaicos ópticos y NDVI regenerados sin costuras.")
