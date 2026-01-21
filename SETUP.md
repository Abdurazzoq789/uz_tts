# Detailed Setup Guide

This guide provides step-by-step instructions for setting up the Uzbek TTS Telegram Bot from scratch.

## Step 1: Google Cloud Setup

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "uzbek-tts-bot")
4. Click "Create"

### 1.2 Enable Text-to-Speech API

1. In the Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Text-to-Speech API"
3. Click on it and press "Enable"
4. Wait for API to be enabled

### 1.3 Create Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click "Create Service Account"
3. Enter details:
   - **Name**: `uzbek-tts-bot`
   - **Description**: "Service account for Uzbek TTS Telegram bot"
4. Click "Create and Continue"
5. Grant role: **Cloud Text-to-Speech API User**
6. Click "Continue" → "Done"

### 1.4 Create Service Account Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click "Add Key" → "Create new key"
4. Select **JSON** format
5. Click "Create"
6. **Save the downloaded JSON file securely** (e.g., `gcp-credentials.json`)
7. **NEVER commit this file to git!**

### 1.5 Verify Setup

```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-credentials.json

# Test with gcloud (optional)
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
```

## Step 2: Telegram Bot Setup

### 2.1 Create Bot with BotFather

1. Open Telegram
2. Search for [@BotFather](https://t.me/botfather)
3. Start conversation: `/start`
4. Create bot: `/newbot`
5. Follow prompts:
   - **Bot name**: Choose a display name (e.g., "Uzbek TTS Bot")
   - **Username**: Choose unique username ending in "bot" (e.g., "uzbek_tts_bot")
6. **Copy the bot token** (looks like `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
7. Save it securely

### 2.2 Configure Bot (Optional but Recommended)

**Set description**:
```
/setdescription
```
Then send:
```
Converts Uzbek text (Latin & Cyrillic) to speech. Post a message with #audio in your channel!
```

**Set about text**:
```
/setabouttext
```
Then send:
```
Uzbek TTS Bot - Converts text to speech using Google Cloud TTS
```

**Set bot photo** (optional):
- Create/find a suitable bot avatar
- `/setuserpic` and upload image

### 2.3 Create Telegram Channel

If you don't have a channel:

1. Open Telegram
2. Click menu → "New Channel"
3. Enter channel info:
   - **Name**: Your channel name
   - **Description**: Channel description
4. Choose channel type (Public or Private)
5. Create channel

### 2.4 Add Bot as Admin

1. Open your channel
2. Click channel name → "Administrators"
3. Click "Add Administrator"
4. Search for your bot username (e.g., `@uzbek_tts_bot`)
5. Select the bot
6. Grant permissions:
   - ✅ **Post Messages** (required)
   - ✅ **Edit Messages** (optional)
   - ✅ **Delete Messages** (optional)
7. Click "Done"

**Important**: The bot MUST be an admin to receive channel posts!

## Step 3: Local Development Setup

### 3.1 Prerequisites

Install Python 3.11+:

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**macOS** (using Homebrew):
```bash
brew install python@3.11
```

**Windows**:
- Download from [python.org](https://www.python.org/downloads/)

### 3.2 Clone/Navigate to Project

```bash
cd /mnt/sdb1/Projects/antigravity/uzbek_tts_bot
```

### 3.3 Create Virtual Environment

```bash
python3.11 -m venv venv
```

**Activate**:

**Linux/macOS**:
```bash
source venv/bin/activate
```

**Windows**:
```cmd
venv\Scripts\activate
```

### 3.4 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.5 Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```bash
# Replace with your actual values
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/gcp-credentials.json

# Optional (use defaults or customize)
TRIGGER_HASHTAG=#audio
MAX_TEXT_LENGTH=4500
VOICE_NAME=uz-UZ-Standard-A
LOG_LEVEL=INFO
```

**Important**: Use **absolute paths** for `GOOGLE_APPLICATION_CREDENTIALS`!

### 3.6 Run the Bot

```bash
python main.py
```

You should see:
```
============================================================
Uzbek TTS Telegram Bot Starting
============================================================
Trigger hashtag: #audio
Max text length: 4500
Voice: uz-UZ-Standard-A
============================================================
Bot initialized: @uzbek_tts_bot (Uzbek TTS Bot)
Handlers and middleware registered
Starting bot polling...
```

## Step 4: Testing

### 4.1 Basic Test

1. Go to your Telegram channel
2. Post a message:
   ```
   Salom dunyo! #audio
   ```
3. The bot should reply with a voice message

### 4.2 Test Cyrillic

```
Салом дунё! #audio
```

### 4.3 Test Long Text

Post a message with 5000+ characters and `#audio`. The bot should send multiple voice messages.

## Step 5: Production Deployment (Docker)

### 5.1 Install Docker

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in
```

**macOS/Windows**:
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 5.2 Build Image

```bash
docker build -t uzbek-tts-bot .
```

### 5.3 Run with Docker Compose

1. **Update `docker-compose.yml`** with correct credentials path:
   ```yaml
   volumes:
     - /absolute/path/to/gcp-credentials.json:/app/credentials.json:ro
   ```

2. **Start bot**:
   ```bash
   docker-compose up -d
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

4. **Stop bot**:
   ```bash
   docker-compose down
   ```

### 5.4 Run in Background (Production)

```bash
# Start
docker-compose up -d

# Check status
docker-compose ps

# Restart
docker-compose restart

# Stop
docker-compose down
```

## Step 6: Monitoring & Maintenance

### 6.1 View Logs

**Local**:
- Logs are printed to console

**Docker**:
```bash
docker-compose logs -f
docker-compose logs --tail=100
```

### 6.2 Monitor Google Cloud Usage

1. Go to **Google Cloud Console**
2. Navigate to **APIs & Services** → **Dashboard**
3. Click **Text-to-Speech API**
4. View usage metrics and quotas

### 6.3 Set Up Alerts (Optional)

In Google Cloud Console:
1. Go to **Monitoring** → **Alerting**
2. Create alert for TTS API quota usage
3. Set notification channel (email, SMS)

## Troubleshooting

### Issue: Bot doesn't respond to channel messages

**Solutions**:
1. Verify bot is admin in channel: Channel → Administrators
2. Check "Post Messages" permission is enabled
3. Check bot is running: `docker-compose ps` or check logs
4. Verify `.env` has correct `BOT_TOKEN`

### Issue: `google.auth.exceptions.DefaultCredentialsError`

**Solutions**:
1. Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
2. Ensure path is absolute (not relative)
3. Verify JSON file exists and is readable
4. Check service account has TTS API permissions

### Issue: Audio quality is poor

**Solutions**:
1. Try different voice:
   - `uz-UZ-Standard-A` (female)
   - Check [Google Cloud docs](https://cloud.google.com/text-to-speech/docs/voices) for more
2. Adjust `speaking_rate` in `tts_engine.py` (default: 1.0)

### Issue: Bot crashes frequently

**Solutions**:
1. Check logs for specific errors
2. Verify network connectivity
3. Ensure sufficient memory (Docker: increase limits)
4. Check Google Cloud quota limits

## Security Best Practices

1. **Never commit credentials**:
   - Add `.env` and `*.json` to `.gitignore`
   - Use environment variables

2. **Use minimal permissions**:
   - Service account: only TTS API
   - Bot: only necessary channel permissions

3. **Regular updates**:
   ```bash
   pip install --upgrade -r requirements.txt
   docker-compose pull
   docker-compose up -d
   ```

4. **Monitor usage**:
   - Check Google Cloud billing
   - Set budget alerts

## Next Steps

- ✅ Set up monitoring and alerts
- ✅ Configure log aggregation (ELK, CloudWatch, etc.)
- ✅ Implement backup strategy (logs, config)
- ✅ Test disaster recovery
- ✅ Document team member access

---

Congratulations! Your Uzbek TTS Telegram Bot is now running! 🎉
