# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = r"C:\Copernico"
ART_DIR = r"C:\Users\JENNER ZUÑIGA\.gemini\antigravity\brain\b756e494-6c73-4cd4-857f-7eb1e6e2c85a"

# Leer matriz NDVI real de Samanga Baja (402 x 400) en Big-Endian (>f4)
ndvi_path = os.path.join(DATA_DIR, "Mapa_NDVI_Samanga_2026.data", "band_1.img")
raw_ndvi = np.fromfile(ndvi_path, dtype=">f4").reshape((402, 400))
ndvi = np.where((np.isfinite(raw_ndvi)) & (raw_ndvi > 0.05) & (raw_ndvi <= 1.0), raw_ndvi, np.nan)
mean_val = float(np.nanmean(ndvi))
ndvi_clean = np.nan_to_num(ndvi, nan=mean_val)

lat_min, lon_min = 2.382871, -76.587846
lat_max, lon_max = 2.418983, -76.551913

fig, ax = plt.subplots(figsize=(9.5, 8.2), dpi=220)
fig.patch.set_facecolor("#0b0e14")
ax.set_facecolor("#0b0e14")

im = ax.imshow(
    ndvi_clean,
    cmap="RdYlGn",
    vmin=0.25,
    vmax=0.95,
    extent=[lon_min, lon_max, lat_min, lat_max],
    interpolation="bilinear"
)

# Marcar punto central de Samanga Baja y Punto de Referencia Estable PS
ax.scatter([-76.56997], [2.40095], c="#00d2ff", s=90, edgecolors="white", linewidths=1.8, zorder=5, label="Centro Vereda Samanga Baja (2.4010°N, -76.5700°W)")
ax.scatter([-76.58704], [2.40542], c="#ffcc00", marker="*", s=140, edgecolors="black", linewidths=1.0, zorder=5, label="Punto Referencia Estable Radar (ASI = 1.00)")

ax.set_title(
    f"MAPA DE VIGOR VEGETATIVO Y CAFETALERO (NDVI - 10 m)\nVereda Samanga Baja, Popayán (Cauca) | Media Territorial: {mean_val:.3f}",
    color="white",
    fontsize=12.5,
    fontweight="bold",
    pad=14
)
ax.set_xlabel("Longitud Oeste (°W - WGS84)", color="#c9d1d9", fontsize=10)
ax.set_ylabel("Latitud Norte (°N - WGS84)", color="#c9d1d9", fontsize=10)
ax.tick_params(colors="#c9d1d9", labelsize=9)
ax.grid(color="white", linestyle="--", linewidth=0.4, alpha=0.25)

for spine in ax.spines.values():
    spine.set_edgecolor("#30363d")

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.035)
cbar.set_label("Índice de Vegetación de Diferencia Normalizada (NDVI = [B08 - B04] / [B08 + B04])", color="white", fontsize=9.5)
cbar.ax.yaxis.set_tick_params(color="white", labelcolor="white", labelsize=9)

leg = ax.legend(loc="lower left", facecolor="#161b22", edgecolor="#30363d", fontsize=8.5, labelcolor="white")

plt.tight_layout()
out_local = os.path.join(DATA_DIR, "Mapa_NDVI_Samanga_Baja_AltaRes_2026.png")
out_art = os.path.join(ART_DIR, "Mapa_NDVI_Samanga_Baja_AltaRes_2026.png")
plt.savefig(out_local, facecolor=fig.get_facecolor(), dpi=220)
plt.savefig(out_art, facecolor=fig.get_facecolor(), dpi=220)
plt.close(fig)

# Actualizar también samanga_ndvi_overlay.png con la misma paleta RdYlGn para el mapa interactivo Leaflet
plt.imsave(os.path.join(DATA_DIR, "samanga_ndvi_overlay.png"), ndvi_clean, cmap="RdYlGn", vmin=0.25, vmax=0.95)
print("OK:", out_local)
