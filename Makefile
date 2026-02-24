.PHONY: up down build migrate migrate-gen seed test lint format install shell

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

migrate:
	alembic upgrade head

migrate-gen:
	alembic revision --autogenerate -m "$(msg)"

seed:
	python -m scripts.seed_data

test:
	pytest -v

lint:
	ruff check app/ tests/

format:
	ruff format app/ tests/
	ruff check --fix app/ tests/

install:
	uv pip install -e ".[dev]"

shell:
	python -c "import asyncio; from app.database import AsyncSessionLocal; print('DB ready')"

superuser:
	python -m scripts.create_superuser
