# Deploy Guide

This guide explains how to deploy the Poupix application to production.

## Prerequisites

- SSH access to the production server
- Git installed locally
- Node.js and npm installed locally (for frontend build)

## Architecture

- **Backend**: Django + Gunicorn running in Docker
- **Frontend**: React static files served by Nginx
- **Database**: PostgreSQL with pgvector extension
- **Cache/Queue**: Redis
- **Background Tasks**: Celery worker
- **File Storage**: Wasabi S3-compatible storage

## Deployment Steps

### 1. Commit and Push Changes

```bash
git add -A
git commit -m "your commit message"
git push origin main
```

### 2. Connect to Server

```bash
ssh root@<SERVER_IP>
cd /root/organizador-contas
```

### 3. Pull Latest Changes

```bash
git pull origin main
```

### 4. Deploy Backend

```bash
# Rebuild and restart backend container
docker compose -f docker-compose.api.yml build --no-cache backend
docker compose -f docker-compose.api.yml up -d backend

# If you also need to update celery worker
docker compose -f docker-compose.api.yml up -d --build celery-worker
```

### 5. Deploy Frontend

On your local machine:

```bash
cd frontend
npm run build
```

Then copy the build to the server:

```bash
rsync -avz --delete frontend/dist/ root@<SERVER_IP>:/var/www/poupix/
```

Or from the server, if you have the repo there:

```bash
cd /root/organizador-contas/frontend
npm install
npm run build
cp -r dist/* /var/www/poupix/
```

## Useful Commands

### Check Container Status

```bash
docker compose -f docker-compose.api.yml ps
```

### View Backend Logs

```bash
docker compose -f docker-compose.api.yml logs -f backend
```

### View Celery Logs

```bash
docker compose -f docker-compose.api.yml logs -f celery-worker
```

### Restart All Services

```bash
docker compose -f docker-compose.api.yml down
docker compose -f docker-compose.api.yml up -d
```

### Run Django Management Commands

```bash
docker compose -f docker-compose.api.yml exec backend python manage.py <command>
```

Examples:
```bash
# Run migrations
docker compose -f docker-compose.api.yml exec backend python manage.py migrate

# Create superuser
docker compose -f docker-compose.api.yml exec backend python manage.py createsuperuser

# Collect static files
docker compose -f docker-compose.api.yml exec backend python manage.py collectstatic --noinput
```

### Force Rebuild (Clear Cache)

If Docker is using cached layers and not picking up new code:

```bash
docker compose -f docker-compose.api.yml down backend
docker rmi organizador-contas-backend
docker compose -f docker-compose.api.yml build --no-cache backend
docker compose -f docker-compose.api.yml up -d backend
```

## Environment Variables

Make sure the `.env` file on the server contains all required variables. See `backend/.env.example` for reference.

## Troubleshooting

### Container not starting
Check logs: `docker compose -f docker-compose.api.yml logs backend`

### New code not being picked up
Force rebuild without cache (see above)

### Database connection issues
Ensure the `db` container is healthy: `docker compose -f docker-compose.api.yml ps`

