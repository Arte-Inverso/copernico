# -*- coding: utf-8 -*-
"""
download_purace_pre_eruption.py — Descarga Optimizada de Subswaths InSAR Pre-Erupción Puracé
========================================================================================
Estrategia: Máxima ciencia, mínimo disco.
1. Busca escenas Sentinel-1 SLC en Track 142 Descendente (Puracé) entre 2024 y 2025.
2. Selecciona N imágenes distribuidas uniformemente en la ventana pre-eruptiva.
3. Descarga cada archivo .zip, extrae ÚNICAMENTE el subswath IW1 VV (y opcionalmente IW2 VV)
   junto con sus metadatos XML de anotación geométrica.
4. ELIMINA INMEDIATAMENTE el archivo .zip de 4.5 GB, ocupando solo ~0.8-1.1 GB por época.
5. Ahorro de espacio: >80% frente a la descarga SLC completa.
"""

import os
import sys
import argparse
import json
import time
import zipfile
import asf_search as asf

OUT_DIR_DEFAULT = r"C:\Copernico\data\sentinel1_pre_eruption"
PURACE_POINT = "POINT(-76.398 2.318)"  # Cráter Volcán Puracé


def get_asf_session():
    """Autenticación segura con NASA Earthdata vía netrc o variables de entorno."""
    session = asf.ASFSession()
    user = os.environ.get("EARTHDATA_USER")
    pwd = os.environ.get("EARTHDATA_PASSWORD")
    try:
        if user and pwd:
            session.auth_with_creds(user, pwd)
        else:
            session.auth_with_netrc()
        return session
    except Exception as e:
        print(f"⚠️ Error al autenticar con NASA Earthdata: {e}")
        print("Asegúrate de tener configurado tu archivo .netrc o las variables $env:EARTHDATA_USER y $env:EARTHDATA_PASSWORD")
        return None


def search_pre_eruption_scenes(start_date="2024-01-01", end_date="2025-10-31"):
    """Busca todas las escenas SLC Sentinel-1 en Track 142 sobre el Puracé."""
    print(f"\n🔍 Buscando escenas Sentinel-1 SLC en Track 142 ({start_date} a {end_date})...")
    results = asf.search(
        platform=asf.PLATFORM.SENTINEL1,
        processingLevel=asf.PRODUCT_TYPE.SLC,
        beamMode="IW",
        flightDirection="DESCENDING",
        intersectsWith=PURACE_POINT,
        start=start_date,
        end=end_date
    )
    
    # Filtrar por Track 142
    track_results = [r for r in results if r.properties.get("pathNumber") == 142]
    # Ordenar cronológicamente
    track_results.sort(key=lambda r: r.properties.get("startTime", ""))
    print(f"✓ Total de adquisiciones disponibles en Track 142: {len(track_results)} escenas")
    return track_results


def select_uniform_scenes(results, count=10):
    """Selecciona N escenas distribuidas uniformemente en el tiempo."""
    if len(results) <= count:
        return results
    
    indices = [int(i * (len(results) - 1) / (count - 1)) for i in range(count)]
    selected = [results[i] for i in sorted(set(indices))]
    return selected


def extract_subswath_and_cleanup(zip_path, target_dir, subswaths=("iw1",)):
    """Extrae únicamente los subswaths VV solicitados y elimina el .zip."""
    subswaths_clean = [s.lower() for s in subswaths]
    extracted_files = []
    
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.namelist():
            m_lower = member.lower()
            # Filtrar solo archivos de medición VV y anotación XML VV para los subswaths elegidos
            is_measurement = "measurement" in m_lower and "vv" in m_lower and m_lower.endswith(".tiff")
            is_annotation = "annotation" in m_lower and "vv" in m_lower and m_lower.endswith(".xml") and "calibration" not in m_lower and "rfi" not in m_lower
            
            if is_measurement or is_annotation:
                matches_swath = any(sw in m_lower for sw in subswaths_clean)
                if matches_swath:
                    dest = os.path.join(target_dir, member)
                    if not os.path.exists(dest):
                        z.extract(member, target_dir)
                    extracted_files.append(dest)
                    
    # ELIMINAR EL ZIP ORIGINAL PARA LIBERAR 4.5 GB INMEDIATAMENTE
    try:
        os.remove(zip_path)
        print(f"    🗑️ Archivo .zip temporal eliminado (liberados ~4.5 GB)")
    except Exception as e:
        print(f"    ⚠️ No se pudo eliminar el zip temporal: {e}")
        
    return extracted_files


