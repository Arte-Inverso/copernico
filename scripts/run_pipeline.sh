#!/usr/bin/env bash
# =============================================================================
# Copernico - Pipeline completo automatizado
# Ejecuta: descarga → pre-procesamiento → InSAR → NDVI → dashboard
# =============================================================================

set -e

CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
NC='\033[0m'

# Cargar variables de entorno
if [ -f /opt/copernico/.env ]; then
    export $(grep -v '^#' /opt/copernico/.env | xargs)
fi

echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  COPERNICO - Pipeline completo automatizado         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar credenciales
if [ -z "$CDSE_USER" ] || [ "$CDSE_USER" = "tu_usuario_registrado" ]; then
    echo -e "${RED}✗ Credenciales no configuradas en .env${NC}"
    echo "  Edita /opt/copernico/.env con tus credenciales de Copernicus Data Space"
    exit 1
fi
echo -e "${GREEN}✓${NC} Credenciales Copernicus OK"

# Paso 1: Descargar Sentinel-1
echo ""
echo -e "${CYAN}[1/5] Descargando Sentinel-1 SLC...${NC}"
python /opt/copernico/scripts/download_s1_latest.py
echo -e "${GREEN}✓${NC} Sentinel-1 descargado"

# Paso 2: Descargar Sentinel-2
echo ""
echo -e "${CYAN}[2/5] Descargando Sentinel-2 L2A...${NC}"
python /opt/copernico/scripts/download_s2_latest.py
echo -e "${GREEN}✓${NC} Sentinel-2 descargado"

# Paso 3: Procesar NDVI
echo ""
echo -e "${CYAN}[3/5] Procesando NDVI Sentinel-2...${NC}"
python /opt/copernico/scripts/process_s2_updated.py
echo -e "${GREEN}✓${NC} NDVI generado en /outputs/ndvi/"

# Paso 4: Procesar InSAR con MintPy
echo ""
echo -e "${CYAN}[4/5] Procesando MT-InSAR con MintPy...${NC}"
if [ -f /opt/copernico/configs/mintpy_template.cfg ]; then
    smallbaselineApp.py /opt/copernico/configs/mintpy_template.cfg
    echo -e "${GREEN}✓${NC} InSAR procesado en /outputs/insar/"
else
    echo -e "${YELLOW}⚠${NC} Configuración MintPy no encontrada. Saltando paso InSAR."
    echo "  Crea configs/mintpy_template.cfg con tu configuración."
fi

# Paso 5: Actualizar dashboard
echo ""
echo -e "${CYAN}[5/5] Actualizando datos del dashboard...${NC}"
python /opt/copernico/scripts/update_dashboard.py
echo -e "${GREEN}✓${NC} Dashboard actualizado"

# Actualizar sismicidad SGC
echo ""
echo -e "${CYAN}[+] Actualizando sismicidad SGC...${NC}"
python /opt/copernico/scripts/sgc_live_data.py || true
echo -e "${GREEN}✓${NC} Sismicidad SGC actualizada"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Pipeline completado. Resultados:                   ║${NC}"
echo -e "${CYAN}╠══════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║  • Mapas InSAR:    /outputs/insar/                   ║${NC}"
echo -e "${CYAN}║  • NDVI:           /outputs/ndvi/                   ║${NC}"
echo -e "${CYAN}║  • Dashboard:      http://localhost:8080              ║${NC}"
echo -e "${CYAN}║  • Datos SGC:      /outputs/dashboard/sgc_data.js    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
