# ================================
# DOCUMIND - Makefile
# ================================


.PHONY: help up down build logs shell-backend shell-db migrate test clean


# Muestra todos los comandos disponibles
help:
	@echo ""
	@echo "  DOCUMIND - Comandos disponibles"
	@echo "  ================================"
	@echo "  make up              → Levanta todos los servicios"
	@echo "  make down            → Para todos los servicios"
	@echo "  make build           → Reconstruye las imágenes Docker"
	@echo "  make logs            → Ver logs de todos los servicios"
	@echo "  make logs-api        → Ver logs solo del backend"
	@echo "  make logs-worker     → Ver logs del worker Celery"
	@echo "  make shell-backend   → Entrar al container del backend"
	@echo "  make shell-db        → Entrar a PostgreSQL"
	@echo "  make migrate         → Ejecutar migraciones de base de datos"
	@echo "  make migrate-create  → Crear nueva migración (usar con msg=...)"
	@echo "  make test            → Ejecutar todos los tests"
	@echo "  make test-unit       → Ejecutar solo tests unitarios"
	@echo "  make clean           → Eliminar containers y volúmenes"
	@echo "  make reset           → Clean + up (empezar de cero)"
	@echo ""


# levantar servicios 
up:
	docker compose up -d
	@echo "✅ Servicios levantados"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Frontend: http://localhost:3000"
	@echo "   API Docs: http://localhost:8000/docs"
	@echo "   MinIO:    http://localhost:9001"


# Levantar con logs visibles (útil para debuggear)
up-logs:
	docker compose up


# Parar servicios
down:
	docker compose down


# Reconstruir imágenes (cuando cambias requirements.txt o Dockerfile)
build:
	docker compose build --no-cache


# Ver logs
logs:
	docker compose logs -f


logs-api:
	docker compose logs -f api

logs-worker:
	docker compose logs -f worker


logs-frontend:
	docker compose logs -f frontend

# Entrar a los containers
shell-backend:
	docker compose exec api bash


shell-db:
	docker compose exec postgres psql -U documind -d documind_db


shell-redis:
	docker compose exec redis redis-cli


# Migraciones de base de datos
migrate:
	docker compose exec api alembic upgrade head

migrate-create:
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

migrate-down:
	docker compose exec api alembic downgrade -1


# Tests
test:
	docker compose exec api pytest tests/ -v

test-unit:
	docker compose exec api pytest tests/unit/ -v

test-integration:
	docker compose exec api pytest tests/integration/ -v


# Limpiar todo
clean:
	docker compose down -v --remove-orphans
	@echo "🧹 Containers y volúmenes eliminados"


# Empezar de cero
reset: clean up

# Ver estado de los servicios
status:
	docker compose ps


train-classifier:
	docker compose exec api python -c "from app.ml.classifier import train_classifier; train_classifier()"
	@echo "✅ Classifier trained and saved"