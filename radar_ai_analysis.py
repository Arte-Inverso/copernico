import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# Rutas locales (evitando ZUÑIGA para compatibilidad de librerías)
img_path = r'c:\Copernico\radar_preview.png'
out_dir = r'c:\Copernico'

# Cargar imagen en escala de grises
img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

if img is not None:
    # 1. Análisis de Histograma (Distribución de Energía Radar)
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    plt.figure(figsize=(10, 4))
    plt.plot(hist, color='red')
    plt.title('Distribución de Energía Radar (Firma de Superficie)')
    plt.xlabel('Intensidad')
    plt.ylabel('Frecuencia')
    plt.grid(True)
    plt.savefig(os.path.join(out_dir, 'radar_histogram.png'))
    plt.close()

    # 2. Mapa de Calor (Simulación de Firma Térmica/Riesgo)
    img_eq = cv2.equalizeHist(img)
    heatmap = cv2.applyColorMap(img_eq, cv2.COLORMAP_JET)
    cv2.imwrite(os.path.join(out_dir, 'radar_heatmap.png'), heatmap)

    # 3. Detección de Bordes (Lineamientos Geológicos)
    edges = cv2.Canny(img, 50, 150)
    edges_inv = cv2.bitwise_not(edges)
    cv2.imwrite(os.path.join(out_dir, 'radar_edges.png'), edges_inv)

    print("--- Análisis IA Completado ---")
else:
    print(f"Error: No se pudo cargar la imagen desde {img_path}")
