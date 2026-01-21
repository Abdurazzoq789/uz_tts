#!/bin/bash
# Uzbek TTS Bot - Automated Setup Script

set -e

echo "==================================="
echo "Uzbek TTS Bot - Setup Script"
echo "==================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Not in virtual environment. Activating...${NC}"
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    source venv/bin/activate
fi

echo "Step 1: Checking Python dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

echo ""
echo "Step 2: Checking .env file..."
if [ ! -f ".env" ]; then
    echo -e "${RED}✗${NC} .env file not found!"
    echo "Creating from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env and set:${NC}"
    echo "  - BOT_TOKEN"
    echo "  - ADMIN_USER_IDS"
    echo "  - Payment details (if needed)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check critical env vars
source .env
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
    echo -e "${RED}✗${NC} BOT_TOKEN not set in .env"
    exit 1
fi
echo -e "${GREEN}✓${NC} .env configured"

echo ""
echo "Step 3: Checking PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo -e "${RED}✗${NC} PostgreSQL not installed"
    echo "Install with: sudo apt install postgresql"
    exit 1
fi

if ! sudo systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
fi
echo -e "${GREEN}✓${NC} PostgreSQL running"

echo ""
echo "Step 4: Checking Redis..."
if ! command -v redis-cli &> /dev/null; then
    echo -e "${RED}✗${NC} Redis not installed"
    echo "Install with: sudo apt install redis-server"
    exit 1
fi

if ! sudo systemctl is-active --quiet redis; then
    echo "Starting Redis..."
    sudo systemctl start redis
fi
echo -e "${GREEN}✓${NC} Redis running"

echo ""
echo "Step 5: Setting up database..."

# Create database if not exists
sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw uzbek_tts || {
    echo "Creating database..."
    sudo -u postgres psql -c "CREATE DATABASE uzbek_tts;"
    sudo -u postgres psql -c "CREATE USER uzbek_bot WITH PASSWORD 'uzbek_bot_pass';"
}

# Grant permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE uzbek_tts TO uzbek_bot;" 2>/dev/null || true
sudo -u postgres psql -c "ALTER DATABASE uzbek_tts OWNER TO uzbek_bot;" 2>/dev/null || true

# Grant schema permissions (PostgreSQL 15+)
sudo -u postgres psql -d uzbek_tts -c "GRANT ALL ON SCHEMA public TO uzbek_bot;" 2>/dev/null || true

echo -e "${GREEN}✓${NC} Database configured"

echo ""
echo "Step 6: Running database migrations..."
alembic upgrade head
echo -e "${GREEN}✓${NC} Migrations complete"

echo ""
echo "Step 7: Seeding default tariffs..."
python -m database.seed
echo -e "${GREEN}✓${NC} Database seeded"

echo ""
echo "Step 8: Testing database connection..."
python -c "from database import init_database; import asyncio; asyncio.run(init_database()); print('✓ Database connection successful')"

echo ""
echo -e "${GREEN}==================================="
echo "✓ Setup Complete!"
echo "===================================${NC}"
echo ""
echo "To start the bot:"
echo "  Terminal 1: python main.py"
echo "  Terminal 2: celery -A tasks worker --loglevel=info -Q tts"
echo ""
echo "Or use: ./start.sh"
