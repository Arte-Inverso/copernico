import asf_search as asf

print("Probando conexión con ASF NASA...")
results = asf.search(
    platform=asf.PLATFORM.SENTINEL1,
    processingLevel=asf.PRODUCT_TYPE.SLC,
    relativeOrbit=142,
    intersectsWith='POINT(-76.57 2.40)',
    start='2026-01-01',
    end='2026-03-31',
    maxResults=3
)

print(f"✓ Consulta exitosa. Se encontraron {len(results)} escenas disponibles:")
for r in results:
    bytes_val = r.properties.get("bytes", 0)
    size_gb = bytes_val / (1024**3)
    name = r.properties.get("fileName", "Unknown")
    date = r.properties.get("startTime", "")[:10]
    print(f"  • {date} | {name} ({size_gb:.2f} GB)")
