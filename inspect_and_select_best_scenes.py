# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET
import requests
from dotenv import load_dotenv

load_dotenv(r"C:\Copernico\.env")
USER = os.getenv('CDSE_USER')
PASSWORD = os.getenv('CDSE_PASSWORD')

def get_token():
    r = requests.post(
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data={'client_id': 'cdse-public', 'username': USER, 'password': PASSWORD, 'grant_type': 'password'},
        timeout=20
    )
    r.raise_for_status()
    return r.json()['access_token']

token = get_token()
headers = {'Authorization': f'Bearer {token}'}

S1_SCENES = [
    {
        "date": "2026-11-06",
        "id": "eb526191-524b-46d1-81fe-25ce52d6955f",
        "name": "S1C_IW_SLC__1SDV_20261106T105051_20261106T105119_010215_014663_F21F.SAFE"
    },
    {
        "date": "2026-10-31",
        "id": "06d3120c-fa9e-4360-bc40-862259db29a7",
        "name": "S1D_IW_SLC__1SDV_20261031T105104_20261031T105132_005258_009FEA_9725.SAFE"
    },
    {
        "date": "2026-10-25",
        "id": "e3855cea-bfc0-4bcc-9da1-60f4d864dc2b",
        "name": "S1C_IW_SLC__1SDV_20261025T105051_20261025T105119_010040_01409C_B3D0.SAFE"
    }
]

print("=== 1. DESCARGANDO METADATOS XML DE ESCENAS SENTINEL-1 (OCT-NOV 2026) ===")
for sc in S1_SCENES:
    safe_dir = os.path.join(r"C:\Copernico", sc["name"])
    ann_dir = os.path.join(safe_dir, "annotation")
    os.makedirs(ann_dir, exist_ok=True)

    # Download manifest.safe
    man_path = os.path.join(safe_dir, "manifest.safe")
    if not os.path.exists(man_path):
        url_man = f"https://download.dataspace.copernicus.eu/odata/v1/Products({sc['id']})/Nodes({sc['name']})/Nodes(manifest.safe)/$value"
        rm = requests.get(url_man, headers=headers, timeout=30)
        if rm.status_code == 200:
            with open(man_path, "wb") as f:
                f.write(rm.content)

    # List annotation files
    url_ann = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({sc['id']})/Nodes({sc['name']})/Nodes(annotation)/Nodes"
    ra = requests.get(url_ann, headers=headers, timeout=20).json()
    for node in ra.get("result", []):
        nid = node["Id"]
        if nid.endswith(".xml") and ("iw1-slc-vv" in nid or "iw2-slc-vv" in nid):
            local_xml = os.path.join(ann_dir, nid)
            if not os.path.exists(local_xml):
                u_xml = f"https://download.dataspace.copernicus.eu/odata/v1/Products({sc['id']})/Nodes({sc['name']})/Nodes(annotation)/Nodes({nid})/$value"
                rx = requests.get(u_xml, headers=headers, timeout=30)
                if rx.status_code == 200:
                    with open(local_xml, "wb") as f:
                        f.write(rx.content)
            # Parse XML coverage
            tree = ET.parse(local_xml)
            root = tree.getroot()
            lats = [float(x.text) for x in root.findall(".//geolocationGridPoint/latitude")]
            lons = [float(x.text) for x in root.findall(".//geolocationGridPoint/longitude")]
            print(f"[{sc['date']}] {nid}: Lat [{min(lats):.3f}, {max(lats):.3f}] | Lon [{min(lons):.3f}, {max(lons):.3f}]")

print("\n=== 2. BUSCANDO ESCENAS SENTINEL-2 L2A MÁS LIMPIAS (2026) ===")
url_cat = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
q_s2 = (
    "Collection/Name eq 'SENTINEL-2' and "
    "contains(Name,'T18NUH') and contains(Name,'MSIL2A') and "
    "ContentDate/Start gt 2026-06-01T00:00:00.000Z and "
    "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/Value lt 38.0)"
)
r_s2 = requests.get(url_cat, params={'$filter': q_s2, '$top': 10, '$orderby': 'ContentDate/Start desc', '$expand': 'Attributes'}, timeout=30).json()
for p in r_s2.get('value', []):
    cc = next((a['Value'] for a in p.get('Attributes', []) if a['Name'] == 'cloudCover'), 999)
    print(f"S2: {p['ContentDate']['Start'][:19]} | Nubes: {cc:.1f}% | {p['Name']} | ID: {p['Id']}")
