# =============================================================================
# Copernico - Makefile
# Comandos principales para gestionar el entorno Docker
# Uso: make <comando>
# =============================================================================

# Variables
DOCKER_COMPOSE = docker-compose -f docker/docker-compose.yml
PROJECT_NAME = copernico

# Colores para output
CYAN = \033[36m
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
NC = \033[0m

.PHONY: help build up down restart logs ps shell notebook dashboard clean test lint

# =============================================================================
# COMANDOS PRINCIPALES
# =============================================================================

help: ## Mostrar ayuda
	@echo "$(CYAN)╔══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║   COPERNICO - Sistema de monitoreo satelital             ║$(NC)"
	@echo "$(CYAN)║   Gestión del entorno Docker                             ║$(NC)"
	@echo "$(CYAN)╚══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Comandos disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

build: ## Construir imagen Docker (primera vez o tras cambios)
	@echo "$(GREEN)[1/3]$(NC) Construyendo imagen Docker para Copernico..."
	$(DOCKER_COMPOSE) build --no-cache copernico-dev
	@echo "$(GREEN)[2/3]$(NC) Imagen construida correctamente."
	@echo "$(GREEN)[3/3]$(NC) Tamaño de la imagen:"
	@docker images | grep copernico | head -3

up: ## Levantar servicios (dev + dashboard)
	@echo "$(CYAN)→$(NC) Levantando servicios Copernico..."
	$(DOCKER_COMPOSE) up -d copernico-dev copernico-dashboard
	@echo "$(GREEN)✓$(NC) Servicios activos:"
	@echo "  • Dev (CLI):        docker exec -it copernico-dev bash"
	@echo "  • Dashboard web:    http://localhost:8080"
	@echo ""
	@echo "$(YELLOW)Para Jupyter:$(NC) make notebook"

up-all: ## Levantar todos los servicios (incluye Jupyter)
	@echo "$(CYAN)→$(NC) Levantando todos los servicios..."
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓$(NC) Todos los servicios activos:"
	@echo "  • Dev (CLI):        docker exec -it copernico-dev bash"
	@echo "  • Dashboard web:    http://localhost:8080"
	@echo "  • Jupyter Lab:     http://localhost:8888 (token: copernico-dev)"

down: ## Detener todos los servicios
	@echo "$(RED)→$(NC) Deteniendo servicios Copernico..."
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓$(NC) Servicios detenidos."

restart: ## Reiniciar servicios
	@echo "$(CYAN)→$(NC) Reiniciando..."
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✓$(NC) Servicios reiniciados."

logs: ## Ver logs en vivo
	$(DOCKER_COMPOSE) logs -f

ps: ## Ver estado de servicios
	@echo "$(CYAN)Estado de servicios Copernico:$(NC)"
	$(DOCKER_COMPOSE) ps

# =============================================================================
# ACCESO A CONTENEDORES
# =============================================================================

shell: ## Abrir shell interactivo en contenedor dev
	@echo "$(CYAN)→$(NC) Abriendo shell en copernico-dev (entorno conda 'copernico' activo)..."
	$(DOCKER_COMPOSE) exec copernico-dev bash

shell-root: ## Abrir shell como root (para instalar paquetes)
	@echo "$(YELLOW)→$(NC) Abriendo shell como ROOT..."
	$(DOCKER_COMPOSE) exec --user root copernico-dev bash

notebook: ## Levantar JupyterLab en puerto 8888
	@echo "$(CYAN)→$(NC) Iniciando JupyterLab..."
	$(DOCKER_COMPOSE) up -d copernico-notebook
	@echo "$(GREEN)✓$(NC) JupyterLab disponible en: http://localhost:8888"
	@echo "  Token: $(YELLOW)copernico-dev$(NC)"

dashboard: ## Levantar dashboard web en puerto 8080
	@echo "$(CYAN)→$(NC) Iniciando dashboard..."
	$(DOCKER_COMPOSE) up -d copernico-dashboard
	@echo "$(GREEN)✓$(NC) Dashboard en: http://localhost:8080"

# =============================================================================
# PIPELINE DE PROCESAMIENTO
# =============================================================================

download-s1: ## Descargar imágenes Sentinel-1 (configurar .env antes)
	@echo "$(CYAN)→$(NC) Descargando Sentinel-1..."
	$(DOCKER_COMPOSE) exec copernico-dev python scripts/download_s1_latest.py

process-insar: ## Procesar InSAR con MintPy
	@echo "$(CYAN)→$(NC) Ejecutando pipeline InSAR..."
	$(DOCKER_COMPOSE) exec copernico-dev python scripts/process_insar.py

process-ndvi: ## Procesar NDVI con Sentinel-2
	@echo "$(CYAN)→$(NC) Procesando NDVI..."
	$(DOCKER_COMPOSE) exec copernico-dev python scripts/process_s2_updated.py

update-dashboard: ## Regenerar datos del dashboard
	@echo "$(CYAN)→$(NC) Actualizando datos del dashboard..."
	$(DOCKER_COMPOSE) exec copernico-dev python scripts/update_dashboard.py

# =============================================================================
# DESARROLLO
# =============================================================================

test: ## Ejecutar tests unitarios
	@echo "$(CYAN)→$(NC) Ejecutando tests..."
	$(DOCKER_COMPOSE) exec copernico-dev pytest tests/ -v --cov=src

lint: ## Verificar estilo de código
	@echo "$(CYAN)→$(NC) Verificando estilo..."
	$(DOCKER_COMPOSE) exec copernico-dev flake8 src/ tests/
	$(DOCKER_COMPOSE) exec copernico-dev black --check src/ tests/
	$(DOCKER_COMPOSE) exec copernico-dev mypy src/

format: ## Formatear código con black
	@echo "$(CYAN)→$(NC) Formateando código..."
	$(DOCKER_COMPOSE) exec copernico-dev black src/ tests/

# =============================================================================
# LIMPIEZA
# =============================================================================

clean: ## Detener servicios y limpiar contenedores
	@echo "$(RED)→$(NC) Limpiando..."
	$(DOCKER_COMPOSE) down -v
	docker system prune -f
	@echo "$(GREEN)✓$(NC) Limpieza completa."

clean-images: ## Eliminar imágenes Docker (libera disco)
	@echo "$(RED)→$(NC) Eliminando imágenes..."
	docker rmi $$(docker images | grep copernico | awk '{print $$3}') -f 2>/dev/null || true
	@echo "$(GREEN)✓$(NC) Imágenes eliminadas."

# =============================================================================
# UTILIDADES
# =============================================================================

env: ## Crear .env a partir de .env.example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓$(NC) .env creado. Edítalo con tus credenciales."; \
	else \
		echo "$(YELLOW)!$(NC) .env ya existe. Edítalo manualmente."; \
	fi

info: ## Mostrar información del entorno
	@echo "$(CYAN)═══════════════════════════════════════════════════$(NC)"
	@echo "$(CYAN) COPERNICO - Información del entorno$(NC)"
	@echo "$(CYAN)═══════════════════════════════════════════════════$(NC)"
	@echo "  Docker:       $$(docker --version)"
	@echo "  Compose:      $$(docker-compose --version)"
	@echo "  Python:       3.10 (en contenedor)"
	@echo "  Conda env:    copernico"
	@echo "  Imagen base:  ubuntu:22.04"
	@echo ""
	@echo "$(GREEN)Servicios:$(NC)"
	@echo "  • copernico-dev        (CLI + scripts)"
	@echo "  • copernico-notebook   (JupyterLab :8888)"
	@echo "  • copernico-dashboard  (Web :8080)"
	@echo ""
	@echo "$(GREEN)Rutas en contenedor:$(NC)"
	@echo "  • Proyecto:   /opt/copernico"
	@echo "  • Datos:      /data"
	@echo "  • Outputs:    /outputs"
