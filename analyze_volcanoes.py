import cv2
import numpy as np
import os

# Rutas
img_path = r'c:\Copernico\radar_preview.png'
out_dir = r'c:\Copernico'

# Coordenadas de la imagen (aproximadas según manifest.safe)
lat_max, lat_min = 4.22, 2.07
lon_max, lon_min = -75.81, -78.04

# Volcanes
volcanoes = {
    'purace': {'lat': 2.317, 'lon': -76.398},
    'sotara': {'lat': 2.107, 'lon': -76.590}
}

img = cv2.imread(img_path)

if img is not None:
    h, w, _ = img.shape
    
    for name, coords in volcanoes.items():
        v_lat, v_lon = coords['lat'], coords['lon']
        
        # Mapeo
        x_pct = (v_lon - lon_min) / (lon_max - lon_min)
        y_pct = 1.0 - (v_lat - lat_min) / (lat_max - lat_min)
        
        px = int(x_pct * w)
        py = int(y_pct * h)
        
        # Zoom
        crop_size = 400
        x1 = max(0, px - crop_size // 2)
        y1 = max(0, py - crop_size // 2)
        x2 = min(w, px + crop_size // 2)
        y2 = min(h, py + crop_size // 2)
        
        crop = img[y1:y2, x1:x2]
        
        # 4. Ajustes Visuales
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray_eq = cv2.equalizeHist(gray)
        
        # Puracé = MAGMA (Rojo/Naranja) | Sotará = VIRIDIS (Verde/Amarillo/Morado)
        cmap = cv2.COLORMAP_MAGMA if name == 'purace' else cv2.COLORMAP_VIRIDIS
        heatmap = cv2.applyColorMap(gray_eq, cmap)

        # 5. Añadir Marcadores Visuales (Crosshair)
        cx, cy = crop_size // 2, crop_size // 2
        color_marker = (255, 255, 255) # Blanco para contraste
        cv2.line(heatmap, (cx - 20, cy), (cx + 20, cy), color_marker, 1)
        cv2.line(heatmap, (cx, cy - 20), (cx, cy + 20), color_marker, 1)
        cv2.circle(heatmap, (cx, cy), 5, color_marker, 1)

        # 6. Etiquetas de Texto
        font = cv2.FONT_HERSHEY_SIMPLEX
        label = f"{name.upper()} ({coords['lat']}, {coords['lon']})"
        cv2.putText(heatmap, label, (10, 30), font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(heatmap, "SAT-I Samanga - Radar Analysis", (10, 390), font, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
        
        # 7. Deep Zoom (Simulación de Alta Resolución 2m)
        deep_crop_size = 100
        dx1 = max(0, px - deep_crop_size // 2)
        dy1 = max(0, py - deep_crop_size // 2)
        dx2 = min(w, px + deep_crop_size // 2)
        dy2 = min(h, py + deep_crop_size // 2)
        
        deep_crop = img[dy1:dy2, dx1:dx2]
        # Resampling bi-cúbico para suavizar la visualización en zoom
        deep_zoom = cv2.resize(deep_crop, (400, 400), interpolation=cv2.INTER_CUBIC)
        
        # Añadir etiquetas al deep zoom
        cv2.putText(deep_zoom, "DEEP ZOOM - CRATER DETAIL", (10, 30), font, 0.6, (0, 255, 255), 2)
        cv2.drawMarker(deep_zoom, (200, 200), (0, 255, 255), cv2.MARKER_TILTED_CROSS, 20, 2)
        
        # Guardar
        cv2.imwrite(os.path.join(out_dir, f'{name}_zoom.png'), crop)
        cv2.imwrite(os.path.join(out_dir, f'{name}_heatmap.png'), heatmap)
        cv2.imwrite(os.path.join(out_dir, f'{name}_deep_zoom.png'), deep_zoom)
        
        print(f"Analizado: {name} en píxel ({px}, {py}) - Deep Zoom generado.")
else:
    print("Error al cargar la imagen")
