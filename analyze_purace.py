import cv2
import numpy as np
import os

# Rutas
img_path = r'c:\Copernico\radar_preview.png'
out_path = r'c:\Copernico\purace_zoom.png'
out_heatmap = r'c:\Copernico\purace_heatmap.png'

# Coordenadas de la imagen (aproximadas según manifest.safe)
# Note: SLC images are usually mirrored/rotated in quick-looks, 
# but we will assume a standard orientation for this demonstration.
lat_max, lat_min = 4.22, 2.07
lon_max, lon_min = -75.81, -78.04

# Coordenadas del Volcán Puracé
v_lat = 2.317
v_lon = -76.398

# Cargar imagen
img = cv2.imread(img_path)

if img is not None:
    h, w, _ = img.shape
    
    # Mapeo lineal simple (Proyección Geográfica Aproximada)
    # X corresponde a Longitud, Y corresponde a Latitud
    # Nota: Latitud disminuye hacia abajo en la imagen
    
    x_pct = (v_lon - lon_min) / (lon_max - lon_min)
    y_pct = 1.0 - (v_lat - lat_min) / (lat_max - lat_min)
    
    px = int(x_pct * w)
    py = int(y_pct * h)
    
    # Definir un área de interés alrededor del volcán (zoom)
    crop_size = 400
    x1 = max(0, px - crop_size // 2)
    y1 = max(0, py - crop_size // 2)
    x2 = min(w, px + crop_size // 2)
    y2 = min(h, py + crop_size // 2)
    
    purace_crop = img[y1:y2, x1:x2]
    
    # Procesamiento IA en el Zoom
    gray = cv2.cvtColor(purace_crop, cv2.COLOR_BGR2GRAY)
    gray_eq = cv2.equalizeHist(gray)
    heatmap = cv2.applyColorMap(gray_eq, cv2.COLORMAP_MAGMA)
    
    # Guardar resultados
    cv2.imwrite(out_path, purace_crop)
    cv2.imwrite(out_heatmap, heatmap)
    
    print(f"--- Análisis Puracé Completado ---")
    print(f"Píxel central estimado: ({px}, {py})")
    print(f"Zoom guardado en: {out_path}")
else:
    print("Error al cargar la imagen")
