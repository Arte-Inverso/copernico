import os
import requests
from datetime import date
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv('CDSE_USER')
PASSWORD = os.getenv('CDSE_PASSWORD')

# Coordenadas Puracé
LON = -76.56997051901716
LAT = 2.4009458302553615

# --- 1. AUTENTICACIÓN ---
auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
response = requests.post(auth_url, data={
    'client_id': 'cdse-public',
    'username': USER,
    'password': PASSWORD,
    'grant_type': 'password'
})

if response.status_code == 200:
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # --- 2. BÚSQUEDA ---
    search_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    filter_query = (
        f"Collection/Name eq 'SENTINEL-1' and "
        f"OData.CSC.Intersects(area=geography'SRID=4326;POINT({LON} {LAT})') and "
        f"Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/Value eq 'IW_SLC__1S')"
    )
    
    params = {
        '$filter': filter_query,
        '$top': 20,
        '$orderby': 'ContentDate/Start desc'
    }
    
    search_response = requests.get(search_url, params=params)
    if search_response.status_code == 200:
        results = search_response.json()
        print("--- Imágenes Disponibles (Sentinel-1 SLC) ---")
        for p in results.get('value', []):
            print(f"Fecha: {p['ContentDate']['Start']} | ID: {p['Id']} | Name: {p['Name']}")
    else:
        print(f"Error búsqueda: {search_response.status_code}")
else:
    print("Error autenticación.")
