import asf_search as asf
import os

print("Probando autenticación con NASA Earthdata (usuario: arteinverso)...")

try:
    session = asf.ASFSession().auth_with_creds('arteinverso', 'LS?wKZ#KkE^R8Zx')
    print("✓ Autenticación exitosa con los servidores de NASA Earthdata.")
except Exception as e:
    print("✗ Error de autenticación:", e)
