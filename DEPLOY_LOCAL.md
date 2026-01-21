# Simple Local Deployment Guide

## Quick Setup (Without Docker)

### 1. Install System Requirements

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y postgresql redis-server python3-pip ffmpeg

# Start services
sudo systemctl start postgresql
sudo systemctl start redis
sudo systemctl enable postgresql
sudo systemctl enable redis
```

### 2. Database Setup

```bash
# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE uzbek_tts;
CREATE USER uzbek_bot WITH PASSWORD 'uzbek_bot_pass';
GRANT ALL PRIVILEGES ON DATABASE uzbek_tts TO uzbek_bot;
ALTER DATABASE uzbek_tts OWNER TO uzbek_bot;
\q
EOF
```

### 3. Configure Bot

Create `.env` file:

```bash
cat > .env <<'EOF'
# Bot Configuration
BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Database
DATABASE_URL=postgresql+asyncpg://uzbek_bot:uzbek_bot_pass@localhost:5432/uzbek_tts

# Redis
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Payments (configure these)
TELEGRAM_PAYMENT_ENABLED=True
MANUAL_PAYMENT_ENABLED=True
MANUAL_PAYMENT_CARD_NUMBER=
MANUAL_PAYMENT_CARD_HOLDER=

# Limits
FREE_TIER_TTS_LIMIT=3
PAID_MONTHLY_PRICE=10.0

# Admin (your Telegram user ID)
ADMIN_USER_IDS=

# Logging
LOG_LEVEL=INFO
EOF
```

**Important:** Edit `.env` and set:
- `BOT_TOKEN` - Get from @BotFather
- `ADMIN_USER_IDS` - Your Telegram user ID
- Payment card details (if using manual payments)

### 4. Install Python Dependencies

```bash
# Install in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Seed default tariffs
python -m database.seed
```

### 6. Run Services

**Terminal 1 - Bot:**
```bash
source venv/bin/activate
python main.py
```

**Terminal 2 - Celery Worker:**
```bash
source venv/bin/activate
celery -A tasks worker --loglevel=info -Q tts
```

That's it! Your bot is running.

---

## Testing

1. **Start bot:** Message `/start` to your bot
2. **Test free tier:** Send "Salom dunyo" 3 times
3. **Test limit:** 4th message should show upgrade prompt
4. **Test admin:** Reply to a message with `/admin_info`

---

## Production Enhancements

### Run as System Services

Create systemd service files:

**Bot Service:** `/etc/systemd/system/uzbek-tts-bot.service`
```ini
[Unit]
Description=Uzbek TTS Telegram Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/path/to/uzbek_tts_bot
Environment="PATH=/path/to/uzbek_tts_bot/venv/bin"
ExecStart=/path/to/uzbek_tts_bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Celery Service:** `/etc/systemd/system/uzbek-tts-worker.service`
```ini
[Unit]
Description=Uzbek TTS Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/path/to/uzbek_tts_bot
Environment="PATH=/path/to/uzbek_tts_bot/venv/bin"
ExecStart=/path/to/uzbek_tts_bot/venv/bin/celery -A tasks worker --loglevel=info -Q tts
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable uzbek-tts-bot
sudo systemctl enable uzbek-tts-worker
sudo systemctl start uzbek-tts-bot
sudo systemctl start uzbek-tts-worker
```

---

## Troubleshooting

**Bot won't start:**
```bash
# Check logs
tail -f /var/log/syslog | grep uzbek

# Test database connection
python -c "from database import init_database; import asyncio; asyncio.run(init_database()); print('OK')"
```

**Queue not processing:**
```bash
celery -A tasks inspect active
redis-cli ping
```

**Database issues:**
```bash
sudo -u postgres psql uzbek_tts -c "SELECT COUNT(*) FROM users;"
```

---

## Monitoring

```bash
# Check services
systemctl status uzbek-tts-bot
systemctl status uzbek-tts-worker
systemctl status postgresql
systemctl status redis

# View logs
journalctl -u uzbek-tts-bot -f
journalctl -u uzbek-tts-worker -f
```

---

## Backup

```bash
# Backup database
sudo -u postgres pg_dump uzbek_tts > backup_$(date +%Y%m%d).sql

# Restore
sudo -u postgres psql uzbek_tts < backup_20260121.sql
```
