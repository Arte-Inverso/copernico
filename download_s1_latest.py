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

# Par Interferométrico Nuevo: 25 de Octubre de 2026 vs 06 de Noviembre de 2026 (Mismo Satélite S1C, Track 142 DESC)
S1_PAIR_NOV2026 = [
    {
        "date": "2026-11-06",
        "id": "eb526191-524b-46d1-81fe-25ce52d6955f",
        "name": "S1C_IW_SLC__1SDV_20261106T105051_20261106T105119_010215_014663_F21F.SAFE"
    },
    {
        "date": "2026-10-25",
        "id": "e3855cea-bfc0-4bcc-9da1-60f4d864dc2b",
        "name": "S1C_IW_SLC__1SDV_20261025T105051_20261025T105119_010040_01409C_B3D0.SAFE"
    }
]

for sc in S1_PAIR_NOV2026:
    print(f"\n=== Descargando Subswaths Radar SLC (IW1 VV + IW2 VV) para {sc['date']} ===")
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}

    safe_dir = os.path.join(r"C:\Copernico", sc["name"])
    meas_dir = os.path.join(safe_dir, "measurement")
    os.makedirs(meas_dir, exist_ok=True)

    url_meas = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({sc['id']})/Nodes({sc['name']})/Nodes(measurement)/Nodes"
    rm = requests.get(url_meas, headers=headers, timeout=20).json()
    for node in rm.get("result", []):
        nid = node["Id"]
        # Descargamos IW1-VV (Volcán Puracé & Coconucos) e IW2-VV (Vereda Samanga Baja & Popayán)
        if nid.endswith(".tiff") and ("iw1-slc-vv" in nid or "iw2-slc-vv" in nid):
            local_tiff = os.path.join(meas_dir, nid)
            expected_len = node.get("ContentLength", 0)
            if os.path.exists(local_tiff) and os.path.getsize(local_tiff) >= expected_len * 0.99 and expected_len > 0:
                print(f"  [SKIP] Ya existe completo: {nid} ({os.path.getsize(local_tiff)/(1024**2):.1f} MB)")
                continue

            print(f"  -> Descargando {nid} ({expected_len/(1024**2):.1f} MB)...")
            token = get_token()
            headers = {'Authorization': f'Bearer {token}'}
            dl_url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({sc['id']})/Nodes({sc['name']})/Nodes(measurement)/Nodes({nid})/$value"
            t0 = time.time()
            with requests.get(dl_url, headers=headers, stream=True, timeout=180) as r_dl:
                r_dl.raise_for_status()
                downloaded = 0
                with open(local_tiff, "wb") as f:
                    for chunk in r_dl.iter_content(chunk_size=1024 * 1024 * 8):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
            dt = max(0.1, time.time() - t0)
            mb = downloaded / (1024 * 1024)
            print(f"  [OK] {nid}: {mb:.1f} MB descargados en {dt:.1f}s ({mb/dt:.1f} MB/s)")
