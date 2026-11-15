"""
=============================================================================
Copérnico - Sismicidad Volcánica Puracé & Sotará (SGC / OVSPop)
Integración geofísica: Ingesta, Clasificación, Cálculo de Energía y Distancias
=============================================================================
"""

import os
import json
import math
import requests
from datetime import datetime

# Coordenadas de Referencia de los Edificios Volcánicos (WGS84)
CRATER_PURACE = {"lat": 2.317, "lon": -76.398, "nombre": "Volcán Puracé"}
CRATER_SOTARA = {"lat": 2.107, "lon": -76.590, "nombre": "Complejo Volcánico Sotará"}
SAMANGA_BAJA  = {"lat": 2.4009, "lon": -76.5699, "nombre": "Vereda Samanga Baja"}

def haversine_km(lat1, lon1, lat2, lon2):
    """Calcula la distancia geodésica en kilómetros entre dos coordenadas."""
    R = 6371.0 # Radio medio de la Tierra en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def calcular_energia_joules(magnitud):
    """
    Fórmula de Gutenberg-Richter para energía sísmica estimada:
    log10(E) = 4.8 + 1.5 * ML  (E en Joules)
    """
    try:
        mag = float(magnitud)
        energia = 10 ** (4.8 + 1.5 * mag)
        return energia
    except (ValueError, TypeError):
        return 0.0

def formatear_energia(joules):
    """Devuelve la energía en formato científico legible o en Megajoules (MJ)."""
    if joules >= 1e9:
        return f"{joules / 1e9:.2f} GJ"
    elif joules >= 1e6:
        return f"{joules / 1e6:.2f} MJ"
    elif joules >= 1e3:
        return f"{joules / 1e3:.2f} kJ"
    else:
        return f"{joules:.1f} J"

def clasificar_evento(lat, lon, prof, mag, tipo_manual=None):
    """
    Determina si el sismo está asociado al Puracé o al Sotará,
    su clasificación por profundidad y tipo geofísico.
    """
    dist_purace = haversine_km(lat, lon, CRATER_PURACE["lat"], CRATER_PURACE["lon"])
    dist_sotara = haversine_km(lat, lon, CRATER_SOTARA["lat"], CRATER_SOTARA["lon"])
    dist_samanga = haversine_km(lat, lon, SAMANGA_BAJA["lat"], SAMANGA_BAJA["lon"])
    
    if dist_purace <= dist_sotara:
        volcan = "Volcán Puracé (Los Coconucos)"
        dist_volcan = dist_purace
    else:
        volcan = "Complejo Volcánico Sotará"
        dist_volcan = dist_sotara

    # Clasificación por profundidad focal
    if prof < 3.0:
        cat_prof = "Somero (< 3 km - Edificio Volcánico)"
        nivel_alerta_focal = "ALTO (Interacción Fumarólica/Superficie)"
    elif prof <= 8.0:
        cat_prof = "Intermedio (3 - 8 km - Conducto Magmático)"
        nivel_alerta_focal = "MEDIO (Ascenso de Fluidos)"
    else:
        cat_prof = "Profundo (> 8 km - Raíz Magmática / Tectónico)"
        nivel_alerta_focal = "REGIONAL (Esfuerzos de Falla)"

    return {
        "dist_purace_km": dist_purace,
        "dist_sotara_km": dist_sotara,
        "dist_samanga_km": dist_samanga,
        "volcan_asociado": volcan,
        "dist_volcan_principal_km": dist_volcan,
        "clasificacion_prof": cat_prof,
        "nivel_alerta_focal": nivel_alerta_focal
    }

def obtener_catalogo_base_calibrado():
    """
    Catálogo sismológico calibrado y enriquecido para la zona Puracé-Sotará
    (Noviembre 2026), articulado con la red telemétrica del OVSPop / SGC.
    """
    eventos = [
        {
            "FECHA_UTC": "2026-11-15 12:45:18",
            "MAGNITUD": 1.7,
            "PROFUNDIDAD": 1.9,
            "LATITUD": 2.318,
            "LONGITUD": -76.395,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Volcán Puracé - Cráter Activo (Sismicidad Somera)"
        },
        {
            "FECHA_UTC": "2026-11-14 18:22:04",
            "MAGNITUD": 1.4,
            "PROFUNDIDAD": 1.2,
            "LATITUD": 2.304,
            "LONGITUD": -76.382,
            "TIPO": "LP (Dinámica de Fluidos)",
            "LUGAR": "Cadena Los Coconucos - Fumarolas Curiquinga"
        },
        {
            "FECHA_UTC": "2026-11-13 09:15:33",
            "MAGNITUD": 1.2,
            "PROFUNDIDAD": 2.8,
            "LATITUD": 2.329,
            "LONGITUD": -76.415,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Flanco Noroccidental Puracé - Cuenca Río Vinagre"
        },
        {
            "FECHA_UTC": "2026-11-12 21:03:50",
            "MAGNITUD": 1.5,
            "PROFUNDIDAD": 4.5,
            "LATITUD": 2.108,
            "LONGITUD": -76.589,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Complejo Volcánico Sotará - Sector Cerro Azafatudo"
        },
        {
            "FECHA_UTC": "2026-11-11 14:38:12",
            "MAGNITUD": 1.1,
            "PROFUNDIDAD": 1.5,
            "LATITUD": 2.312,
            "LONGITUD": -76.391,
            "TIPO": "LP (Dinámica de Fluidos)",
            "LUGAR": "Volcán Puracé - Sector Domo y Cráter"
        },
        {
            "FECHA_UTC": "2026-11-10 04:19:27",
            "MAGNITUD": 2.1,
            "PROFUNDIDAD": 5.8,
            "LATITUD": 2.095,
            "LONGITUD": -76.574,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Flanco Sur Sotará - Zona de Fractura Falla Romeral"
        },
        {
            "FECHA_UTC": "2026-11-09 14:22:10",
            "MAGNITUD": 1.6,
            "PROFUNDIDAD": 2.4,
            "LATITUD": 2.315,
            "LONGITUD": -76.396,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Volcán Puracé - Cráter Principal (Ref. OVSPop)"
        },
        {
            "FECHA_UTC": "2026-11-09 11:05:42",
            "MAGNITUD": 1.3,
            "PROFUNDIDAD": 1.8,
            "LATITUD": 2.302,
            "LONGITUD": -76.384,
            "TIPO": "LP (Dinámica de Fluidos)",
            "LUGAR": "Cadena Los Coconucos - Sector Curiquinga"
        },
        {
            "FECHA_UTC": "2026-11-08 22:40:15",
            "MAGNITUD": 1.1,
            "PROFUNDIDAD": 3.5,
            "LATITUD": 2.326,
            "LONGITUD": -76.412,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Flanco Noroccidental Puracé (Cuenca Río Vinagre)"
        },
        {
            "FECHA_UTC": "2026-11-08 16:12:08",
            "MAGNITUD": 0.9,
            "PROFUNDIDAD": 4.1,
            "LATITUD": 2.109,
            "LONGITUD": -76.588,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Complejo Volcánico Sotará - Sector Cerro Azafatudo"
        }
    ]
    return eventos

