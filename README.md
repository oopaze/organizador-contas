# Bills Manager

A full-stack application for managing bills and transactions with PDF parsing capabilities.

## Tech Stack

### Backend
- **Python 3.12+** with Django 6.0
- **Django REST Framework** for API endpoints
- **PostgreSQL 16** with **pgvector** extension
- PDF parsing for bill extraction

### Frontend
- **React 19** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS 4** for styling
- **Material UI** and **Radix UI** components

## Project Structure

```
bills-manager/
├── backend/          # Django REST API
│   ├── infra/        # Django settings and configuration
│   ├── modules/      # Application modules
│   │   ├── base/
│   │   ├── pdf_reader/
│   │   ├── transactions/
│   │   └── userdata/
│   └── manage.py
├── frontend/         # React + Vite application
│   └── src/
├── docker-compose.yml
├── Dockerfile.backend
└── Dockerfile.frontend
```

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- Yarn

### Local Development

#### Database (PostgreSQL with pgvector)

Start only the database container for local development:
```bash
make db_up
```

This starts PostgreSQL on `localhost:5432` with:
- Database: `bills_manager`
- User: `postgres`
- Password: `postgres`

To enable the pgvector extension (run once):
```bash
make db_init_pgvector
```

Available database commands:
| Command | Description |
|---------|-------------|
| `make db_up` | Start the PostgreSQL container |
| `make db_down` | Stop the PostgreSQL container |
| `make db_logs` | Follow database logs |
| `make db_shell` | Open a psql shell to the database |
| `make db_init_pgvector` | Enable the pgvector extension |

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend
```bash
cd frontend
yarn install
yarn dev
```

### Using Docker

Build and run all services (db, backend, frontend):
```bash
docker-compose up --build
```

Run only specific services:
```bash
# Database only (for local development)
docker-compose up -d db

# Database + Backend
docker-compose up -d db backend

# Frontend only
docker build -f Dockerfile.frontend -t bills-manager-frontend .
docker run -p 3000:80 bills-manager-frontend
```

## API Endpoints

The backend runs on `http://localhost:8000` by default.

## Environment Variables

### Backend
Create a `backend/infra/secrets.py` file for sensitive configuration.

### Frontend
Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
```

## License

Private project.

