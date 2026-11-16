# -*- coding: utf-8 -*-
"""
compute_pair_10mar_16mar.py — Procesa par interferométrico S1A (10-Mar-2026) vs S1C (16-Mar-2026)
Intervalo temporal: 6 días (Banda C Sentinel-1, subswath IW2-VV sobre Popayán / Samanga Baja)
"""

import os
import tifffile
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skimage.restoration import unwrap_phase

tiff_a = r"C:\Copernico\S1A_IW_SLC__1SDV_20260310T105208_20260310T105236_063564_07FCFB_FA9C.SAFE\measurement\s1a-iw2-slc-vv-20260310t105208-20260310t105236-063564-07fcfb-005.tiff"
tiff_c = r"C:\Copernico\S1C_IW_SLC__1SDV_20260316T105045_20260316T105113_006788_00DB83_BEA4.SAFE\measurement\s1c-iw2-slc-vv-20260316t105045-20260316t105113-006788-00db83-005.tiff"

out_dir = r"C:\Users\JENNER ZUÑIGA\copernico\outputs\pair_6days"
os.makedirs(out_dir, exist_ok=True)

print("1. Cargando porciones coincidentes de SLC complejos (10-Mar vs 16-Mar)...")
# S1A Line 0-1502 corresponde a S1C Line 13518-15019 (~2.42° a ~2.25° Lat)
# Cargamos un bloque de 1200 líneas x 4000 píxeles alrededor de Samanga Baja
mem_a = tifffile.imread(tiff_a, key=0)
slc_a = mem_a[0:1200, 0:4000]
del mem_a

mem_c = tifffile.imread(tiff_c, key=0)
slc_c = mem_c[13500:14700, 0:4000]
del mem_c

print("   SLC A shape:", slc_a.shape, "dtype:", slc_a.dtype)
print("   SLC C shape:", slc_c.shape, "dtype:", slc_c.dtype)

# Convertir a complejo si está en int16 (I, Q)
if slc_a.dtype != np.complex64 and slc_a.dtype != np.complex128:
    c_a = slc_a.astype(np.float32)
    c_c = slc_c.astype(np.float32)
else:
    c_a = slc_a
    c_c = slc_c

print("2. Calculando interferograma complejo I = s1 * conj(s2)...")
interferogram = c_a * np.conj(c_c)
phase_wrapped = np.angle(interferogram)

print("3. Calculando coherencia interferométrica con multilook espacial 7x7...")
ksize = 7
kernel = np.ones((ksize, ksize), dtype=np.float32) / (ksize * ksize)

e_cross = cv2.filter2D(interferogram.real, -1, kernel) + 1j * cv2.filter2D(interferogram.imag, -1, kernel)
p1 = cv2.filter2D((np.abs(c_a)**2).astype(np.float32), -1, kernel)
p2 = cv2.filter2D((np.abs(c_c)**2).astype(np.float32), -1, kernel)

coherence = np.abs(e_cross) / (np.sqrt(p1 * p2) + 1e-8)
coherence = np.clip(coherence, 0.0, 1.0)
mean_coh = np.mean(coherence)
print(f"   Coherencia media a 6 días: {mean_coh:.3f}")

print("4. Desenrollando fase (unwrap_phase - Herráez 2002)...")
# Reducir resolución para unwrapping rápido y robusto
down_factor = 4
phase_sub = cv2.resize(phase_wrapped, (phase_wrapped.shape[1]//down_factor, phase_wrapped.shape[0]//down_factor), interpolation=cv2.INTER_AREA)
coh_sub = cv2.resize(coherence, (coherence.shape[1]//down_factor, coherence.shape[0]//down_factor), interpolation=cv2.INTER_AREA)

mask = coh_sub > 0.15
unwrapped_sub = unwrap_phase(np.ma.masked_array(phase_sub, ~mask))
unwrapped = cv2.resize(unwrapped_sub.filled(0), (phase_wrapped.shape[1], phase_wrapped.shape[0]), interpolation=cv2.INTER_LINEAR)

# Longitud de onda C-band: 55.4657 mm
wavelength = 55.4657
d_los_mm = -(wavelength / (4.0 * np.pi)) * unwrapped

print(f"   Desplazamiento LOS 6 días: Min={np.min(d_los_mm):.2f} mm, Max={np.max(d_los_mm):.2f} mm, Media={np.mean(d_los_mm):.2f} mm")

print("5. Generando visualización...")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

im0 = axes[0].imshow(phase_wrapped, cmap='hsv', aspect='auto')
axes[0].set_title("Fase Envuelta (10-Mar vs 16-Mar, 6 días)\nInterferograma Crudo")
plt.colorbar(im0, ax=axes[0], label="Radianes (-π, π)")

im1 = axes[1].imshow(coherence, cmap='viridis', vmin=0, vmax=1, aspect='auto')
axes[1].set_title(f"Coherencia Espacial γ (Media = {mean_coh:.2f})\nConservación de Fase en 6 días")
plt.colorbar(im1, ax=axes[1], label="Coherencia [0, 1]")

im2 = axes[2].imshow(d_los_mm, cmap='coolwarm', vmin=-15, vmax=15, aspect='auto')
axes[2].set_title("Deformación LOS Unwrapped (Herráez 2002)\nDesplazamiento [mm] en 6 días")
plt.colorbar(im2, ax=axes[2], label="d_LOS [mm]")

plt.tight_layout()
out_plot = os.path.join(out_dir, "insar_pair_6days_samanga_popayan.png")
plt.savefig(out_plot, dpi=200)
plt.close()

# Guardar copia en dashboard
dash_plot = r"C:\Users\JENNER ZUÑIGA\copernico\dashboard\insar_pair_6days_samanga_popayan.png"
import shutil
shutil.copy(out_plot, dash_plot)

print(f"✓ Análisis de 6 días completado exitosamente: {out_plot}")
