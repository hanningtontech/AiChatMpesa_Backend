# Docker Setup for AI Chat M-Pesa Backend

Simple Docker setup for the M-Pesa backend application.

## Quick Start

1. **Setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your M-Pesa credentials
   ```

2. **Configure ngrok**:
   - Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
   - Update `ngrok.yml` with your token

3. **Start everything**:
   ```bash
   ./start.sh
   ```

That's it! The script will:
- Build the Docker image
- Start the M-Pesa backend server
- Start ngrok tunnel for callbacks
- Show you all the URLs

## Services

- **Backend**: http://localhost:8001
- **Health Check**: http://localhost:8001/health
- **Ngrok Dashboard**: http://localhost:4040

## Manual Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Access container shell
docker-compose exec mpesa-backend bash
```

## Environment Variables

Required in `.env`:
- `GOOGLE_API_KEY` - Your Google AI API key
- `MPESA_CONSUMER_KEY` - From Safaricom Developer Portal
- `MPESA_CONSUMER_SECRET` - From Safaricom Developer Portal
- `MPESA_PASSKEY` - From Safaricom Developer Portal
- `MPESA_CALLBACK_URL` - Your ngrok URL + `/mpesa/callback`
