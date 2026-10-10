==========================================
Stage 1: Build & Dependencies Layer
==========================================
FROM python:3.11-slim-bullseye AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends 
build-essential 
gcc 
&& rm -rf /var/lib/apt/lists/*
COPY requirements.txt . RUN pip install --no-cache-dir --user -r requirements.txt
==========================================
Stage 2: Minimal Distroless/Production Runtime Layer
==========================================
FROM python:3.11-slim-bullseye AS runner
WORKDIR /app
Non-root user for security compliance (Senior DevOps Standard)
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser
Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local
Copy application source code
COPY . .
Persistent storage directories setup & permission grant
RUN mkdir -p /app/storage/slips /app/storage/daily_reports && 
chown -R appuser:appuser /app
ENV PATH=/home/appuser/.local/bin:$PATH 
PYTHONUNBUFFERED=1 
PYTHONDONTWRITEBYTECODE=1
USER appuser
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 
CMD python -c "import socket; sys.exit(0)"
CMD ["python", "run.py"]
