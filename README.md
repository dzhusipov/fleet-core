# FleetCore — Corporate Fleet Management System

Enterprise-grade fleet management system for 500+ vehicles. Self-hosted web application built with Python.

## Tech Stack

- **Backend**: FastAPI (async) + SQLAlchemy 2.0 + Alembic
- **Frontend**: Jinja2 + HTMX + Alpine.js + TailwindCSS
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7 + Celery
- **File Storage**: MinIO (S3-compatible)
- **Auth**: JWT + session cookies

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12 (conda recommended)

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env with your settings
```

### 2. Start infrastructure

```bash
docker compose up -d db redis minio
```

### 3. Install dependencies

```bash
conda create -n fleet-core python=3.12 -c conda-forge
conda activate fleet-core
pip install -e ".[dev]"
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Create superuser

```bash
python scripts/create_superuser.py
```

### 6. Seed demo data (optional)

```bash
python scripts/seed_data.py
```

### 7. Run the application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

## Features

### Modules

| Module | Description |
|--------|------------|
| **Vehicles** | Registry of 500+ vehicles with full specs, photos, QR codes |
| **Drivers** | Driver management with license/medical tracking |
| **Mileage** | Mileage logging with anomaly detection |
| **Maintenance** | Scheduled/unscheduled maintenance with Kanban view |
| **Expenses** | Cost tracking by category, fuel consumption analysis |
| **Contracts** | Leasing, insurance, service contracts with expiry alerts |
| **Documents** | File upload/download via MinIO (S3) |
| **Reports** | TCO, fleet utilization, fuel analysis with Excel/CSV export |
| **Notifications** | In-app, email (SMTP), Telegram alerts |
| **Audit Log** | Complete audit trail of all actions |

### Dashboard

- Fleet overview with vehicle status distribution
- Attention alerts (overdue maintenance, expiring contracts/licenses)
- Expense chart with category breakdown
- Top expensive vehicles
- Maintenance statistics

### Roles

| Role | Access |
|------|--------|
| `admin` | Full system access |
| `fleet_manager` | Vehicle, driver, maintenance, expense, contract management |
| `driver` | View assigned vehicles, submit mileage |
| `viewer` | Read-only dashboards and reports |

### i18n

Supported languages: Russian, English, Kazakh, Turkish.

## API

REST API available at `/api/v1/`:

- `POST /api/v1/auth/login` — authenticate
- `GET /api/v1/vehicles` — list vehicles
- `GET /api/v1/reports/fleet-utilization` — fleet stats
- `GET /api/v1/reports/export/tco.xlsx` — download Excel report
- Full Swagger docs at `/docs`

## Development

### Run tests

```bash
pytest tests/ -v
```

### Run linter

```bash
ruff check app/
```

### Generate migration

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Celery worker (for background tasks)

```bash
celery -A app.tasks.celery_app worker -l info
celery -A app.tasks.celery_app beat -l info
```

## Project Structure

```
app/
├── api/v1/          # REST API endpoints
├── web/             # Web UI routes (Jinja2 + HTMX)
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response schemas
├── services/        # Business logic layer
├── repositories/    # Data access layer
├── tasks/           # Celery background tasks
├── templates/       # Jinja2 templates
├── i18n/            # Translation files (ru, en, kz, tr)
└── utils/           # Security, S3, email, export utilities
```

## Environment Variables

See `.env.example` for all configuration options:

- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `SECRET_KEY` — JWT signing key
- `MINIO_*` — MinIO/S3 configuration
- `SMTP_*` — Email server settings
- `TELEGRAM_*` — Telegram Bot API settings

## License

Proprietary. Internal use only.
