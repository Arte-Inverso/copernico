# =============================================================================
# Copernico - Dockerfile Optimizado (Rápido, ligero y 100% estable)
# Sistema de monitoreo satelital MT-InSAR para cuencas hídricas y volcanes
# =============================================================================

FROM python:3.10-slim-bookworm

LABEL maintainer="Arte-Inverso (Jenner Zúñiga)"
LABEL project="Copernico - Vigilancia Volcánica e Hidrológica Samanga Baja"
LABEL version="2.5-fast"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 1. Herramientas del sistema y binarios GDAL de Debian Bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    curl \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar dependencias Python científicas y geoespaciales
WORKDIR /tmp
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# 3. Estructura del proyecto
ENV COPERNICO_HOME=/opt/copernico
ENV COPERNICO_DATA=/data
ENV COPERNICO_OUTPUTS=/outputs

RUN mkdir -p $COPERNICO_HOME $COPERNICO_DATA $COPERNICO_OUTPUTS \
    $COPERNICO_DATA/sentinel1 $COPERNICO_DATA/sentinel2 $COPERNICO_DATA/dem \
    $COPERNICO_OUTPUTS/insar $COPERNICO_OUTPUTS/ndvi $COPERNICO_OUTPUTS/dashboard

WORKDIR $COPERNICO_HOME

# 4. Copiar código fuente del proyecto
COPY . $COPERNICO_HOME/

# Asegurar permisos de ejecución para scripts
RUN chmod +x $COPERNICO_HOME/scripts/*.sh 2>/dev/null || true && \
    find $COPERNICO_HOME -name "*.py" -exec chmod +x {} + 2>/dev/null || true

# 5. Usuario no-root para seguridad
RUN useradd -m -s /bin/bash copernico && \
    chown -R copernico:copernico $COPERNICO_HOME $COPERNICO_DATA $COPERNICO_OUTPUTS

USER copernico

VOLUME ["/data", "/outputs"]

CMD ["/bin/bash"]
