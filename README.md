This is a repository for a public photography server.

# Getting Started

## Prerequisites

- Python 3.12+
- Node.js 18+
- UV package manager
- PostgreSQL (for production)

## Development

### Quick Start with Docker Compose (Recommended)

The easiest way to run the entire stack:

```bash
# Start all services (database, API, frontend)
cd docker_compose
./docker_compose.sh

# View logs
./docker_compose.sh logs -f

# Stop all services
./docker_compose.sh down
```

**Alternative using individual compose files:**
```bash
cd docker_compose
docker compose -f compose.postgres.yaml -f compose.api.yaml -f compose.frontend.yaml up -d
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

### Local Development (Alternative)

If you prefer to run services locally:

#### 1. Start PostgreSQL
```bash
# Using Docker for just the database
cd docker_compose
./docker_compose.sh --exclude=api,frontend

# Or install PostgreSQL locally and create database:
createdb photography_server
```

#### 2. Run Database Migrations
```bash
cd src/pgs_db
uv run alembic upgrade head
```

#### 3. Start the Backend API
```bash
cd src/pgs_api
uv run run.py
```

#### 4. Start the Frontend
```bash
cd src/frontend
npm run dev
```

### Development Workflow

#### Docker Compose Development
- Modify code locally - changes are mounted into containers
- API and frontend will reload automatically
- Database data persists across container restarts
- Use `docker-compose logs api` or `docker-compose logs frontend` to view specific service logs

#### Environment Variables

For local development, you can override database settings:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=photography_server
export DB_USER=postgres
export DB_PASSWORD=postgres
```

### Code Formatting

```bash
# Format API code
cd src/pgs_api
make format

# Lint frontend code
cd src/frontend
npm run lint
```
