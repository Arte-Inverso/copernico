import os
import requests
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv('CDSE_USER')
PASSWORD = os.getenv('CDSE_PASSWORD')

if not USER or not PASSWORD:
    print("Error: Credenciales no encontradas en .env")
    exit()

# IDs encontrados en la búsqueda previa (3 imágenes históricas)
PRODUCTS = [
    {"date": "2026-03-16", "id": "8c00d7ea-64fd-4cd2-aec9-fe7c2a66490d", "name": "S1C_IW_SLC__1SDV_20260316T105045_20260316T105113_006788_00DB83_BEA4.SAFE"},
    {"date": "2026-03-09", "id": "32d188e4-a0a3-4c4e-b2e2-e65ac2a91d4e", "name": "S1C_IW_SLC__1SDV_20260309T232049_20260309T232116_006694_00D831_16D0.SAFE"},
    {"date": "2026-03-04", "id": "4e2d2069-a404-4be7-bd5a-9a5b6f514fc7", "name": "S1C_IW_SLC__1SDV_20260304T105044_20260304T105112_006613_00D588_C70E.SAFE"}
]

# --- DESCARGAS ---
for p in PRODUCTS:
    print(f"\n--- Preparando: {p['date']} ({p['id']}) ---")
    filename = f"c:\\Copernico\\{p['name']}.zip"
    
    # Solo saltar si el archivo ya tiene el tamaño esperado (aprox 7GB+)
    if os.path.exists(filename) and os.path.getsize(filename) > 7000000000:
        print(f"El archivo {filename} ya está completo, saltando...")
        continue
    
    if os.path.exists(filename):
        print(f"Archivo {filename} incompleto ({os.path.getsize(filename)/1e9:.2f} GB), reintentando descarga...")
        # Eliminamos el incompleto para evitar corrupción al concatenar sin Range headers
        os.remove(filename)

    # 1. Obtener Token fresco (evita expiración en descargas largas)
    print("Autenticando...")
    auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    auth_response = requests.post(auth_url, data={
        'client_id': 'cdse-public',
        'username': USER,
        'password': PASSWORD,
        'grant_type': 'password'
    })
    
    if auth_response.status_code != 200:
        print(f"Error de autenticación para {p['date']}: {auth_response.status_code}")
        continue
        
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Iniciar Descarga
    print(f"Iniciando descarga: {p['date']}")
    download_url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({p['id']})/$value"
    
    try:
        with requests.get(download_url, headers=headers, stream=True) as r:
            r.raise_for_status()
            downloaded = 0
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024 * 8): # 8MB chunks
                    f.write(chunk)
                    downloaded += len(chunk)
                    print(f"Descargado: {downloaded / (1024 * 1024):.2f} MB", end='\r')
        print(f"\n¡Descarga completada!: {filename}")
    except Exception as e:
        print(f"Error al descargar {p['date']}: {e}")

print("\n--- Todas las descargas solicitadas han finalizado ---")
