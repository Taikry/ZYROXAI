# ==========================================
# Stage 1: Frontend Asset Compilation (Vite + React)
# ==========================================
FROM node:22-slim AS frontend-builder

WORKDIR /build

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

# ==========================================
# Stage 2: Production Python Backend Runtime
# ==========================================
FROM python:3.12-slim

WORKDIR /app

# Run the application as an unprivileged user in production
RUN groupadd --system app && useradd --system --gid app --home-dir /app app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app . .
COPY --from=frontend-builder --chown=app:app /build/dist ./dist

# SQLite and runtime permission handling
RUN chown app:app /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD ["sh", "-c", "curl --fail --silent http://127.0.0.1:${PORT:-8000}/ping || exit 1"]

CMD ["sh", "-c", "uvicorn taikry.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
