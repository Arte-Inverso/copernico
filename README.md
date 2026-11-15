# Copernico 2.0 - Sistema de monitoreo satelital MT-InSAR dockerizado

> Sistema de vigilancia volcánica e hidrológica para Samanga Baja, Volcán Puracé y Complejo Volcánico Sotará (Cauca, Colombia).

Esta versión 2.0 transforma el repositorio original en un **entorno reproducible y aislado mediante Docker**, alineado a la investigación en InSAR avanzado (MintPy, StaMPS, TomoSAR, ERA5, NISAR, BIOMASS).

---

## 🚀 Quick Start (5 minutos)

### Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) 20+
- [Docker Compose](https://docs.docker.com/compose/install/) v2+
- 8 GB RAM mínimo (16 GB recomendado)
- 20 GB disco libre
- Cuenta gratuita en [Copernicus Data Space](https://identity.dataspace.copernicus.eu/)

### 1. Clonar y configurar

```bash
git clone https://github.com/Arte-Inverso/copernico.git
cd copernico

# Crear .env con tus credenciales
cp .env.example .env
# Edita .env con tu editor preferido y añade tus credenciales
nano .env
```

### 2. Construir la imagen Docker

```bash
make build
# Primera vez: ~20-30 minutos (descarga Ubuntu, conda, MintPy, SNAP)
# Siguientes veces: ~30 segundos (caché)
```

### 3. Levantar los servicios

```bash
make up-all
```

Esto levanta 3 servicios:

| Servicio | Puerto | Función |
|---|---|---|
| `copernico-dev` | - | CLI + scripts Python |
| `copernico-notebook` | http://localhost:8888 | JupyterLab (token: `copernico-dev`) |
| `copernico-dashboard` | http://localhost:8080 | Dashboard web Leaflet |

### 4. Verificar el entorno

```bash
make shell
# Dentro del contenedor:
./scripts/verify_env.sh
```

### 5. Ejecutar el pipeline completo

```bash
make shell
./scripts/run_pipeline.sh
```

---

## 📁 Estructura del proyecto Dockerizado

```
copernico/
├── docker/
│   ├── Dockerfile                 # Imagen principal (Ubuntu 22.04 + conda + MintPy + SNAP)
│   ├── docker-compose.yml         # Orquestación de servicios
│   └── .dockerignore              # Archivos excluidos de la imagen
├── scripts/
│   ├── entrypoint.sh              # Inicialización del contenedor
│   ├── verify_env.sh              # Verificación post-instalación
│   ├── run_pipeline.sh            # Pipeline completo automatizado
│   ├── download_s1_latest.py     # Descarga Sentinel-1 (Copernicus API)
│   ├── download_s2_latest.py     # Descarga Sentinel-2
│   ├── process_insar.py           # Procesamiento MT-InSAR con MintPy
│   ├── process_s2_updated.py      # NDVI Sentinel-2 sin costuras
│   └── update_dashboard.py        # Regenera datos del dashboard
├── src/                           # Código modular Python
│   ├── __init__.py
│   ├── ingest/                    # Módulos de descarga
│   ├── processing/                # Pipeline InSAR y NDVI
│   ├── analysis/                  # Análisis y estadísticas
│   └── visualization/             # Generación de mapas
├── tests/                         # Tests unitarios (pytest)
├── notebooks/                     # Jupyter notebooks exploratorios
├── dashboard/                     # Web (HTML + JS + CSS + Leaflet)
├── configs/
│   ├── mintpy_template.cfg        # Configuración MintPy
│   └── areas_of_interest.geojson  # Bounding boxes de zonas
├── docs/                          # Documentación técnica
├── data/                          # Datos satelitales (volcado Docker, NO en git)
│   ├── sentinel1/                 # SLC (~5 GB por escena)
│   ├── sentinel2/                 # L2A (~1 GB por escena)
│   └── dem/                       # DEMs SRTM/Copernicus
├── outputs/                       # Resultados generados
│   ├── insar/                     # Mapas de velocidad, series temporales
│   ├── ndvi/                      # Mapas NDVI
│   └── dashboard/                 # Datos JS para el dashboard
├── .env.example                   # Plantilla de credenciales
├── .gitignore                     # Archivos excluidos de git
├── environment.yml                # Definición del entorno conda
├── Makefile                       # Comandos principales
└── README.md                      # Este archivo
```

---

## 🛠️ Comandos principales (Makefile)

```bash
make help          # Ver todos los comandos disponibles
make build         # Construir imagen Docker
make up            # Levantar dev + dashboard
make up-all        # Levantar todos los servicios (incluye Jupyter)
make down          # Detener servicios
make restart       # Reiniciar
make logs          # Ver logs en vivo
make ps            # Estado de servicios

# Acceso a contenedores
make shell         # Shell interactivo en entorno conda copernico
make shell-root    # Shell como root (instalar paquetes)
make notebook      # Levantar JupyterLab
make dashboard     # Levantar dashboard web

# Pipeline
make download-s1     # Descargar Sentinel-1
make process-insar   # Procesar InSAR con MintPy
make process-ndvi    # Procesar NDVI Sentinel-2
make update-dashboard # Regenerar dashboard

# Desarrollo
make test          # Tests unitarios
make lint          # Verificar estilo (flake8, black, mypy)
make format        # Formatear código con black

# Limpieza
make clean         # Eliminar contenedores y volúmenes
make clean-images  # Eliminar imágenes Docker
```

---

## 🔬 Stack tecnológico dockerizado

### Capa base
- **Ubuntu 22.04 LTS** - Sistema operativo base
- **Miniconda 3** - Gestión de entornos Python
- **OpenJDK 11** - Para ESA SNAP (Java)

### Procesamiento científico
- **MintPy** - InSAR time-series (Universidad de Miami)
- **ISCE2** - Framework SAR (NASA JPL)
- **ESA SNAP 9.0** - Pre-procesamiento Sentinel
- **PyAPS3** - Corrección atmosférica ERA5

### Geoespacial
- **GDAL 3.6+** - I/O ráster
- **rasterio + rioxarray** - Acceso Python a rasters
- **geopandas** - Datos vectoriales
- **OpenCV** - Procesamiento de imagen

### Machine Learning
- **scikit-learn** - Clasificación y regresión
- **xgboost** - Gradient boosting
- (Opcional) **TensorFlow/PyTorch** - Deep learning

### Descarga y APIs
- **asf-search** - Cliente NASA ASF Vertex
- **cdsapi** - Copernicus Climate (ERA5)
- **eodag** - Cliente Copernicus alternativo
- **earthengine-api** - Google Earth Engine

### Visualización
- **Leaflet 1.9.4** - Mapas web interactivos
- **JupyterLab 4.0** - Análisis exploratorio
- **matplotlib + seaborn** - Visualización científica
- **ipyleaflet** - Mapas interactivos en notebooks

### DevOps
- **Docker + Compose** - Contenerización
- **Make** - Automatización
- **pytest** - Tests unitarios
- **flake8 + black + mypy** - Linting y formato
- **GitHub Actions** (futuro) - CI/CD

---

## 🗺️ Plan de migración desde el repositorio actual

Si ya tienes el repositorio `C:\Copernico` en tu PC, sigue estos pasos para migrar a la estructura Dockerizada:

### Paso 1: Respalda tu trabajo actual

```powershell
# En Windows PowerShell
Compress-Archive -Path C:\Copernico -DestinationPath C:\Copernico_backup_$(Get-Date -Format "yyyyMMdd").zip
```

### Paso 2: Clona la nueva estructura

```bash
# En tu PC (Windows con WSL o Linux)
git clone https://github.com/Arte-Inverso/copernico.git
cd copernico
git checkout -b feature/docker-migration
```

### Paso 3: Copia los archivos Docker en tu repo

Copia la carpeta `docker/`, `scripts/`, `Makefile`, `environment.yml` y `.env.example` desde el paquete que te entregué a la raíz de tu repo.

### Paso 4: Reorganiza los scripts

```bash
mkdir -p src/ingest src/processing src/analysis src/visualization tests notebooks configs

# Mover scripts existentes a estructura modular
mv download_s1_latest.py src/ingest/
mv download_s2_latest.py src/ingest/
mv download_sar.py src/ingest/

mv mt_insar_asi_sbas.py src/processing/  # Será reescrito
mv process_s2_updated.py src/processing/
mv insar_processing.py src/processing/

mv analyze_ndvi.py src/analysis/
mv sgc_live_data.py src/analysis/

# Mover XMLs de SNAP a configs
mv insar_*.xml configs/snap_graphs/

# Dashboard queda donde está
# dashboard/ ya está en la estructura correcta
```

### Paso 5: Construir y probar

```bash
make build
make up
make shell
./scripts/verify_env.sh
```

### Paso 6: Commit y push

```bash
git add .
git commit -m "feat: migrar a arquitectura Docker con MintPy+ISCE2+SNAP

- Añade Dockerfile basado en Ubuntu 22.04 + conda
- docker-compose con 3 servicios (dev, notebook, dashboard)
- environment.yml con todas las dependencias (MintPy, ISCE2, SNAP)
- Makefile con comandos automatizados
- scripts/entrypoint.sh, verify_env.sh, run_pipeline.sh
- .env.example ampliado con todas las credenciales
- Reorganización src/ en módulos (ingest, processing, analysis, visualization)"

git push origin feature/docker-migration
```

---

## 🔐 Configuración de credenciales

El archivo `.env` (NO se sube a git) debe contener:

```bash
# Copernicus Data Space (obligatorio)
CDSE_USER=tu_usuario
CDSE_PASSWORD=tu_password

# NASA Earthdata (recomendado para ASF)
EARTHDATA_USER=tu_usuario
EARTHDATA_PASSWORD=tu_password

# Copernicus Climate (ERA5, para corrección atmosférica)
CDS_API_KEY=tu_key_de_cds
```

Regístrate gratis en:
- https://identity.dataspace.copernicus.eu/ (Copernicus)
- https://urs.earthdata.nasa.gov/users/new (NASA Earthdata)
- https://cds.climate.copernicus.eu/ (Climate Data Store)

---

## 📊 Performance y recursos

### Recomendado para procesamiento real

| Recurso | Mínimo | Recomendado | Óptimo |
|---|---|---|---|
| RAM | 8 GB | 16 GB | 32 GB |
| CPU | 4 núcleos | 8 núcleos | 16+ núcleos |
| Disco | 50 GB SSD | 200 GB NVMe | 1 TB NVMe |
| GPU | No requerida | Opcional (deep learning) | Recomendada (training) |

### Tiempos estimados de procesamiento

| Operación | 8 GB RAM | 16 GB RAM | 32 GB RAM |
|---|---|---|---|
| Construcción imagen | 30 min | 20 min | 15 min |
| Descarga 30 S1 SLC | ~3 horas | ~3 horas | ~3 horas (límite red) |
| Procesamiento MintPy (30 imgs, 50×50 km) | ~6 horas | ~3 horas | ~1.5 horas |
| Procesamiento NDVI S2 | ~5 min | ~3 min | ~2 min |

---

## 🐛 Troubleshooting

### Problema: Error "no space left on device"

```bash
# Limpiar imágenes y contenedores antiguos
docker system prune -af --volumes
make clean
```

### Problema: SNAP no arranca en Docker

```bash
# SNAP requiere Java y librerías gráficas
# Verificar:
docker exec -it copernico-dev /opt/snap/bin/gpt --version
# Si falla, reinstalar dentro del contenedor:
make shell-root
/opt/snap/bin/snap --nosplash --nodesktop
```

### Problema: MintPy no encuentra ISCE2

```bash
# Verificar variables de entorno
make shell
echo $ISCE_HOME
# Debe apuntar a /opt/conda/envs/copernico/lib/python3.10/site-packages/isce
```

### Problema: Descarga muy lenta de Sentinel-1

```bash
# Alternativa: usar ASF Vertex en lugar de Copernicus
# Configura EARTHDATA_USER y EARTHDATA_PASSWORD en .env
# Usa asf-search en lugar de OData API
```

### Problema: Error de memoria en MintPy

```bash
# Aumentar memoria del contenedor en docker-compose.yml
# O reducir el tamaño del área de interés
```

---

## 📈 Roadmap futuro

### v2.1 (Q1 2027)
- [ ] Backend FastAPI + PostgreSQL/PostGIS
- [ ] API REST para datos del dashboard
- [ ] Tests unitarios completos (>80% cobertura)
- [ ] CI/CD con GitHub Actions

### v2.2 (Q2 2027)
- [ ] Integración TomoSAR cloud (Dr. Dinh Ho Tong Minh)
- [ ] Procesamiento NISAR banda L
- [ ] ComSAR para Big Data
- [ ] Auto-update del dashboard cada 12 días

### v2.3 (Q3 2027)
- [ ] Aplicación móvil para comunidad Samanga Baja
- [ ] Alertas SMS/WhatsApp para eventos críticos
- [ ] Integración con IGAC (GNSS)
- [ ] Publicación en Zenodo con DOI

### v3.0 (Q4 2027)
- [ ] BIOMASS integration (banda P)
- [ ] Deep learning para detección automática de derrumbes
- [ ] Modelo predictivo de lahares volcánicos
- [ ] Dashboard multilingüe (español + nasa yuwe)

---

## 📜 Licencia

MIT License - Libre uso con atribución.

## 📧 Contacto

**Jenner Zúñiga** - Arte-Inverso  
Proyecto: Vigilancia Volcánica e Hidrológica Samanga Baja  
Convocatoria: MinCiencias 2026  
Alianzas: TECNICAFÉ, Colegio Mayor del Cauca (UNIMAYOR), JAC Samanga Baja

---

## 🙏 Agradecimientos

- Canal [@geoscienceengineering](https://youtube.com/@geoscienceengineering) por tutoriales MintPy/ISCE2
- Dr. Dinh Ho Tong Minh (INRAE, Francia) por TomoSAR y ComSAR
- Tamayo Duque et al. (2023) por la metodología ASI
- Ávila Vélez et al. (2026) por la descomposición vertical/E-O
- ESA Copernicus y NASA ASF por datos abiertos
