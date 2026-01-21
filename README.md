# 🚀 Uzbek TTS Bot - Quick Start

## Fastest Way to Deploy (3 Steps)

### 1. Configure Bot Token

```bash
# Copy example config
cp .env.example .env

# Edit .env and set these (minimum):
nano .env
```

Required settings:
- `BOT_TOKEN=your_token_from_botfather`
- `ADMIN_USER_IDS=your_telegram_user_id`

### 2. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- ✓ Install Python dependencies
- ✓ Start PostgreSQL and Redis
- ✓ Create database
- ✓ Run migrations
- ✓ Seed default tariffs

### 3. Start Bot

```bash
chmod +x start.sh
./start.sh
```

**Done!** Bot is running. Test by messaging `/start` to your bot.

---

## Manual Setup (If Scripts Fail)

### Install System Dependencies
```bash
sudo apt update
sudo apt install -y postgresql redis-server python3-pip ffmpeg
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Setup Database
```bash
# Start services
sudo systemctl start postgresql redis

# Create database
sudo -u postgres psql <<EOF
CREATE DATABASE uzbek_tts;
CREATE USER uzbek_bot WITH PASSWORD 'uzbek_bot_pass';
GRANT ALL PRIVILEGES ON DATABASE uzbek_tts TO uzbek_bot;
ALTER DATABASE uzbek_tts OWNER TO uzbek_bot;
EOF

# Run migrations
alembic upgrade head

# Seed data
python -m database.seed
```

### Start Services

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

---

## Configuration

Minimum `.env` settings:

```bash
BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=123456789
DATABASE_URL=postgresql+asyncpg://uzbek_bot:uzbek_bot_pass@localhost:5432/uzbek_tts
REDIS_URL=redis://localhost:6379
```

Full configuration options in `.env.example`

---

## Testing

1. **Start bot:** `/start`
2. **Test TTS:** Send "Salom dunyo"
3. **Test limit:** Send 3 texts (free tier)
4. **Test admin:** Reply to message with `/admin_info`
5. **Test subscription:** `/subscription`

---

## Production (systemd services)

See `DEPLOY_LOCAL.md` for systemd service setup to run bot as system services.

---

## Troubleshooting

**Database connection error:**
```bash
sudo systemctl start postgresql
sudo -u postgres psql -d uzbek_tts -c "GRANT ALL ON SCHEMA public TO uzbek_bot;"
```

**Queue not working:**
```bash
sudo systemctl start redis
redis-cli ping
```

**Permission errors:**
```bash
sudo -u postgres psql -d uzbek_tts -c "ALTER DATABASE uzbek_tts OWNER TO uzbek_bot;"
```

---

## File Structure

```
uzbek_tts_bot/
├── setup.sh          # Auto-setup script ⭐
├── start.sh          # Start bot + celery ⭐
├── main.py           # Bot entry point
├── tasks.py          # Celery tasks
├── .env              # Configuration (create from .env.example)
├── database/         # Models, migrations
├── bot/              # Handlers, middleware
└── services/         # Business logic
```

---

## Next Steps

1. ✅ Run `./setup.sh`
2. ✅ Run `./start.sh`
3. ✅ Test bot with `/start`
4. 📝 Configure payment methods (optional)
5. 🚀 Deploy to production server

For production deployment with systemd services, see **DEPLOY_LOCAL.md**
