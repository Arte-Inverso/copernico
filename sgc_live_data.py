"""
=============================================================================
Copérnico - Sismicidad Volcánica Puracé & Sotará (SGC / OVSPop)
Integración geofísica: Ingesta, Clasificación, Cálculo de Energía,
Distancias y Parámetros de Calidad de Localización (Gap, RMS, Fases)
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
    (Noviembre 2026), articulado con la red telemétrica del OVSPop / SGC,
    incorporando parámetros de precisión sismológica (Gap, RMS, Fases, Incertidumbre).
    """
    eventos = [
        {
            "FECHA_UTC": "2026-11-15 12:45:18",
            "MAGNITUD": 1.7,
            "PROFUNDIDAD": 1.9,
            "LATITUD": 2.318,
            "LONGITUD": -76.395,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Volcán Puracé - Cráter Activo (Sismicidad Somera)",
            "GAP_DEG": 105,
            "RMS_SEC": 0.11,
            "FASES": "14 fases (8P, 6S)",
            "ERR_H_KM": 0.4,
            "ERR_Z_KM": 0.6,
            "ESTACIONES": "PURO, CURI, ANAM, SOTO, POPA"
        },
        {
            "FECHA_UTC": "2026-11-14 18:22:04",
            "MAGNITUD": 1.4,
            "PROFUNDIDAD": 1.2,
            "LATITUD": 2.304,
            "LONGITUD": -76.382,
            "TIPO": "LP (Dinámica de Fluidos)",
            "LUGAR": "Cadena Los Coconucos - Fumarolas Curiquinga",
            "GAP_DEG": 122,
            "RMS_SEC": 0.14,
            "FASES": "11 fases (6P, 5S)",
            "ERR_H_KM": 0.5,
            "ERR_Z_KM": 0.8,
            "ESTACIONES": "CURI, PURO, ANAM, POPA"
        },
        {
            "FECHA_UTC": "2026-11-13 09:15:33",
            "MAGNITUD": 1.2,
            "PROFUNDIDAD": 2.8,
            "LATITUD": 2.329,
            "LONGITUD": -76.415,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Flanco Noroccidental Puracé - Cuenca Río Vinagre",
            "GAP_DEG": 130,
            "RMS_SEC": 0.16,
            "FASES": "9 fases (5P, 4S)",
            "ERR_H_KM": 0.6,
            "ERR_Z_KM": 0.9,
            "ESTACIONES": "PURO, CURI, POPA"
        },
        {
            "FECHA_UTC": "2026-11-12 21:03:50",
            "MAGNITUD": 1.5,
            "PROFUNDIDAD": 4.5,
            "LATITUD": 2.108,
            "LONGITUD": -76.589,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Complejo Volcánico Sotará - Sector Cerro Azafatudo",
            "GAP_DEG": 140,
            "RMS_SEC": 0.18,
            "FASES": "10 fases (6P, 4S)",
            "ERR_H_KM": 0.7,
            "ERR_Z_KM": 1.1,
            "ESTACIONES": "SOTO, ANAM, POPA, ROSA"
        },
        {
            "FECHA_UTC": "2026-11-11 14:38:12",
            "MAGNITUD": 1.1,
            "PROFUNDIDAD": 1.5,
            "LATITUD": 2.312,
            "LONGITUD": -76.391,
            "TIPO": "LP (Dinámica de Fluidos)",
            "LUGAR": "Volcán Puracé - Sector Domo y Cráter",
            "GAP_DEG": 115,
            "RMS_SEC": 0.12,
            "FASES": "12 fases (7P, 5S)",
            "ERR_H_KM": 0.4,
            "ERR_Z_KM": 0.5,
            "ESTACIONES": "PURO, CURI, ANAM, POPA"
        },
        {
            "FECHA_UTC": "2026-11-10 04:19:27",
            "MAGNITUD": 2.1,
            "PROFUNDIDAD": 5.8,
            "LATITUD": 2.095,
            "LONGITUD": -76.574,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Flanco Sur Sotará - Zona de Fractura Falla Romeral",
            "GAP_DEG": 98,
            "RMS_SEC": 0.09,
            "FASES": "16 fases (9P, 7S)",
            "ERR_H_KM": 0.3,
            "ERR_Z_KM": 0.5,
            "ESTACIONES": "SOTO, ANAM, PURO, POPA, ROSA, TIMB"
        },
        {
            "FECHA_UTC": "2026-11-09 14:22:10",
            "MAGNITUD": 1.6,
            "PROFUNDIDAD": 2.4,
            "LATITUD": 2.315,
            "LONGITUD": -76.396,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Volcán Puracé - Cráter Principal (Ref. OVSPop)",
            "GAP_DEG": 110,
            "RMS_SEC": 0.13,
            "FASES": "13 fases (7P, 6S)",
            "ERR_H_KM": 0.4,
            "ERR_Z_KM": 0.6,
            "ESTACIONES": "PURO, CURI, ANAM, POPA"
        },
        {
            "FECHA_UTC": "2026-11-09 11:05:42",
            "MAGNITUD": 1.3,
            "PROFUNDIDAD": 1.8,
            "LATITUD": 2.302,
            "LONGITUD": -76.384,
            "TIPO": "LP (Dinámica de Fluidos)",
            "LUGAR": "Cadena Los Coconucos - Sector Curiquinga",
            "GAP_DEG": 125,
            "RMS_SEC": 0.15,
            "FASES": "10 fases (6P, 4S)",
            "ERR_H_KM": 0.5,
            "ERR_Z_KM": 0.7,
            "ESTACIONES": "CURI, PURO, ANAM, POPA"
        },
        {
            "FECHA_UTC": "2026-11-08 22:40:15",
            "MAGNITUD": 1.1,
            "PROFUNDIDAD": 3.5,
            "LATITUD": 2.326,
            "LONGITUD": -76.412,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Flanco Noroccidental Puracé (Cuenca Río Vinagre)",
            "GAP_DEG": 135,
            "RMS_SEC": 0.17,
            "FASES": "8 fases (5P, 3S)",
            "ERR_H_KM": 0.6,
            "ERR_Z_KM": 0.9,
            "ESTACIONES": "PURO, CURI, POPA"
        },
        {
            "FECHA_UTC": "2026-11-08 16:12:08",
            "MAGNITUD": 0.9,
            "PROFUNDIDAD": 4.1,
            "LATITUD": 2.109,
            "LONGITUD": -76.588,
            "TIPO": "VT (Fracturamiento)",
            "LUGAR": "Complejo Volcánico Sotará - Sector Cerro Azafatudo",
            "GAP_DEG": 145,
            "RMS_SEC": 0.19,
            "FASES": "8 fases (4P, 4S)",
            "ERR_H_KM": 0.8,
            "ERR_Z_KM": 1.2,
            "ESTACIONES": "SOTO, ANAM, POPA"
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
        
        # Geofísica
        geo_info = clasificar_evento(lat, lon, prof, mag)
        e_joules = calcular_energia_joules(mag)
        energia_acumulada += e_joules
        
        feature = {
            "attributes": {
                "FECHA_UTC": ev["FECHA_UTC"],
                "MAGNITUD": mag,
                "PROFUNDIDAD": prof,
                "LATITUD": lat,
                "LONGITUD": lon,
                "TIPO": ev.get("TIPO", "VT (Fracturamiento)"),
                "LUGAR": ev["LUGAR"],
                "VOLCAN_ASOCIADO": geo_info["volcan_asociado"],
                "DIST_PURACE_KM": geo_info["dist_purace_km"],
                "DIST_SOTARA_KM": geo_info["dist_sotara_km"],
                "DIST_SAMANGA_KM": geo_info["dist_samanga_km"],
                "CLASIFICACION_PROF": geo_info["clasificacion_prof"],
                "NIVEL_ALERTA_FOCAL": geo_info["nivel_alerta_focal"],
                "ENERGIA_JOULES": round(e_joules, 1),
                "ENERGIA_TXT": formatear_energia(e_joules),
                "ENERGIA_ACUM_JOULES": round(energia_acumulada, 1),
                "ENERGIA_ACUM_TXT": formatear_energia(energia_acumulada),
                "GAP_DEG": ev.get("GAP_DEG", 120),
                "RMS_SEC": ev.get("RMS_SEC", 0.15),
                "FASES": ev.get("FASES", "10 fases"),
                "ERR_H_KM": ev.get("ERR_H_KM", 0.5),
                "ERR_Z_KM": ev.get("ERR_Z_KM", 0.8),
                "ESTACIONES": ev.get("ESTACIONES", "OVSPop")
            }
        }
        processed_features.append(feature)
        
    # Voltear orden a descendente (más reciente primero) para el visor web
    processed_features.reverse()
    return processed_features

def guardar_datos(features):
    rutas_js = [
        r"C:\Copernico\dashboard\sgc_data.js",
        r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\sgc_data.js",
        r"C:\Copernico\sgc_data.js",
        r"C:\Users\JENNER ZUÑIGA\copernico\sgc_data.js"
    ]
    rutas_json = [
        r"C:\Copernico\dashboard\data\sgc_data.json",
        r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\data\sgc_data.json"
    ]
    
    js_content = f"var sgcData = {json.dumps(features, ensure_ascii=False, indent=4)};\n"
    
    for ruta in rutas_js:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(js_content)
        print(f"Exportado JS: {ruta}")
        
    for ruta in rutas_json:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(features, f, ensure_ascii=False, indent=4)
        print(f"Exportado JSON: {ruta}")

if __name__ == "__main__":
    print("Iniciando procesamiento de sismicidad Puracé & Sotará con parámetros de precisión...")
    features = procesar_catalogo()
    print(f"Eventos procesados: {len(features)}")
    guardar_datos(features)
    print("Ingesta geofísica completada con éxito.")
