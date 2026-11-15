# -*- coding: utf-8 -*-
"""
Análisis de Inteligencia de Datos - Fase 2 (Vista Previa)
Proyecto: Samanga Sostenible
"""

import os
import requests
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()
USER = os.getenv('CDSE_USER')
PASSWORD = os.getenv('CDSE_PASSWORD')

# Coordenadas Samanga Baja
LON, LAT = -76.56997051901716, 2.4009458302553615
FECHA_FIN = date.today().strftime("%Y-%m-%d")
FECHA_INICIO = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")

def get_token():
    auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    res = requests.post(auth_url, data={'client_id': 'cdse-public', 'username': USER, 'password': PASSWORD, 'grant_type': 'password'})
    return res.json().get('access_token') if res.status_code == 200 else None

def search_sentinel2(token):
    url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    # Buscamos Sentinel-2 con poca nubosidad (<20%)
    filter_q = f"Collection/Name eq 'SENTINEL-2' and OData.CSC.Intersects(area=geography'SRID=4326;POINT({LON} {LAT})') and ContentDate/Start gt {FECHA_INICIO} and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/Value lt 20.0)"
    res = requests.get(url, params={'$filter': filter_q, '$top': 5, '$orderby': 'ContentDate/Start desc'})
    return res.json().get('value', [])

token = get_token()
if token:
    print(f"--- Análisis de Disponibilidad: Samanga Baja (Últimos 30 días) ---")
    results = search_sentinel2(token)
    if results:
        for p in results:
            print(f"- Imagen: {p['Name']}")
            print(f"  Fecha: {p['ContentDate']['Start']}")
            print(f"  ID: {p['Id']}")
            print("-" * 20)
    else:
        print("No se encontraron imágenes con baja nubosidad en los últimos 30 días.")
else:
    print("Error de autenticacion.")
