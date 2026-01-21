# Uzbek TTS Production Deployment Guide

## Quick Start

```bash
# 1. Clone and setup
cd uzbek_tts_bot
cp .env.example .env
# Edit .env with your values

# 2. Start services with Docker
docker-compose up -d

# 3. Initialize database
docker-compose exec bot alembic upgrade head
docker-compose exec bot python -m database.seed

# 4. Bot is ready!
```

## Production Deployment Steps

### 1. Server Setup

**Minimum Requirements:**
- 2 CPU cores
- 4GB RAM
- 20GB storage
- Ubuntu 20.04+ or similar

**Install Dependencies:**
```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose
sudo apt install docker-compose

# Or without Docker:
sudo apt install -y python3.11 python3-pip postgresql-14 redis-server ffmpeg
```

### 2. Configuration

**Create .env file:**
```bash
BOT_TOKEN=your_actual_bot_token
DATABASE_URL=postgresql+asyncpg://uzbek_bot:strong_password@postgres:5432/uzbek_tts
REDIS_URL=redis://redis:6379
ADMIN_USER_IDS=your_telegram_user_id
MANUAL_PAYMENT_CARD_NUMBER=your_card_number
MANUAL_PAYMENT_CARD_HOLDER=Your Name
```

### 3. Database Migration

```bash
# Run migrations
docker-compose exec bot alembic upgrade head

# Seed initial data
docker-compose exec bot python -m database.seed

# Verify
docker-compose exec bot python -c "from database import init_database; import asyncio; asyncio.run(init_database()); print('✅ Database ready')"
```

### 4. Start Services

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f bot
docker-compose logs -f celery_worker

# Check status
docker-compose ps
```

### 5. Verify Deployment

```bash
# Test bot
# Send message to bot: /start

# Test queue
docker-compose exec celery_worker celery -A tasks inspect active

# Test database
docker-compose exec postgres psql -U postgres -d uzbek_tts -c "SELECT COUNT(*) FROM users;"
```

## Monitoring

```bash
# View logs
docker-compose logs -f

# Resource usage
docker stats

# Database size
docker-compose exec postgres psql -U postgres -d uzbek_tts -c "SELECT pg_size_pretty(pg_database_size('uzbek_tts'));"
```

## Backup

```bash
# Database backup
docker-compose exec postgres pg_dump -U postgres uzbek_tts > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U postgres uzbek_tts < backup_20260121.sql
```

## Scaling

**Multiple Celery Workers:**
```bash
docker-compose up -d --scale celery_worker=3
```

**Load Balancing:**
- Use Nginx for multiple bot instances
- Redis Sentinel for high availability
- PostgreSQL replication for read scaling

## Troubleshooting

**Bot not responding:**
```bash
docker-compose logs bot | tail -50
```

**Queue not processing:**
```bash
docker-compose exec celery_worker celery -A tasks inspect stats
```

**Database connection issues:**
```bash
docker-compose exec postgres psql -U postgres -c "SELECT COUNT(*) FROM pg_stat_activity;"
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | ✅ | - | Telegram bot token |
| `DATABASE_URL` | ✅ | localhost | PostgreSQL connection URL |
| `REDIS_URL` | ✅ | localhost | Redis connection URL |
| `ADMIN_USER_IDS` | ✅ | [] | Comma-separated admin IDs |
| `FREE_TIER_TTS_LIMIT` | ❌ | 3 | Free TTS per month |
| `PAID_MONTHLY_PRICE` | ❌ | 10.0 | Subscription price |
| `TELEGRAM_PAYMENT_ENABLED` | ❌ | True | Enable Telegram Stars |
| `MANUAL_PAYMENT_ENABLED` | ❌ | True | Enable manual payments |
| `MANUAL_PAYMENT_CARD_NUMBER` | ⚠️ | "" | Card for manual payments |
| `MANUAL_PAYMENT_CARD_HOLDER` | ⚠️ | "" | Card holder name |
| `LOG_LEVEL` | ❌ | INFO | Logging level |

## Security Checklist

- [ ] Strong database passwords
- [ ] Admin IDs configured
- [ ] `.env` not in git
- [ ] Firewall configured (ports 5432, 6379 not public)
- [ ] Regular backups enabled
- [ ] Bot token kept secure
- [ ] SSL/TLS for external connections

## Production Checklist

- [ ] Environment variables configured
- [ ] Database initialized and seeded
- [ ] Services running (bot, celery, postgres, redis)
- [ ] Test free tier (3 TTS limit)
- [ ] Test paid subscription
- [ ] Test payment flows (both methods)
- [ ] Test admin commands
- [ ] Monitoring configured
- [ ] Backups automated
- [ ] Documentation updated

---

**🎉 Your production SaaS platform is ready!**
