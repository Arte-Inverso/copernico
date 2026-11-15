#!/usr/bin/env bash
# =============================================================================
# Copernico - script de verificación post-instalación
# Verifica que todo el stack funciona correctamente
# =============================================================================

set -e

CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  COPERNICO - Verificación post-instalación         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

PASS=0
FAIL=0
WARN=0

check() {
    local desc="$1"
    local cmd="$2"
    local expected="$3"

    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $desc"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}✗${NC} $desc"
        FAIL=$((FAIL + 1))
    fi
}

warn_check() {
    local desc="$1"
    local cmd="$2"

    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $desc"
        PASS=$((PASS + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} $desc (opcional)"
        WARN=$((WARN + 1))
    fi
}

echo -e "${CYAN}[1/6] Core Python${NC}"
check "Python 3.10"        "python --version 2>&1 | grep -q '3.10'"
check "numpy"              "python -c 'import numpy'"
check "scipy"              "python -c 'import scipy'"
check "pandas"             "python -c 'import pandas'"
check "matplotlib"         "python -c 'import matplotlib'"
echo ""

echo -e "${CYAN}[2/6] Geoespacial${NC}"
check "GDAL"               "python -c 'from osgeo import gdal'"
check "rasterio"           "python -c 'import rasterio'"
check "rioxarray"          "python -c 'import rioxarray'"
check "geopandas"          "python -c 'import geopandas'"
check "shapely"            "python -c 'import shapely'"
echo ""

echo -e "${CYAN}[3/6] Imagen y visión${NC}"
check "OpenCV"             "python -c 'import cv2'"
check "tifffile"           "python -c 'import tifffile'"
check "PIL/Pillow"         "python -c 'import PIL'"
echo ""

echo -e "${CYAN}[4/6] InSAR específico${NC}"
check "MintPy"             "python -c 'import mintpy'"
check "ISCE2"              "python -c 'import isce'"
warn_check "PyAPS3 (ERA5)" "python -c 'import pyaps3'"
warn_check "SNAP (gpt)"    "/opt/snap/bin/gpt --version 2>/dev/null"
echo ""

echo -e "${CYAN}[5/6] Descarga y APIs${NC}"
check "requests"           "python -c 'import requests'"
check "dotenv"             "python -c 'import dotenv'"
warn_check "asf-search"    "python -c 'import asf_search'"
warn_check "cdsapi (ERA5)" "python -c 'import cdsapi'"
echo ""

echo -e "${CYAN}[6/6] Jupyter y desarrollo${NC}"
check "jupyterlab"        "python -c 'import jupyterlab'"
check "pytest"             "python -c 'import pytest'"
warn_check "black"         "python -c 'import black'"
echo ""

echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
echo -e "  Resultados: ${GREEN}$PASS OK${NC} | ${YELLOW}$WARN opcionales${NC} | ${RED}$FAIL errores${NC}"
echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}✗ Hay $FAIL errores. Revisa los logs de construcción.${NC}"
    exit 1
elif [ $WARN -gt 0 ]; then
    echo -e "${YELLOW}⚠ $WARN componentes opcionales no instalados.${NC}"
    echo "  Para funcionalidad completa instala: asf-search, cdsapi, PyAPS3"
else
    echo -e "${GREEN}✓ Entorno Copernico verificado correctamente.${NC}"
    echo -e "  Listo para procesamiento InSAR."
fi
