# -*- coding: utf-8 -*-
"""
Cliente de Descarga Automática - Convocatoria MinCiencias 2026
Proyecto: Vigilancia Volcánica e Hidrológica Samanga Baja
Actualización: Compatible con API Copernicus Data Space (Marzo 2026)
"""

import os
import requests
import json
from datetime import date
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- CONFIGURACIÓN ---
USER = os.getenv('CDSE_USER')
PASSWORD = os.getenv('CDSE_PASSWORD')

if not USER or not PASSWORD or USER == 'tu_usuario_registrado':
    print("Error: Configura tus credenciales en el archivo .env (copia .env.example)")
    exit()

# Coordenadas de Samanga Baja (Volcanes Puracé/Sotará)
LON = -76.56997051901716
LAT = 2.4009458302553615

# Fecha de hoy para buscar imágenes recientes
FECHA_HOY = date.today().strftime("%Y-%m-%d")
FECHA_INICIO = "2026-01-01"  # Buscamos imágenes de este año

print(f"--- Buscando imágenes sobre Samanga Baja ({LAT}, {LON}) ---")

# --- 1. AUTENTICACIÓN EN LA NUEVA API ---
auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
response = requests.post(auth_url, data={
    'client_id': 'cdse-public',
    'username': USER,
    'password': PASSWORD,
    'grant_type': 'password'
})

if response.status_code != 200:
    print(f"Error de autenticación ({response.status_code}). Verifica tu usuario de Copernicus Data Space.")
    print(response.text)
    exit()

token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# --- 2. BÚSQUEDA DE PRODUCTOS (Sentinel-1 Radar) ---
search_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

# Filtro OData: Sentinel-1, Tipo SLC (para InSAR), Intersecta coordenadas
# Nota: El productType exacto para SLC es 'IW_SLC__1S'.
filter_query = (
    f"Collection/Name eq 'SENTINEL-1' and "
    f"OData.CSC.Intersects(area=geography'SRID=4326;POINT({LON} {LAT})') and "
    f"Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/Value eq 'IW_SLC__1S') and "
    f"ContentDate/Start gt {FECHA_INICIO}"
)

params = {
    '$filter': filter_query,
    '$top': 1, # Traemos solo la más reciente
    '$orderby': 'ContentDate/Start desc'
}

search_response = requests.get(search_url, params=params)
if search_response.status_code != 200:
    print(f"Error en la búsqueda ({search_response.status_code}).")
    print(search_response.text)
    exit()

results = search_response.json()

if 'value' in results and len(results['value']) > 0:
    producto = results['value'][0]
    product_id = producto['Id']
    product_name = producto['Name']
    print(f"¡Imagen encontrada!: {product_name}")
    
    # --- 3. DESCARGA AUTOMÁTICA ---
    download_url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
    
    # Check size first
    size_mb = producto.get('ContentLength', 0) / (1024 * 1024)
    print(f"Tamaño estimado: {size_mb:.2f} MB")
    
    if size_mb > 1000:
        print("Aviso: El archivo es un SLC completo (>1GB). La descarga en este ambiente puede ser limitada.")
    
    print("Iniciando descarga (archivo pesado, puede tardar minutos)...")
    # Stream the download to avoid memory issues with large files
    download_response = requests.get(download_url, headers=headers, stream=True)
    
    if download_response.status_code == 200:
        filename = f"{product_name}.zip"
        downloaded = 0
        with open(filename, 'wb') as f:
            for chunk in download_response.iter_content(chunk_size=8192 * 1024): # 8MB chunks
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    print(f"Descargado: {downloaded / (1024 * 1024):.2f} MB", end='\r')
        print(f"\n¡Descarga completada! Archivo guardado: {filename}")
        print("Este archivo contiene el 'Mapa de Radar' crudo para el análisis.")
    else:
        print(f"Error en la descarga ({download_response.status_code}).")
else:
    print("No se encontraron imágenes recientes para estas coordenadas.")
