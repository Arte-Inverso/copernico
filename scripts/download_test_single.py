# -*- coding: utf-8 -*-
"""
download_test_single.py — Descarga de prueba controlada de 1 escena Sentinel-1 SLC vía NASA ASF
"""

import os
import time
import asf_search as asf

# Directorio de descarga
DOWNLOAD_DIR = r"C:\Copernico\data\sentinel1"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def main():
    print("=" * 70)
    print("PRUEBA DE DESCARGA DIRECTA — NASA EARTHDATA (ASF)")
    print("=" * 70)
    
    # 1. Autenticar
    session = asf.ASFSession()
    session.auth_with_creds('arteinverso', 'LS?wKZ#KkE^R8Zx')
    print("✓ Autenticado en NASA Earthdata como 'arteinverso'")
    
    # 2. Buscar la escena de prueba más reciente disponible de 2026 sobre Popayán (Track 142)
    print("🔍 Seleccionando escena objetivo...")
    results = asf.search(
        platform=asf.PLATFORM.SENTINEL1,
        processingLevel=asf.PRODUCT_TYPE.SLC,
        beamMode='IW',
        flightDirection='DESCENDING',
        intersectsWith='POINT(-76.57 2.40)',
        start='2026-03-20',
        end='2026-03-30'
    )
    results = [r for r in results if r.properties.get('pathNumber') == 142]
    
    if not results:
        print("No se encontraron escenas en esa ventana, buscando alternativa...")
        results = asf.search(
            platform=asf.PLATFORM.SENTINEL1,
            processingLevel=asf.PRODUCT_TYPE.SLC,
            flightDirection='DESCENDING',
            intersectsWith='POINT(-76.57 2.40)',
            start='2026-01-01',
            end='2026-03-31',
            maxResults=1
        )
        
    target = results[0]
    fname = target.properties.get('fileName')
    size_gb = target.properties.get('bytes', 0) / (1024**3)
    
    print(f"\n📦 Escena seleccionada: {fname}")
    print(f"📊 Tamaño: {size_gb:.2f} GB")
    print(f"📁 Destino: {DOWNLOAD_DIR}")
    
    target_file = os.path.join(DOWNLOAD_DIR, fname)
    if os.path.exists(target_file):
        print(f"✓ El archivo ya existe completamente en disco ({os.path.getsize(target_file) / (1024**3):.2f} GB).")
        return

    print("\n🚀 Iniciando transferencia desde la nube de NASA...")
    t0 = time.time()
    target.download(path=DOWNLOAD_DIR, session=session)
    elapsed = time.time() - t0
    
    if os.path.exists(target_file):
        actual_gb = os.path.getsize(target_file) / (1024**3)
        speed_mb = (actual_gb * 1024) / elapsed if elapsed > 0 else 0
        print(f"\n✅ ¡Descarga completada con éxito en {elapsed:.1f} segundos!")
        print(f"   Tamaño descargado: {actual_gb:.2f} GB")
        print(f"   Velocidad media: {speed_mb:.2f} MB/s")
    else:
        print("✗ No se encontró el archivo tras el proceso.")

if __name__ == "__main__":
    main()
