# =============================================================================
# Copernico - Dockerfile principal
# Sistema de monitoreo satelital MT-InSAR para cuencas hídricas y volcanes
# Basado en Ubuntu 22.04 + Miniconda + MintPy + SNAP
# =============================================================================

FROM condaforge/miniforge3:latest

LABEL maintainer="Arte-Inverso (Jenner Zúñiga)"
LABEL project="Copernico - Vigilancia Volcánica e Hidrológica Samanga Baja"
LABEL version="2.0-docker"

# Evitar prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# =============================================================================
# 1. DEPENDENCIAS DEL SISTEMA
# =============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc g++ gfortran \
    git cmake wget curl unzip \
    libfftw3-dev libgdal-dev libproj-dev \
    libhdf5-dev libnetcdf-dev \
    libgeos-dev libxml2-dev libxslt1-dev \
    libjpeg-dev libpng-dev libtiff-dev \
    libgl1 libqt5gui5 libqt5core5a libqt5dbus5 \
    fonts-dejavu fonts-noto-cjk \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

# =============================================================================
# 3. ENTORNO CONDA PARA COPERNICO
# =============================================================================
COPY environment.yml /tmp/environment.yml

RUN $CONDA_DIR/bin/mamba env create -f /tmp/environment.yml || $CONDA_DIR/bin/conda env create -f /tmp/environment.yml && \
    $CONDA_DIR/bin/conda clean -afy

# Activar entorno por defecto
ENV PATH=$CONDA_DIR/envs/copernico/bin:$PATH
ENV CONDA_DEFAULT_ENV=copernico

# =============================================================================
# 4. ESA SNAP (para pre-procesamiento Sentinel)
# =============================================================================
ENV SNAP_HOME=/opt/snap
ENV PATH=$SNAP_HOME/bin:$PATH

# Snap es grande (~1.1 GB), lo instalamos en una capa separada para cache
RUN wget --progress=dot:giga https://download.esa.int/step/snap/14.0/installers/esa-snap_sentinel_linux-14.0.0.sh -O /tmp/snap_installer.sh && \
    chmod +x /tmp/snap_installer.sh && \
    /tmp/snap_installer.sh -q -dir $SNAP_HOME && \
    rm -f /tmp/snap_installer.sh

# Configurar variables SNAP
ENV GPT_PATH=$SNAP_HOME/bin/gpt
ENV SNAP_CACHE_DIR=/tmp/snap_cache

# =============================================================================
# 5. ESTRUCTURA DEL PROYECTO
# =============================================================================
ENV COPERNICO_HOME=/opt/copernico
ENV COPERNICO_DATA=/data
ENV COPERNICO_OUTPUTS=/outputs

RUN mkdir -p $COPERNICO_HOME $COPERNICO_DATA $COPERNICO_OUTPUTS && \
    mkdir -p $COPERNICO_DATA/sentinel1 $COPERNICO_DATA/sentinel2 $COPERNICO_DATA/dem && \
    mkdir -p $COPERNICO_OUTPUTS/insar $COPERNICO_OUTPUTS/ndvi $COPERNICO_OUTPUTS/dashboard

WORKDIR $COPERNICO_HOME

# =============================================================================
# 6. COPIAR CÓDIGO DEL PROYECTO
# =============================================================================
COPY . $COPERNICO_HOME/

# Asegurar permisos de ejecución para scripts
RUN chmod +x $COPERNICO_HOME/scripts/*.sh 2>/dev/null || true && \
    find $COPERNICO_HOME -name "*.py" -exec chmod +x {} \\; 2>/dev/null || true

# =============================================================================
# 7. CONFIGURACIÓN FINAL
# =============================================================================

# Crear usuario no-root para ejecutar (seguridad)
RUN useradd -m -s /bin/bash copernico && \
    chown -R copernico:copernico $COPERNICO_HOME $COPERNICO_DATA $COPERNICO_OUTPUTS

USER copernico

# Shell que activa conda por defecto
SHELL ["/bin/bash", "-c"]

# Healthcheck básico
HEALTHCHECK --interval=5m --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import mintpy; import isce" || exit 1

# Comando por defecto: shell interactivo en el entorno conda
CMD ["/bin/bash", "-c", "source $CONDA_DIR/activate copernico && exec bash"]

# =============================================================================
# VOLÚMENES PARA DATOS PERSISTENTES
# =============================================================================
VOLUME ["/data", "/outputs"]
