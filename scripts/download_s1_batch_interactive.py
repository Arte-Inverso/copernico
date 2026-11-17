# -*- coding: utf-8 -*-
"""
download_s1_batch_interactive.py — Descarga masiva y selectiva de Sentinel-1 SLC vía NASA ASF
"""

import os
import json
import asf_search as asf
from datetime import datetime

DOWNLOAD_BASE = os.environ.get("S1_DOWNLOAD_DIR", r"C:\Copernico\data\sentinel1")
os.makedirs(DOWNLOAD_BASE, exist_ok=True)

# Coordenada central sobre Popayán / Samanga Baja / Puracé
POINT_POPAYAN = "POINT(-76.57 2.40)"

def get_asf_session():
    """Autentica sesión contra NASA Earthdata usando netrc o variables de entorno."""
    session = asf.ASFSession()
    try:
        user = os.environ.get("EARTHDATA_USER")
        pwd = os.environ.get("EARTHDATA_PASSWORD")
        if user and pwd:
            session.auth_with_creds(user, pwd)
        else:
            session.auth_with_netrc()
        return session
    except Exception as e:
        print("Error en autenticación:", e)
        return None

def search_scenes(start_date="2025-01-01", end_date="2026-11-15"):
    """Busca escenas Sentinel-1 SLC en Track 142 Descendente (pathNumber=142)."""
    print(f"\n🔍 Consultando catálogo de la NASA en Track 142 Descendente ({start_date} a {end_date})...")
    
    # En ASF el parámetro para Track de órbita relativa es pathNumber
    results = asf.search(
        platform=asf.PLATFORM.SENTINEL1,
        processingLevel=asf.PRODUCT_TYPE.SLC,
        beamMode='IW',
        flightDirection='DESCENDING',
        intersectsWith=POINT_POPAYAN,
        start=start_date,
        end=end_date
    )
    # Filtrar solo Track 142
    results = [r for r in results if r.properties.get('pathNumber') == 142]
    # Ordenar cronológicamente
    results.sort(key=lambda r: r.properties.get("startTime", ""))
    print(f"✓ ¡Se encontraron {len(results)} escenas Sentinel-1 SLC disponibles en Track 142 Descendente!")
    return results

def catalog_and_preview(results, limit=15):
    catalog = []
    print(f"\n📋 Catálogo cronológico de las primeras {min(limit, len(results))} escenas seleccionadas:")
    total_bytes = 0
    for i, r in enumerate(results[:limit]):
        props = r.properties
        b = props.get("bytes", 0)
        total_bytes += b
        date_str = props.get("startTime", "")[:10]
        fname = props.get("fileName", "Unknown")
        platform = props.get("platform", "Sentinel-1")
        size_gb = b / (1024**3)
        print(f"  [{i+1:02d}] 📅 {date_str} | {platform} | {fname} ({size_gb:.2f} GB)")
        catalog.append({
            "index": i + 1,
            "date": date_str,
            "platform": platform,
            "filename": fname,
            "size_gb": round(size_gb, 2),
            "url": props.get("url", ""),
            "orbit": props.get("orbit", 0)
        })
    print(f"\n📦 Espacio estimado para este paquete de {min(limit, len(results))} escenas: {total_bytes / (1024**3):.2f} GB")
    return catalog

if __name__ == "__main__":
    print("=" * 70)
    print("SISTEMA DE DESCARGA SENTINEL-1 — NASA EARTHDATA & ASF VERTEX")
    print("=" * 70)
    
    session = get_asf_session()
    if session:
        print("✓ Autenticación con NASA verificada exitosamente.")
        results = search_scenes("2025-01-01", "2026-11-15")
        cat = catalog_and_preview(results, limit=15)
        
        # Guardar catálogo JSON local
        cat_file = os.path.join(DOWNLOAD_BASE, "sentinel1_track142_catalog.json")
        with open(cat_file, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=2)
        print(f"\n💾 Catálogo guardado en: {cat_file}")
