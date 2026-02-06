# Poupix

A personal finance application with AI-powered bill parsing and transaction management.

## Features

- 📄 **File Upload & Parsing**: Upload PDF/Excel files and extract transactions using AI
- 🤖 **AI-Powered Analysis**: Uses Google AI, OpenAI, or DeepSeek for intelligent data extraction
- 💬 **AI Chat**: Chat with your financial data
- 📊 **AI Insights**: Track AI usage, costs, and performance metrics
- 💰 **Transaction Management**: Organize and categorize your transactions
- ☁️ **Cloud Storage**: Files stored in Wasabi S3-compatible storage

## Tech Stack

### Backend
- **Python 3.12+** with Django 6.0
- **Django REST Framework** for API endpoints
- **PostgreSQL 16** with **pgvector** extension for vector search
- **Celery** with **Redis** for background task processing
- **Wasabi S3** for file storage

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS 4** for styling
- **Radix UI** and **shadcn/ui** components
- **Recharts** for data visualization

## Project Structure

```
poupix/
├── backend/              # Django REST API
│   ├── infra/            # Django settings and configuration
│   ├── modules/          # Application modules
│   │   ├── ai/           # AI integrations and chat
│   │   ├── base/         # Base models and utilities
│   │   ├── file_reader/  # File upload and parsing
│   │   ├── transactions/ # Transaction management
│   │   └── userdata/     # User authentication
│   └── manage.py
├── frontend/             # React + Vite application
│   └── src/
├── docs/                 # Documentation
│   ├── SETUP.md          # Local development setup
│   └── DEPLOY.md         # Production deployment guide
├── docker-compose.api.yml
├── Dockerfile.backend
└── Makefile
```

## Documentation

- **[Setup Guide](docs/SETUP.md)** - Local development setup instructions
- **[Deploy Guide](docs/DEPLOY.md)** - Production deployment instructions

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker and Docker Compose

### Local Development

1. **Start database and Redis:**
```bash
docker compose -f docker-compose.api.yml up -d db redis
```

2. **Setup backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your API keys
python manage.py migrate
python manage.py runserver
```

3. **Setup frontend:**
```bash
cd frontend
npm install
npm run dev
```

4. **Start Celery worker** (for background tasks):
```bash
cd backend
celery -A infra worker --loglevel=info
```

See [docs/SETUP.md](docs/SETUP.md) for detailed instructions.

### Using Docker

```bash
# Start all services
docker compose -f docker-compose.api.yml up -d

# View logs
docker compose -f docker-compose.api.yml logs -f
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make dev` | Run frontend and backend in dev mode |
| `make api` | Build and start API with Docker |
| `make api-logs` | View API logs |
| `make db_up` | Start database container |
| `make db_shell` | Open database shell |
| `make migrate` | Run Django migrations |

Run `make help` for all available commands.

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```env
# AI API Keys (at least one required)
GOOGLE_AI_API_KEY=
OPENAI_API_KEY=
DEEPSEEK_API_KEY=

# Database
DATABASE_PASSWORD=

# Django
SECRET_KEY=
DEBUG=1

# Wasabi S3 (optional for local dev)
WASABI_ACCESS_KEY=
WASABI_SECRET_KEY=
```

## License

Private project.

