# Bills Manager

A full-stack application for managing bills and transactions with PDF parsing capabilities.

## Tech Stack

### Backend
- **Python 3.12+** with Django 6.0
- **Django REST Framework** for API endpoints
- **SQLite** database (development)
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

Build and run both services:
```bash
docker-compose up --build
```

Or run services individually:
```bash
# Backend only
docker build -f Dockerfile.backend -t bills-manager-backend .
docker run -p 8000:8000 bills-manager-backend

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

