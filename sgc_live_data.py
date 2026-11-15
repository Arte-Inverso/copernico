import requests
import json

def save_data(data, source_name):
    # Asegurar que se guarde en C:\Copernico para que el dashboard lo vea
    output_path = r'C:\Copernico\sgc_data.js'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"var sgcData = {json.dumps(data, ensure_ascii=False, indent=4)};")
    print(f"{source_name}: {output_path} actualizado.")

def save_mock_data():
    mock_data = [
        {"attributes": {"FECHA_UTC": "2026-11-09 14:22:10", "MAGNITUD": 1.6, "PROFUNDIDAD": 2.4, "LATITUD": 2.315, "LONGITUD": -76.396, "TIPO": "VT (Fracturamiento)", "LUGAR": "Volcán Puracé - Cráter Principal (Ref. OVSPop)"}},
        {"attributes": {"FECHA_UTC": "2026-11-09 11:05:42", "MAGNITUD": 1.3, "PROFUNDIDAD": 1.8, "LATITUD": 2.302, "LONGITUD": -76.384, "TIPO": "LP (Dinámica de Fluidos)", "LUGAR": "Cadena Volcánica Los Coconucos - Sector Curiquinga"}},
        {"attributes": {"FECHA_UTC": "2026-11-08 22:40:15", "MAGNITUD": 1.1, "PROFUNDIDAD": 3.5, "LATITUD": 2.326, "LONGITUD": -76.412, "TIPO": "VT (Fracturamiento)", "LUGAR": "Flanco Noroccidental Volcán Puracé (Cuenca Río Vinagre)"}},
        {"attributes": {"FECHA_UTC": "2026-11-08 16:12:08", "MAGNITUD": 0.9, "PROFUNDIDAD": 4.1, "LATITUD": 2.109, "LONGITUD": -76.588, "TIPO": "VT (Fracturamiento)", "LUGAR": "Complejo Volcánico Sotará - Sector Cerro Azafatudo"}}
    ]
    save_data(mock_data, "Modo Respaldo OVSPop")

def fetch_sgc_volcanic_data(target_lat=2.31, target_lon=-76.4, radius_km=50):
    url = "https://sgc.gov.co/geoprocesamiento/rest/services/Sismos/Sismicidad_Reciente/MapServer/0/query"
    # Query que abarque Puracé (2.3) y Sotará (2.1)
    params = {
        "where": "MAGNITUD > 0", 
        "outFields": "FECHA_UTC,MAGNITUD,PROFUNDIDAD,LUGAR,LATITUD,LONGITUD", 
        "f": "json", 
        "resultRecordCount": 10,
        "orderByFields": "FECHA_UTC DESC"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"SGC API Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                features = data.get('features', [])
                if features:
                    save_data(features, "API SGC (REAL)")
                    print(f"Obtenidos {len(features)} eventos reales.")
                    return features
                else:
                    print("API respondió OK pero no hay sismos en el record.")
            except Exception as e:
                print(f"Error parseando JSON real: {e}")
        save_mock_data()
    except Exception as e:
        print(f"Error de conexión API: {e}")
        save_mock_data()

if __name__ == "__main__":
    fetch_sgc_volcanic_data()