def download_optimized_series(scenes, out_dir, subswaths=("iw1",)):
    """Descarga secuencialmente cada escena, extrae subswaths y borra el .zip."""
    os.makedirs(out_dir, exist_ok=True)
    session = get_asf_session()
    if not session:
        return
    
    print("\n" + "=" * 75)
    print(f"DESCARGA OPTIMIZADA SENTINEL-1 — SERIE TEMPORAL PURACÉ ({len(scenes)} ÉPOCAS)")
    print(f"Subswaths seleccionados: {', '.join(subswaths).upper()} (Polarización VV)")
    print(f"Directorio de destino: {out_dir}")
    print("=" * 75)
    
    catalog_entries = []
    
    for idx, scene in enumerate(scenes):
        props = scene.properties
        fname = props.get("fileName", f"scene_{idx}.zip")
        date_str = props.get("startTime", "")[:10]
        safe_name = fname.replace(".zip", ".SAFE")
        
        print(f"\n[{idx+1}/{len(scenes)}] Fecha: {date_str} — {fname}")
        
        # Verificar si ya está extraído en destino
        expected_measurement_dir = os.path.join(out_dir, safe_name, "measurement")
        if os.path.exists(expected_measurement_dir) and len(os.listdir(expected_measurement_dir)) > 0:
            print(f"    ✓ Ya extraído previamente en disco. Omitiendo descarga.")
            catalog_entries.append({
                "index": idx + 1,
                "date": date_str,
                "scene_name": props.get("sceneName", ""),
                "safe_name": safe_name,
                "status": "ALREADY_EXISTS"
            })
            continue
            
        temp_zip_path = os.path.join(out_dir, fname)
        t0 = time.time()
        
        print(f"    🚀 Descargando archivo desde ASF...")
        try:
            scene.download(path=out_dir, session=session)
            dt = time.time() - t0
            zip_size_mb = os.path.getsize(temp_zip_path) / (1024**2)
            print(f"    ✓ Descarga finalizada en {dt:.1f} s ({zip_size_mb:.1f} MB a {zip_size_mb/dt:.2f} MB/s)")
            
            print(f"    📦 Extrayendo subswaths {', '.join(subswaths).upper()}...")
            extracted = extract_subswath_and_cleanup(temp_zip_path, out_dir, subswaths)
            print(f"    ✓ Extraídos {len(extracted)} archivos clave.")
            
            catalog_entries.append({
                "index": idx + 1,
                "date": date_str,
                "scene_name": props.get("sceneName", ""),
                "safe_name": safe_name,
                "extracted_files": [os.path.basename(f) for f in extracted],
                "status": "DOWNLOADED_AND_EXTRACTED"
            })
        except Exception as e:
            print(f"    ✗ Error durante la descarga/extracción: {e}")
            if os.path.exists(temp_zip_path):
                try:
                    os.remove(temp_zip_path)
                except:
                    pass
                    
    # Guardar catálogo JSON de la serie
    cat_path = os.path.join(out_dir, "pre_eruption_catalog.json")
    with open(cat_path, "w", encoding="utf-8") as f:
        json.dump(catalog_entries, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 75)
    print(f"✓ Serie pre-eruptiva optimizada completada.")
    print(f"✓ Catálogo guardado en: {cat_path}")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(description="Descarga optimizada de subswaths Sentinel-1 SLC sobre Puracé")
    parser.add_argument("--count", type=int, default=10, help="Número de imágenes a descargar distribuidas uniformemente (default: 10)")
    parser.add_argument("--start", type=str, default="2024-01-01", help="Fecha inicial YYYY-MM-DD (default: 2024-01-01)")
    parser.add_argument("--end", type=str, default="2025-10-31", help="Fecha final YYYY-MM-DD (default: 2025-10-31)")
    parser.add_argument("--include-samanga", action="store_true", help="Incluir subswath IW2 además de IW1 (para Samanga Baja/POVA)")
    parser.add_argument("--outdir", type=str, default=OUT_DIR_DEFAULT, help=f"Directorio de salida (default: {OUT_DIR_DEFAULT})")
    
    args = parser.parse_args()
    
    subswaths = ["iw1"]
    if args.include_samanga:
        subswaths.append("iw2")
        
    all_scenes = search_pre_eruption_scenes(args.start, args.end)
    if not all_scenes:
        print("No se encontraron escenas para el rango especificado.")
        return
        
    selected = select_uniform_scenes(all_scenes, count=args.count)
    print(f"\n📅 Escenas seleccionadas para la serie pre-eruptiva ({len(selected)} épocas):")
    for s in selected:
        print(f"   • {s.properties.get('startTime', '')[:10]} | {s.properties.get('sceneName', '')}")
        
    download_optimized_series(selected, args.outdir, subswaths)


if __name__ == "__main__":
    main()
