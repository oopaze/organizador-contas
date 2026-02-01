# ===========================================
# Poupix - Makefile
# ===========================================

.PHONY: help dev prod prod-build prod-up prod-down prod-logs prod-restart

# Show help
help:
	@echo "Poupix - Available commands:"
	@echo ""
	@echo "  Development:"
	@echo "    make dev              - Run frontend and backend in dev mode"
	@echo "    make run_dev          - Run backend only"
	@echo "    make run_dev_front    - Run frontend only"
	@echo ""
	@echo "  Production (Full Stack):"
	@echo "    make prod             - Build and start production"
	@echo "    make prod-down        - Stop production containers"
	@echo "    make prod-logs        - View production logs"
	@echo ""
	@echo "  API Only (for CDN frontend):"
	@echo "    make api              - Build and start API + Database"
	@echo "    make api-down         - Stop API containers"
	@echo "    make api-logs         - View API logs"
	@echo ""
	@echo "  Database:"
	@echo "    make db_up            - Start database container"
	@echo "    make db_shell         - Open database shell"
	@echo "    make migrate          - Run migrations"
	@echo ""

# ===========================================
# Development
# ===========================================

# Run both frontend and backend
dev:
	@echo "Starting development servers..."
	@make -j2 run_dev run_dev_front

# Frontend commands
run_dev_front:
	cd frontend && yarn dev

# Backend commands
run_dev:
	cd backend && python manage.py runserver

migrations:
	cd backend && python manage.py makemigrations

migrate:
	cd backend && python manage.py migrate

app_shell:
	cd backend && python manage.py shell

# ===========================================
# Production (Full Stack)
# ===========================================

# Build and start production
prod: prod-build prod-up
	@echo "✅ Production is running!"
	@echo "   Access: http://localhost:$${PORT:-80}"

# Build production images
prod-build:
	@echo "🔨 Building production images..."
	docker compose -f docker-compose.prod.yml build

# Start production containers
prod-up:
	@echo "🚀 Starting production..."
	docker compose -f docker-compose.prod.yml up -d

# Stop production containers
prod-down:
	@echo "🛑 Stopping production..."
	docker compose -f docker-compose.prod.yml down

# View production logs
prod-logs:
	docker compose -f docker-compose.prod.yml logs -f

# Restart production containers
prod-restart:
	@echo "🔄 Restarting production..."
	docker compose -f docker-compose.prod.yml restart

# ===========================================
# API Only (Backend + Database for CDN frontend)
# ===========================================

# Build and start API only
api: api-build api-up
	@echo "✅ API is running!"
	@echo "   Access: http://localhost:$${API_PORT:-8000}"

# Build API images
api-build:
	@echo "🔨 Building API images..."
	docker compose -f docker-compose.api.yml build

# Start API containers
api-up:
	@echo "🚀 Starting API..."
	docker compose -f docker-compose.api.yml up -d

# Stop API containers
api-down:
	@echo "🛑 Stopping API..."
	docker compose -f docker-compose.api.yml down

# View API logs
api-logs:
	docker compose -f docker-compose.api.yml logs -f

# Restart API containers
api-restart:
	@echo "🔄 Restarting API..."
	docker compose -f docker-compose.api.yml restart

# ===========================================
# Database
# ===========================================

db_up:
	docker compose up -d db

db_down:
	docker compose down db

db_logs:
	docker compose logs -f db

db_shell:
	docker compose exec db psql -U postgres -d poupix

db_init_pgvector:
	docker compose exec db psql -U postgres -d poupix -c "CREATE EXTENSION IF NOT EXISTS vector;"

db_clean:
	docker compose down -v db
	docker volume rm bills-manager_postgres_data 2>/dev/null || true