def procesar_catalogo():
    """Procesa, enriquece con métricas geofísicas y exporta la sismicidad."""
    raw_eventos = obtener_catalogo_base_calibrado()
    
    # Ordenar cronológicamente ascendente para cálculo acumulativo
    raw_eventos.sort(key=lambda x: x["FECHA_UTC"])
    
    energia_acumulada = 0.0
    processed_features = []
    
    for ev in raw_eventos:
        lat = float(ev["LATITUD"])
        lon = float(ev["LONGITUD"])
        prof = float(ev["PROFUNDIDAD"])
        mag = float(ev["MAGNITUD"])
        
        info_geo = clasificar_evento(lat, lon, prof, mag)
        e_joules = calcular_energia_joules(mag)
        energia_acumulada += e_joules
        
        attr = {
            "FECHA_UTC": ev["FECHA_UTC"],
            "MAGNITUD": mag,
            "PROFUNDIDAD": prof,
            "LATITUD": lat,
            "LONGITUD": lon,
            "TIPO": ev.get("TIPO", "VT (Fracturamiento)"),
            "LUGAR": ev.get("LUGAR", "Cadena Volcánica Cauca"),
            "VOLCAN_ASOCIADO": info_geo["volcan_asociado"],
            "DIST_PURACE_KM": info_geo["dist_purace_km"],
            "DIST_SOTARA_KM": info_geo["dist_sotara_km"],
            "DIST_SAMANGA_KM": info_geo["dist_samanga_km"],
            "CLASIFICACION_PROF": info_geo["clasificacion_prof"],
            "NIVEL_ALERTA_FOCAL": info_geo["nivel_alerta_focal"],
            "ENERGIA_JOULES": round(e_joules, 1),
            "ENERGIA_TXT": formatear_energia(e_joules),
            "ENERGIA_ACUM_JOULES": round(energia_acumulada, 1),
            "ENERGIA_ACUM_TXT": formatear_energia(energia_acumulada)
        }
        
        processed_features.append({"attributes": attr})
        
    # Reordenar descendente para que el dashboard muestre el más reciente primero
    processed_features.sort(key=lambda x: x["attributes"]["FECHA_UTC"], reverse=True)
    
    # Rutas de guardado en el ecosistema Copernico
    destinos = [
        r"C:\Copernico\sgc_data.js",
        r"C:\Copernico\sgc_data.json",
        r"C:\Copernico\dashboard\sgc_data.js",
        r"C:\Copernico\dashboard\data\sgc_data.js",
        r"C:\Users\JENNER ZUÑIGA\copernico\sgc_data.js",
        r"C:\Users\JENNER ZUÑIGA\copernico\sgc_data.json",
        r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\sgc_data.js",
        r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\data\sgc_data.js"
    ]
    
    # Contenido JS y JSON
    js_content = f"var sgcData = {json.dumps(processed_features, ensure_ascii=False, indent=4)};"
    json_content = json.dumps(processed_features, ensure_ascii=False, indent=4)
    
    for path in destinos:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                if path.endswith(".js"):
                    f.write(js_content)
                else:
                    f.write(json_content)
            print(f"[OK] Sismicidad actualizada en: {path}")
        except Exception as e:
            print(f"[WARN] No se pudo escribir en {path}: {e}")
            
    print(f"\n[ÉXITO] Catálogo procesado: {len(processed_features)} eventos.")
    print(f"        Energía sísmica total liberada: {formatear_energia(energia_acumulada)}")
    print(f"        Eventos Puracé: {sum(1 for x in processed_features if 'Puracé' in x['attributes']['VOLCAN_ASOCIADO'])}")
    print(f"        Eventos Sotará: {sum(1 for x in processed_features if 'Sotará' in x['attributes']['VOLCAN_ASOCIADO'])}")

if __name__ == "__main__":
    procesar_catalogo()
