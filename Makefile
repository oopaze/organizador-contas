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

# Database commands
db_up:
	docker-compose up -d db

db_down:
	docker-compose down db

db_logs:
	docker-compose logs -f db

db_shell:
	docker-compose exec db psql -U postgres -d bills_manager

db_init_pgvector:
	docker-compose exec db psql -U postgres -d bills_manager -c "CREATE EXTENSION IF NOT EXISTS vector;"

db_clean:
	docker-compose down -v db
	docker volume rm bills-manager_postgres_data 2>/dev/null || true