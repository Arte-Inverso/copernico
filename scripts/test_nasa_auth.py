import asf_search as asf
import os

print("Probando autenticación con NASA Earthdata (netrc / variables de entorno)...")

try:
    user = os.environ.get("EARTHDATA_USER")
    pwd = os.environ.get("EARTHDATA_PASSWORD")
    if user and pwd:
        session = asf.ASFSession().auth_with_creds(user, pwd)
    else:
        session = asf.ASFSession().auth_with_netrc()
    print("✓ Autenticación exitosa con los servidores de NASA Earthdata.")
except Exception as e:
    print("✗ Error de autenticación:", e)
