# 🐳 Docker Setup Guide

This guide explains how to run CarBot using Docker and Docker Compose.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Services Overview](#services-overview)
- [Docker Commands](#docker-commands)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## Prerequisites

Before you begin, ensure you have:

- **Docker Desktop** installed ([Download here](https://www.docker.com/products/docker-desktop))
- **Docker Compose** (included with Docker Desktop)
- **Telegram Bot Token** from [@BotFather](https://t.me/botfather)
- At least **2GB RAM** available
- At least **5GB disk space**

### Verify Installation

```bash
docker --version
# Docker version 20.10.0 or higher

docker-compose --version
# docker-compose version 1.29.0 or higher
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Mrxfg/se-toolkit-hackathon.git
cd carbot
```

### 2. Configure Bot Token

```bash
# Copy example environment file
cp bot/.env.example bot/.env

# Edit the file and add your bot token
# On Windows: notepad bot/.env
# On Mac/Linux: nano bot/.env
```

**bot/.env:**
```env
BOT_TOKEN=your_telegram_bot_token_here
API_URL=http://backend:8000
```

### 3. Start All Services

```bash
docker-compose up --build
```

This command will:
- Build Docker images for bot and backend
- Pull PostgreSQL image
- Create a network for services
- Start all containers

### 4. Run Database Migrations

Open a **new terminal** and run:

```bash
docker exec -it carbot-backend python migrate.py
```

You should see:
```
Starting database migrations...
0. Creating tables if they don't exist...
1. Enabling pg_trgm extension...
...
✅ All migrations completed successfully!
```

### 5. Test Your Bot

Open Telegram and search for your bot, then send `/start`

---

## Services Overview

CarBot uses three Docker containers:

### 1. PostgreSQL Database (`db`)

**Image:** `postgres:15`  
**Container Name:** `carbot-db`  
**Port:** `5432`

**Purpose:** Stores all data (users, cars, images, messages)

**Volume:** `postgres_data` - Persists data between restarts

**Environment Variables:**
- `POSTGRES_DB=carbot`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD` - Set via `.env` file

### 2. FastAPI Backend (`backend`)

**Build:** `./carbot-backend/Dockerfile`  
**Container Name:** `carbot-backend`  
**Port:** `8000`

**Purpose:** REST API for business logic and data validation

**Dependencies:** Waits for `db` to be ready

**Environment Variables:**
- `DB_NAME=carbot`
- `DB_USER=postgres`
- `DB_PASSWORD` - From `.env`
- `DB_HOST=db`
- `DB_PORT=5432`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Telegram Bot (`bot`)

**Build:** `./bot/Dockerfile`  
**Container Name:** `carbot-bot`

**Purpose:** Handles user interactions via Telegram

**Dependencies:** Waits for `backend` to be ready

**Environment Variables:**
- `BOT_TOKEN` - From `bot/.env`
- `API_URL=http://backend:8000`

---

## Docker Commands

### Starting Services

```bash
# Start all services (foreground)
docker-compose up

# Start all services (background/detached)
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Start specific service
docker-compose up bot
```

### Stopping Services

```bash
# Stop all services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (deletes data!)
docker-compose down -v
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# View specific service logs
docker-compose logs bot
docker-compose logs backend
docker-compose logs db

# Last 100 lines
docker-compose logs --tail=100
```

### Accessing Containers

```bash
# Execute command in backend container
docker exec -it carbot-backend python migrate.py

# Open bash shell in backend
docker exec -it carbot-backend bash

# Open bash shell in bot
docker exec -it carbot-bot bash

# Access PostgreSQL
docker exec -it carbot-db psql -U postgres -d carbot
```

### Managing Images

```bash
# List images
docker images

# Remove unused images
docker image prune

# Remove specific image
docker rmi carbot-backend
docker rmi carbot-bot
```

### Managing Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect carbot_postgres_data

# Remove volume (deletes all data!)
docker volume rm carbot_postgres_data
```

---

## Configuration

### Environment Variables

#### Root `.env` (Optional)

Create a `.env` file in the project root for shared variables:

```env
DB_PASSWORD=your_secure_password_here
```

#### Backend `.env`

Not needed when using Docker Compose (configured in `docker-compose.yml`)

#### Bot `.env`

**Required!** Create `bot/.env`:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
API_URL=http://backend:8000
```

### Port Configuration

To change exposed ports, edit `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8080:8000"  # Change 8080 to your preferred port
  
  db:
    ports:
      - "5433:5432"  # Change 5433 to your preferred port
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "Port already in use"

**Error:**
```
Error starting userland proxy: listen tcp 0.0.0.0:5432: bind: address already in use
```

**Solution:**
```bash
# Option 1: Stop the conflicting service
# On Windows:
net stop postgresql-x64-13

# On Mac/Linux:
sudo systemctl stop postgresql

# Option 2: Change the port in docker-compose.yml
ports:
  - "5433:5432"  # Use 5433 instead
```

#### 2. "Cannot connect to Docker daemon"

**Error:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solution:**
- Make sure Docker Desktop is running
- Restart Docker Desktop
- On Linux: `sudo systemctl start docker`

#### 3. "TLS handshake timeout" (Bot)

**Error:**
```
ssl.SSLWantReadError: The operation did not complete (read)
TimeoutError
```

**Solution:**
- Check your internet connection
- Restart Docker Desktop
- Configure Docker DNS:
  - Docker Desktop → Settings → Docker Engine
  - Add:
    ```json
    {
      "dns": ["8.8.8.8", "8.8.4.4"]
    }
    ```
  - Click "Apply & Restart"

#### 4. "Database connection refused"

**Error:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check if database is running
docker-compose ps

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db

# Wait for database to be ready (takes 5-10 seconds)
```

#### 5. "Migration failed"

**Error:**
```
❌ Migration failed: relation "users" already exists
```

**Solution:**
```bash
# This is usually safe to ignore if tables exist
# To reset database (WARNING: deletes all data):
docker-compose down -v
docker-compose up -d db
# Wait 10 seconds
docker exec -it carbot-backend python migrate.py
```

#### 6. "Bot not responding"

**Checklist:**
- [ ] Is `BOT_TOKEN` correct in `bot/.env`?
- [ ] Is the bot container running? (`docker-compose ps`)
- [ ] Check bot logs: `docker-compose logs bot`
- [ ] Is backend running? (`curl http://localhost:8000/docs`)
- [ ] Did you run migrations?

**Solution:**
```bash
# Restart bot
docker-compose restart bot

# Check logs
docker-compose logs -f bot

# Verify token
cat bot/.env
```

#### 7. "Image pull timeout"

**Error:**
```
failed to fetch oauth token: Post "https://auth.docker.io/token": net/http: TLS handshake timeout
```

**Solution:**
```bash
# Option 1: Check if images already exist
docker images | grep carbot

# If they exist, run without rebuild:
docker-compose up

# Option 2: Pull base image manually
docker pull python:3.12-slim

# Option 3: Configure Docker proxy (if behind corporate firewall)
```

#### 8. "Permission denied" (Linux)

**Error:**
```
Got permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, then:
docker-compose up
```

---

## Production Deployment

### Security Best Practices

1. **Use Strong Passwords**
   ```env
   DB_PASSWORD=$(openssl rand -base64 32)
   ```

2. **Don't Expose Database Port**
   ```yaml
   db:
     # Remove or comment out:
     # ports:
     #   - "5432:5432"
   ```

3. **Use Docker Secrets** (Docker Swarm)
   ```yaml
   secrets:
     db_password:
       external: true
   ```

4. **Enable SSL/TLS**
   - Use reverse proxy (nginx, Caddy)
   - Configure HTTPS for backend API

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
  
  bot:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

### Health Checks

Add health checks:

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Logging

Configure logging:

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Backup Database

```bash
# Backup
docker exec carbot-db pg_dump -U postgres carbot > backup.sql

# Restore
docker exec -i carbot-db psql -U postgres carbot < backup.sql
```

---

## Monitoring

### Check Service Status

```bash
# List running containers
docker-compose ps

# Check resource usage
docker stats

# Check container health
docker inspect carbot-backend | grep -A 10 Health
```

### View Metrics

```bash
# Backend API metrics
curl http://localhost:8000/docs

# Database connections
docker exec carbot-db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## Useful Commands Cheat Sheet

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart bot

# Run migrations
docker exec -it carbot-backend python migrate.py

# Access database
docker exec -it carbot-db psql -U postgres -d carbot

# Stop everything
docker-compose down

# Clean up (removes data!)
docker-compose down -v

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

**Need help?** Open an issue on [GitHub](https://github.com/Mrxfg/se-toolkit-hackathon/issues)

---

*Last updated: April 2026*
