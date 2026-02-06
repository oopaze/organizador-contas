# Setup Guide

This guide explains how to set up the Poupix application for local development.

## Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- Docker and Docker Compose (for database and Redis)
- Git

## Project Structure

```
├── backend/          # Django REST API
├── frontend/         # React + Vite + Tailwind
├── docs/             # Documentation
├── Dockerfile.backend
└── docker-compose.api.yml
```

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in the required values:

```env
# AI API Keys (at least one required)
GOOGLE_AI_API_KEY=your_google_ai_key
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_deepseek_key

# Database
DATABASE_NAME=poupix
DATABASE_USER=poupix
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Django
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
DEBUG=1

# Wasabi S3 Storage (optional for local dev)
WASABI_ACCESS_KEY=
WASABI_SECRET_KEY=
WASABI_BUCKET_NAME=poupix-media-dev
WASABI_REGION=us-east-1
```

### 4. Start Database and Redis with Docker

```bash
# From project root
docker compose -f docker-compose.api.yml up -d db redis
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### 8. Run Celery Worker (for background tasks)

In a separate terminal:

```bash
cd backend
source venv/bin/activate
celery -A infra worker --loglevel=info
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Running with Docker (Full Stack)

To run everything with Docker:

```bash
docker compose -f docker-compose.api.yml up -d
```

This starts:
- PostgreSQL with pgvector
- Redis
- Django backend (port 8000)
- Celery worker

## Code Quality Tools

The project uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Tools configured:
- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Linting

## API Documentation

Once the backend is running, access:
- Admin: `http://localhost:8000/admin/`
- API endpoints: `http://localhost:8000/api/`

## Troubleshooting

### Database connection error
Make sure PostgreSQL is running: `docker compose -f docker-compose.api.yml ps`

### Redis connection error
Make sure Redis is running: `docker compose -f docker-compose.api.yml ps`

### Frontend can't connect to backend
Check CORS settings in `.env` and ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL.

