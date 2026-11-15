# Proyecto: Vigilancia Volcánica e Hidrológica Samanga Baja

Este repositorio contiene las herramientas técnicas para la descarga y el análisis de datos satelitales en el marco de la convocatoria MinCiencias 2026.

## 🚀 Inicio Rápido

### 1. Requisitos
- Python 3.8+
- Registro en [Copernicus Data Space Ecosystem](https://identity.dataspace.copernicus.eu/).

### 2. Instalación
```bash
pip install -r requirements.txt
```

### 3. Configuración
Copia el archivo `.env.example` a `.env` y añade tus credenciales:
```bash
cp .env.example .env
```

### 4. Ejecución
Para descargar la imagen Sentinel-1 más reciente sobre Samanga Baja:
```bash
python download_sar.py
```

---

## 📊 Plan de Análisis (IA + Sentinel)

### A. Mapa de Deformación del Terreno (D-InSAR)
- **Objetivo:** Detección de movimientos milimétricos en el Volcán Puracé y laderas inestables.
- **Técnica:** Comparación de patrones de fase entre dos adquisiciones SLC.
- **Alerta:** Formación de franjas de interferencia ("ojos") que indican inflación volcánica o deslizamientos inminentes.

### B. Análisis de Coherencia
- **Objetivo:** Identificar cambios bruscos en la cobertura del suelo (derrumbes, inundaciones).
- **Interpretación:** 
    - **Baja coherencia (Negro):** Zonas de cambio drástico.
    - **Alta coherencia (Blanco):** Zonas estables.

### C. Monitoreo Óptico (Sentinel-2)
- **NDVI:** Salud de cultivos de café y estrés hídrico.
- **Alertas Tempranas:** Sequía agrícola y cambios en la vegetación por actividad volcánica.

---
---

## 🛠️ Metodología (Copernicus Browser)

### Herramientas Estratégicas:
1. **Sentinel-1/2:** Radar para movimiento de tierras y óptico para salud de cultivos.
2. **Scripts Personalizados:** Desarrollo de algoritmos NDVI/NDWI adaptados a la zona.
3. **Perfil de Elevación:** Modelado de riesgos de lahares volcánicos y rutas de evacuación.
4. **Análisis Estadístico:** Monitoreo histórico de caudales y sequía para la JAC.

> *"El proyecto integra visualización 3D y análisis temporal para transformar datos satelitales en decisiones comunitarias inmediatas."*

## 📝 Resumen para la Propuesta

> *"La estrategia de procesamiento utiliza los endpoints actualizados de la API de Copernicus Data Space para la adquisición sistemática de productos Sentinel-1. Posteriormente, aplicamos técnicas de Interferometría Diferencial (D-InSAR) asistidas por Machine Learning para generar mapas de deformación superficial con precisión milimétrica, permitiendo discernir entre movimientos del suelo asociados a inestabilidad de laderas (derrubios) o actividad magmática (inflación volcánica en Puracé/Sotará)."*
