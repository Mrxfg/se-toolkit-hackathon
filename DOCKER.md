# 🐳 Docker Setup Guide

## Quick Start

Run everything with one command:

```bash
docker-compose up --build
```

## 📋 Prerequisites

- Docker installed
- Docker Compose installed
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

## 🚀 Setup Steps

### 1. Configure Bot Token

Create `.env` file in `bot/` directory:

```bash
cd bot
cp .env.example .env
```

Edit `bot/.env` and add your bot token:

```env
BOT_TOKEN=your_actual_telegram_bot_token
API_URL=http://backend:8000
```

### 2. Start All Services

From the project root:

```bash
docker-compose up --build
```

This will start:
- 🗄️ PostgreSQL database (port 5432)
- 🚀 FastAPI backend (port 8000)
- 🤖 Telegram bot

### 3. Run Database Migrations

In a new terminal, run migrations:

```bash
docker exec -it carbot-backend python migrate.py
```

### 4. Verify Everything Works

- Backend API: http://localhost:8000/docs
- Database: `localhost:5432` (user: postgres, password: postgres123)
- Bot: Open Telegram and send `/start` to your bot

## 🛠️ Useful Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f bot
docker-compose logs -f backend
docker-compose logs -f db
```

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Volumes (⚠️ Deletes database data)

```bash
docker-compose down -v
```

### Restart a Service

```bash
docker-compose restart bot
docker-compose restart backend
```

### Access Container Shell

```bash
# Backend
docker exec -it carbot-backend bash

# Bot
docker exec -it carbot-bot bash

# Database
docker exec -it carbot-db psql -U postgres -d carbot
```

### Rebuild After Code Changes

```bash
docker-compose up --build
```

## 🔧 Configuration

### Database Connection

The backend automatically connects to the database using these settings (defined in `docker-compose.yml`):

```
DB_HOST=db          # Docker service name
DB_NAME=carbot
DB_USER=postgres
DB_PASSWORD=postgres123
DB_PORT=5432
```

### API URL

The bot connects to the backend using:

```
API_URL=http://backend:8000
```

⚠️ **Important**: Use service names (`db`, `backend`) not `localhost` when services communicate inside Docker!

## 📊 Database Management

### Backup Database

```bash
docker exec carbot-db pg_dump -U postgres carbot > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker exec -i carbot-db psql -U postgres carbot
```

### Access Database

```bash
docker exec -it carbot-db psql -U postgres -d carbot
```

## 🐛 Troubleshooting

### Bot can't connect to backend

**Problem**: `Connection refused` or `Name or service not known`

**Solution**: Make sure `API_URL=http://backend:8000` in `bot/.env` (not `localhost`)

### Database connection failed

**Problem**: Backend can't connect to database

**Solution**: Check that `DB_HOST=db` in backend environment (not `localhost`)

### Port already in use

**Problem**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**: 
```bash
# Stop conflicting service or change port in docker-compose.yml
docker-compose down
# Change ports in docker-compose.yml if needed
```

### Migrations not applied

**Problem**: Tables don't exist

**Solution**:
```bash
docker exec -it carbot-backend python migrate.py
```

### Bot not responding

**Problem**: Bot doesn't reply to messages

**Solution**:
1. Check bot token is correct in `bot/.env`
2. Check logs: `docker-compose logs -f bot`
3. Verify backend is running: `curl http://localhost:8000/docs`

## 🔄 Development Workflow

### Making Code Changes

1. Edit code locally
2. Rebuild and restart:
   ```bash
   docker-compose up --build
   ```

### Hot Reload (Development)

For faster development, you can mount code as volumes. Add to `docker-compose.yml`:

```yaml
backend:
  volumes:
    - ./carbot-backend:/app
  command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

bot:
  volumes:
    - ./bot:/app
```

## 🌐 Production Deployment

For production, consider:

1. **Use secrets management** instead of `.env` files
2. **Set strong passwords** for database
3. **Use environment-specific configs**
4. **Enable SSL/TLS** for API
5. **Set up monitoring** and logging
6. **Use Docker secrets** for sensitive data
7. **Configure restart policies** properly

Example production `docker-compose.yml` additions:

```yaml
services:
  backend:
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
  
  db:
    restart: unless-stopped
    volumes:
      - /var/lib/postgresql/data:/var/lib/postgresql/data
```

## 📝 Notes

- Database data persists in Docker volume `postgres_data`
- Logs are available via `docker-compose logs`
- Services automatically restart on failure
- Backend runs on port 8000, accessible at http://localhost:8000

---

Need help? Check the main [README.md](../README.md) or open an issue!
