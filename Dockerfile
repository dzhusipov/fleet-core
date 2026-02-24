FROM python:3.12-slim

# System deps for weasyprint, qrcode/PIL, postgres client
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    libglib2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system -e ".[dev]"

# Copy application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
