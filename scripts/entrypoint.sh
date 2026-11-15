#!/usr/bin/env bash
# =============================================================================
# Copernico - script de inicialización del contenedor
# Se ejecuta automáticamente al levantar el contenedor
# =============================================================================

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║  COPERNICO - Sistema de monitoreo satelital MT-InSAR  ║"
echo "║  Vigilancia Volcánica e Hidrológica Samanga Baja       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Activar entorno conda
echo "→ Activando entorno conda 'copernico'..."
source /opt/conda/activate copernico

# Verificar dependencias críticas
echo "→ Verificando dependencias críticas..."
python -c "import numpy, scipy, gdal, rasterio, mintpy, isce; print('  ✓ Dependencias core OK')" 2>/dev/null || {
    echo "  ⚠ Algunas dependencias no están disponibles"
    echo "  Revisa con: pip list | grep -i 'mintpy\\|isce\\|gdal'"
}

# Verificar SNAP
if [ -x "/opt/snap/bin/gpt" ]; then
    echo "  ✓ SNAP disponible: $(/opt/snap/bin/gpt --version 2>&1 | head -1)"
else
    echo "  ⚠ SNAP no encontrado en /opt/snap/bin/gpt"
fi

# Verificar variables de entorno
echo "→ Verificando configuración..."
if [ -f /opt/copernico/.env ]; then
    echo "  ✓ Archivo .env encontrado"
    if grep -q "tu_usuario_registrado" /opt/copernico/.env; then
        echo "  ⚠ Credenciales por defecto. Edita /opt/copernico/.env con tus credenciales reales de Copernicus."
    else
        echo "  ✓ Credenciales configuradas"
    fi
else
    echo "  ⚠ .env no encontrado. Cópialo desde .env.example"
fi

# Verificar volúmenes montados
echo "→ Verificando volúmenes..."
for dir in /data/sentinel1 /data/sentinel2 /outputs/insar /outputs/ndvi; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        mkdir -p "$dir" 2>/dev/null && echo "  + $dir (creado)" || echo "  ✗ $dir (no accesible)"
    fi
done

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Entorno listo. Comandos útiles:                      ║"
echo "║                                                        ║"
echo "║  python scripts/download_s1_latest.py   # Descargar S1  ║"
echo "║  python scripts/process_insar.py        # Procesar     ║"
echo "║  python scripts/update_dashboard.py     # Dashboard    ║"
echo "║  pytest tests/ -v                       # Tests        ║"
echo "║                                                        ║"
echo "║  Salir: 'exit'                                         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Ejecutar comando o abrir shell
if [ "$1" = "bash" ] || [ -z "$1" ]; then
    exec bash
else
    exec "$@"
fi
