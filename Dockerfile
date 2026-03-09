# Production image — multi-stage build
# Stage 1: install dependencies
FROM python:3.14-slim AS builder

WORKDIR /build

COPY requirements/prod.txt requirements/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements/prod.txt


# Stage 2: lean runtime image
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.prod

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy project source
COPY djangoapi/ .

# Create non-root user for security
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    mkdir -p logs staticfiles && \
    chown -R appuser:appgroup /app

USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "-m", "gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "60", \
     "--access-logfile", "-"]
