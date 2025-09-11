# syntax=docker/dockerfile:1

# --- Frontend build stage ---
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install --legacy-peer-deps
COPY frontend/ ./
RUN npm run build

# --- Backend build stage ---
FROM python:3.11-slim AS backend-build
WORKDIR /app

# Install system deps for Python packages
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy backend and requirements
COPY backend/ ./backend/
COPY backend/requirements.txt ./backend/requirements.txt
COPY pyproject.toml ./pyproject.toml

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r backend/requirements.txt

# --- Final stage ---
FROM python:3.11-slim
WORKDIR /app

# Copy backend and built frontend


# Copy backend, datascience, and built frontend
COPY --from=backend-build /app/backend /app/backend
COPY datascience /app/datascience
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Copy requirements and config
COPY backend/requirements.txt ./backend/requirements.txt
COPY pyproject.toml ./pyproject.toml

# Install Python dependencies in final stage
RUN pip install --upgrade pip && pip install -r backend/requirements.txt

# Expose port
EXPOSE 8000


# Set environment variables
ENV DATABASE_URL=sqlite:///data/crosswalk.db
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend:/app/datascience

# Create persistent data volume for SQLite
VOLUME ["/app/data"]

# Entrypoint: seed DB if needed, then run Uvicorn
CMD ["sh", "-c", "python backend/seed_data.py; uvicorn backend.app:app --host 0.0.0.0 --port 8000 --log-level info"]
