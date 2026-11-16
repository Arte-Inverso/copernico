# ESTADO DE DESARROLLO Y ARQUITECTURA GRAPHIFY — PROYECTO COPERNICO

> **Nota para futuras sesiones:** Este documento registra el estado técnico real, los scripts activos y los pasos inmediatos para retomar el desarrollo sin fricciones.

---

## 📌 1. Estado Actual del Núcleo Físico (100% Real y Operativo)
* **Interferometría Compleja D-InSAR:** Operativa sobre SLC Sentinel-1 (.tiff de 1.5 GB). Script: `scripts/insar_mogi_seismic_inversion_v2.py`.
* **Unwrapping 2D:** Implementado vía Herráez et al. (2002) / `scikit-image`.
* **Inversión Mogi (1958):** Cámara magmática del Puracé estimada a 1.57 km ($\Delta V = 1.47\text{ Mm}^3$).
* **Acoplamiento Sísmico (Hanks-Kanamori 1979):** Catálogo SGC acoplado (99.99% deformación asísmica).
* **Benchmark de Control (6 Días):** Par 10-Mar vs 16-Mar-2026 arrojó media de **`-0.02 mm`** (`scripts/compute_pair_10mar_16mar.py`), certificando que el algoritmo no introduce derivas numéricas.
* **Colocalización Geodésica POVA:** Píxel InSAR extraído a exactamente **10 metros (0.01 km)** de la estación GNSS continua con $\gamma = 0.315$.
* **Validación Ética:** `scripts/validate_gnss_igac_v4_honesto.py` no utiliza datos sintéticos; reporta estado PENDIENTE de datos GNSS reales.
* **Hub 3D WebGL Multi-territorio:** En `http://localhost:8085/modelo_3d_purace.html` (Puracé, Sotará, Samanga Baja con DEM Terrarium).
* **Storytelling Pedagógico:** En `http://localhost:8085/pedagogical_storytelling.html` y dentro de la pestaña del dashboard principal.

---

## 🚀 2. Próximos Pasos Prioritarios para Continuar el Desarrollo
1. **Stack Multitemporal (20+ SLCs Sentinel-1):**
   - Descarga automatizada y alineamiento de la serie 2023–2026 en Track 142 Descendente.
2. **Corrección Atmosférica ERA5 / PyAPS3:**
   - Incorporar corrección troposférica local para eliminar retardos por vapor de agua andino.
3. **Automatización de Ingesta Sísmica SGC:**
   - Programar cron o sincronización periódica automática vía API/WebService FDSN del SGC.
4. **Descomposición 2D / 3D de Vectores de Desplazamiento:**
   - Combinar Track Descendente (142) con Track Ascendente para separar movimiento vertical de horizontal.

---

## 🛠️ 3. Scripts Principales del Repositorio
| Script | Función |
|---|---|
| `scripts/insar_mogi_seismic_inversion_v2.py` | Motor D-InSAR real + Mogi + colocalización POVA (10 m) |
| `scripts/compute_pair_10mar_16mar.py` | Benchmark de control de 6 días (-0.02 mm) |
| `scripts/validate_gnss_igac_v4_honesto.py` | Módulo de validación transparente sin datos simulados |
| `scripts/generate_all_3d_territories.py` | Generador de mallas DEM y escenas 3D WebGL |
| `scripts/generate_pedagogical_dashboard.py` | Generador del storytelling narrativo visual e infografías |
| `sgc_live_data.py` | Ingesta, clasificación y cálculo de energía sísmica OVSPop/SGC |
