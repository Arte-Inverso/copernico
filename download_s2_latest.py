# -*- coding: utf-8 -*-
import os
import time
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

# Candidatos Sentinel-2 L2A (Noviembre/Octubre 2026 + Escena Libre de Nubes 0.7% Junio 2026)
S2_CANDIDATES = [
    {"date": "2026-11-08", "id": "af9aa7f3-b86d-4a42-897b-008c4c5a238a", "name": "S2A_MSIL2A_20261108T153951_N0513_R068_T18NUH_20261108T214351.SAFE"},
    {"date": "2026-10-27", "id": "1d356160-fe14-4eb0-a2c7-95c9b565b7f4", "name": "S2C_MSIL2A_20261027T153621_N0513_R068_T18NUH_20261027T202008.SAFE"},
    {"date": "2026-09-17", "id": "dd2575ef-506a-496d-b1a8-abb4ab02b341", "name": "S2C_MSIL2A_20260917T153621_N0512_R068_T18NUH_20260917T214908.SAFE"},
    {"date": "2026-06-11", "id": "746361b1-6eab-4891-9f80-03f13b9c8700", "name": "S2B_MSIL2A_20260611T152649_N0512_R025_T18NUH_20260611T203217.SAFE"}
]

out_base = r"C:\Copernico\S2_Updated_2026"
os.makedirs(out_base, exist_ok=True)

for sc in S2_CANDIDATES:
    print(f"\n--- Explorando GRANULE de Sentinel-2 ({sc['date']}) ---")
    u_gran = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({sc['id']})/Nodes({sc['name']})/Nodes(GRANULE)/Nodes"
    rg = requests.get(u_gran, headers=headers, timeout=20).json()
    granules = rg.get("result", [])
    if not granules:
        print("No se encontró GRANULE")
        continue
    gran_id = granules[0]["Id"]
    
    # Listar R10m y R20m
    u_r10 = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({sc['id']})/Nodes({sc['name']})/Nodes(GRANULE)/Nodes({gran_id})/Nodes(IMG_DATA)/Nodes(R10m)/Nodes"
    u_r20 = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({sc['id']})/Nodes({sc['name']})/Nodes(GRANULE)/Nodes({gran_id})/Nodes(IMG_DATA)/Nodes(R20m)/Nodes"
    
    r10_list = requests.get(u_r10, headers=headers, timeout=20).json().get("result", [])
    r20_list = requests.get(u_r20, headers=headers, timeout=20).json().get("result", [])
    
    sc_dir = os.path.join(out_base, sc["date"])
    os.makedirs(sc_dir, exist_ok=True)
    
    # Descargar SCL_20m.jp2 primero para evaluar nubes sobre Samanga Baja
    for item in r20_list:
        fid = item["Id"]
        if "_SCL_20m.jp2" in fid:
            local_f = os.path.join(sc_dir, fid)
            if not os.path.exists(local_f):
                dl_url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({sc['id']})/Nodes({sc['name']})/Nodes(GRANULE)/Nodes({gran_id})/Nodes(IMG_DATA)/Nodes(R20m)/Nodes({fid})/$value"
                r_dl = requests.get(dl_url, headers=headers, timeout=60)
                if r_dl.status_code == 200:
                    with open(local_f, "wb") as f:
                        f.write(r_dl.content)
                    print(f"  [OK] Descargado SCL ({len(r_dl.content)/1024:.1f} KB): {fid}")

    # Para la más reciente (2026-11-08) y la más despejada (2026-06-11 y 2026-10-27), descargar B02, B03, B04, B08 (10m)
    if sc["date"] in ["2026-11-08", "2026-10-27", "2026-06-11"]:
        for item in r10_list:
            fid = item["Id"]
            if any(b in fid for b in ["_B02_10m.jp2", "_B03_10m.jp2", "_B04_10m.jp2", "_B08_10m.jp2"]):
                local_f = os.path.join(sc_dir, fid)
                if os.path.exists(local_f) and os.path.getsize(local_f) > 1000000:
                    print(f"  [SKIP] Ya existe: {fid}")
                    continue
                t0 = time.time()
                dl_url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({sc['id']})/Nodes({sc['name']})/Nodes(GRANULE)/Nodes({gran_id})/Nodes(IMG_DATA)/Nodes(R10m)/Nodes({fid})/$value"
                with requests.get(dl_url, headers=headers, stream=True, timeout=120) as r_dl:
                    r_dl.raise_for_status()
                    total_b = 0
                    with open(local_f, "wb") as f:
                        for chunk in r_dl.iter_content(chunk_size=1024 * 1024 * 4):
                            if chunk:
                                f.write(chunk)
                                total_b += len(chunk)
                dt = max(0.1, time.time() - t0)
                mb = total_b / (1024 * 1024)
                print(f"  [OK] {fid}: {mb:.1f} MB en {dt:.1f}s ({mb/dt:.1f} MB/s)")
