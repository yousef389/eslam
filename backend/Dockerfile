FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Build stage
# ============================================
FROM base AS builder

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# Production stage
# ============================================
FROM base AS production

# Copy installed dependencies
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd -r erpuser && useradd -r -g erpuser -d /app -s /sbin/nologin erpuser

# Create upload directories
RUN mkdir -p /app/uploads/telegram /app/uploads/ai/temp && \
    chown -R erpuser:erpuser /app

# Copy application code
COPY --chown=erpuser:erpuser . .

# Switch to non-root user
USER erpuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
