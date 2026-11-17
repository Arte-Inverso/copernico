# -*- coding: utf-8 -*-
"""
batch_download_seismic_targets.py — Descarga automatizada y resiliente de escenas Sentinel-1 SLC
para los eventos co-sísmicos de Chocó (M 7.4), Tolima/Chaparral (M 5.4/4.5) y Venezuela (M 5.0).
"""

import os
import time
import asf_search as asf

DOWNLOAD_DIR = r"C:\Copernico\data\sentinel1"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Escenas clave identificadas para los pares co-sísmicos en Track 142 Descendente
TARGET_SCENES = [
    # 1. Evento Chocó (M 7.4 del 10-Agosto-2026)
    {
        "event": "Chocó M 7.4 (Pre-sismo)",
        "date": "2026-08-08",
        "filename": "S1D_IW_SLC__1SDV_20260808T105103_20260808T105130_004033_007567_9CF7.zip"
    },
    {
        "event": "Chocó M 7.4 (Post-sismo)",
        "date": "2026-08-14",
        "filename": "S1C_IW_SLC__1SDV_20260814T105050_20260814T105118_008990_011D78_C97B.zip"
    },
    # 2. Evento Venezuela (M 5.0 del 02-Octubre-2026)
    {
        "event": "Venezuela M 5.0 (Pre-sismo)",
        "date": "2026-10-01",
        "filename": "S1C_IW_SLC__1SDV_20261001T105051_20261001T105119_009690_0134C4_67D0.zip"
    },
    {
        "event": "Venezuela M 5.0 (Post-sismo)",
        "date": "2026-10-07",
        "filename": "S1D_IW_SLC__1SDV_20261007T105104_20261007T105132_004908_0093DE_5AC2.zip"
    },
    # 3. Evento Rioblanco & Chaparral Tolima (M 5.4 / M 4.5 de Noviembre-2026)
    {
        "event": "Rioblanco/Chaparral (Pre-sismo)",
        "date": "2026-10-31",
        "filename": "S1D_IW_SLC__1SDV_20261031T105104_20261031T105132_005258_009FEA_9725.zip"
    },
    {
        "event": "Rioblanco/Chaparral (Post-sismo)",
        "date": "2026-11-12",
        "filename": "S1D_IW_SLC__1SDV_20261112T105104_20261112T105132_005433_00A5F2_5F54.zip"
    }
]

def main():
    print("=" * 75)
    print("PROGRAMA DE DESCARGA CO-SÍSMICA SENTINEL-1 — NASA EARTHDATA (ASF)")
    print("Eventos: Chocó M 7.4 · Rioblanco/Chaparral M 5.4/4.5 · Venezuela M 5.0")
    print("=" * 75)

    session = asf.ASFSession()
    user = os.environ.get("EARTHDATA_USER")
    pwd = os.environ.get("EARTHDATA_PASSWORD")
    if user and pwd:
        session.auth_with_creds(user, pwd)
    else:
        session.auth_with_netrc()
    print("✓ Autenticado exitosamente en NASA Earthdata (netrc / env)")

    for idx, item in enumerate(TARGET_SCENES):
        fname = item["filename"]
        event_name = item["event"]
        date_str = item["date"]
        target_path = os.path.join(DOWNLOAD_DIR, fname)

        print(f"\n[{idx+1}/{len(TARGET_SCENES)}] {event_name} (Fecha: {date_str})")
        print(f"    Archivo: {fname}")

        if os.path.exists(target_path) and os.path.getsize(target_path) > 3.5 * (1024**3):
            print(f"    ✓ Ya existe completo en disco ({os.path.getsize(target_path)/(1024**3):.2f} GB). Omitiendo.")
            continue

        print("    🔍 Buscando metadatos en ASF...")
        res = asf.search(
            platform=asf.PLATFORM.SENTINEL1,
            processingLevel=asf.PRODUCT_TYPE.SLC,
            flightDirection='DESCENDING',
            intersectsWith='POINT(-76.57 2.40)',
            start=date_str,
            end=date_str + "T23:59:59"
        )
        matched = [r for r in res if r.properties.get("fileName") == fname]
        if not matched:
            print("    ⚠ No se pudo localizar la escena exacta por nombre, buscando por fecha...")
            matched = res

        if matched:
            scene = matched[0]
            size_gb = scene.properties.get('bytes', 0) / (1024**3)
            print(f"    🚀 Descargando {size_gb:.2f} GB desde NASA ASF...")
            t0 = time.time()
            try:
                scene.download(path=DOWNLOAD_DIR, session=session)
                elapsed = time.time() - t0
                speed = (size_gb * 1024) / elapsed if elapsed > 0 else 0
                print(f"    ✅ Descarga completada en {elapsed/60:.1f} min ({speed:.2f} MB/s).")
            except Exception as e:
                print(f"    ✗ Error durante la descarga: {e}")
        else:
            print(f"    ✗ No se encontró la escena en el catálogo.")

if __name__ == "__main__":
    main()
