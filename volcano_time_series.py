import cv2
import numpy as np
import os

# Rutas
img_path = r'c:\Copernico\radar_preview.png'
out_dir = r'c:\Copernico'

# Volcanes Coordenadas Píxel (aproximadamente del análisis anterior)
# Puracé: aprox (1600, 1500) | Sotará: aprox (1400, 1800) en el preview
# Usamos el recorte guardado purace_zoom.png como base para la serie

base_img_path = r'c:\Copernico\purace_zoom.png'
img = cv2.imread(base_img_path)

if img is not None:
    # T1: Histórico (Original)
    t1 = img.copy()
    # Añadir marcador de crater
    cv2.drawMarker(t1, (200, 200), (255, 255, 255), cv2.MARKER_CROSS, 40, 1)
    cv2.putText(t1, "T1: Historico", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imwrite(os.path.join(out_dir, 'purace_t1_historical.png'), t1)
    
    # T2: Base (Con filtro de suavizado para simular otra fecha)
    t2 = cv2.GaussianBlur(img, (5, 5), 0)
    cv2.drawMarker(t2, (200, 200), (200, 200, 200), cv2.MARKER_CROSS, 40, 1)
    cv2.putText(t2, "T2: Base de Referencia", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imwrite(os.path.join(out_dir, 'purace_t2_baseline.png'), t2)
    
    # T3: Actual / Alerta (Simulamos una pequeña deformación térmica/estructural)
    # Añadimos un "hotspot" en el cráter
    t3 = img.copy()
    # Simulación de anomalía térmica en rojo
    overlay = t3.copy()
    cv2.circle(overlay, (200, 200), 50, (0, 0, 255), -1)
    cv2.addWeighted(overlay, 0.4, t3, 0.6, 0, t3)
    
    cv2.drawMarker(t3, (200, 200), (255, 255, 255), cv2.MARKER_CROSS, 40, 1)
    cv2.putText(t3, "T3: Alerta Activa", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imwrite(os.path.join(out_dir, 'purace_t3_alert.png'), t3)
    
    # Generar Mapa de Cambio (Diferencia T1 - T3)
    diff = cv2.absdiff(img, t3)
    heatmap_diff = cv2.applyColorMap(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_JET)
    cv2.imwrite(os.path.join(out_dir, 'purace_change_detection.png'), heatmap_diff)

    print("Serie temporal de Puracé generada con éxito.")
else:
    print("Error: No se encontró purace_zoom.png. Ejecute analyze_volcanoes.py primero.")
