# Football Match Simulator - Deployment Guide

This guide covers multiple deployment options for the Football Match Simulator application, including Docker, Fly.io, and manual deployment.

## Table of Contents
- [Quick Start with Docker](#quick-start-with-docker)
- [Architecture Overview](#architecture-overview)
- [Deployment Options](#deployment-options)
  - [Option 1: Docker Compose (Recommended for Local/Self-Hosted)](#option-1-docker-compose)
  - [Option 2: Fly.io (Cloud Deployment)](#option-2-flyio)
  - [Option 3: Manual Deployment](#option-3-manual-deployment)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)

---

## Quick Start with Docker

The fastest way to run the entire application locally:

```bash
# Clone the repository
git clone https://github.com/Sniffr/simulate.git
cd simulate

# Start both backend and frontend
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

Stop the application:
```bash
docker-compose down
```

---

## Architecture Overview

The application consists of two main components:

1. **Backend (FastAPI)**: Located in `football_sim_backend/`
   - FastAPI REST API
   - SQLite database for simulation history
   - Python 3.12+ required
   - Poetry for dependency management

2. **Frontend (React)**: Located in `dashboard/`
   - React + TypeScript + Vite
   - Tailwind CSS + shadcn/ui
   - Recharts for data visualization
   - Node.js 18+ required

---

## Deployment Options

### Option 1: Docker Compose

**Best for:** Local development, self-hosted servers, quick setup

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

#### Setup Steps

1. **Clone the repository:**
```bash
git clone https://github.com/Sniffr/simulate.git
cd simulate
```

2. **Configure environment variables:**
```bash
# Backend (optional - defaults work out of the box)
cp football_sim_backend/.env.example football_sim_backend/.env

# Frontend
cp dashboard/.env.example dashboard/.env
```

3. **Build and start services:**
```bash
docker-compose up -d --build
```

4. **Verify deployment:**
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Test backend
curl http://localhost:8000/healthz

# Test frontend
curl http://localhost:3000
```

#### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Rebuild after code changes
docker-compose up -d --build

# Remove all data (including database)
docker-compose down -v
```

---

### Option 2: Fly.io

**Best for:** Production cloud deployment, automatic scaling

#### Prerequisites
- Fly.io account (sign up at https://fly.io)
- Fly CLI installed (`curl -L https://fly.io/install.sh | sh`)

#### Backend Deployment

1. **Login to Fly.io:**
```bash
flyctl auth login
```

2. **Deploy backend:**
```bash
cd football_sim_backend

# Create and deploy the app (first time)
flyctl launch --name your-app-name

# Or deploy to existing app
flyctl deploy
```

3. **Configure secrets (if needed):**
```bash
flyctl secrets set DATABASE_URL=your_database_url
```

4. **Get your backend URL:**
```bash
flyctl info
# Note the hostname, e.g., your-app-name.fly.dev
```

#### Frontend Deployment

The frontend can be deployed to:
- **Fly.io Static Sites**
- **Vercel** (recommended)
- **Netlify**
- **Any static hosting**

**Using Vercel:**

1. **Build the frontend:**
```bash
cd dashboard
npm install
npm run build
```

2. **Deploy:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

3. **Configure backend URL:**
Update `dashboard/.env` with your Fly.io backend URL before building.

---

### Option 3: Manual Deployment

**Best for:** Custom infrastructure, learning purposes

#### Backend Manual Deployment

1. **Install dependencies:**
```bash
cd football_sim_backend

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Run the backend:**
```bash
# Development
poetry run fastapi dev app/main.py

# Production (with Gunicorn)
poetry run gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

4. **Set up as systemd service (Linux):**
```bash
sudo nano /etc/systemd/system/football-simulator.service
```

```ini
[Unit]
Description=Football Simulator Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/football_sim_backend
Environment="PATH=/path/to/.local/bin:/usr/bin"
ExecStart=/path/to/.local/bin/poetry run gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable football-simulator
sudo systemctl start football-simulator
```

#### Frontend Manual Deployment

1. **Install dependencies:**
```bash
cd dashboard
npm install
```

2. **Configure backend URL:**
```bash
# Edit .env
VITE_API_URL=https://your-backend-url.com
```

3. **Build:**
```bash
npm run build
```

4. **Deploy static files:**
```bash
# Using nginx
sudo cp -r dist/* /var/www/html/

# Or using any static file server
npx serve dist -p 3000
```

5. **Nginx configuration example:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Environment Configuration

### Backend Environment Variables

Create `football_sim_backend/.env`:

```env
# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./simulations.db

# API Configuration
CORS_ORIGINS=["http://localhost:3000", "https://your-frontend-domain.com"]

# Default RTP
DEFAULT_RTP=0.96
```

### Frontend Environment Variables

Create `dashboard/.env`:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# Optional: Analytics, etc.
# VITE_ANALYTICS_ID=your-analytics-id
```

**Important:** After changing backend URL in frontend `.env`, you must rebuild:
```bash
cd dashboard
npm run build
```

---

## Troubleshooting

### Docker Issues

**Problem:** Port already in use
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :3000

# Stop the service or change ports in docker-compose.yml
```

**Problem:** Container won't start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Backend Issues

**Problem:** Module not found errors
```bash
# Reinstall dependencies
cd football_sim_backend
poetry install

# Check Python version
python --version  # Should be 3.12+
```

**Problem:** Database locked
```bash
# SQLite is locked by another process
# Stop all instances and restart
killall python
poetry run fastapi dev app/main.py
```

### Frontend Issues

**Problem:** API calls failing
```bash
# Check backend URL in .env
cat dashboard/.env

# Verify backend is running
curl http://localhost:8000/healthz

# Check browser console for CORS errors
```

**Problem:** Build fails
```bash
# Clear node_modules and reinstall
cd dashboard
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Network Issues

**Problem:** Frontend can't connect to backend
- Ensure backend URL in frontend `.env` is correct
- Check CORS settings in `football_sim_backend/app/main.py`
- Verify firewall rules allow traffic on ports 8000 and 3000
- For Docker: ensure services are on the same network

---

## Production Checklist

Before deploying to production:

- [ ] Set secure CORS origins (remove `*`)
- [ ] Use production database (PostgreSQL recommended)
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy for database
- [ ] Set resource limits (CPU, memory)
- [ ] Enable rate limiting on API
- [ ] Set up health checks
- [ ] Configure proper error handling
- [ ] Review and set appropriate RTP values
- [ ] Test with production-like data volume

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/Sniffr/simulate/issues
- Documentation: See API_EXAMPLES_FINAL.md
- API Docs: Visit `/docs` endpoint on your backend deployment

---

## Current Deployments

**Production instances:**
- Backend: https://app-pqyimwto.fly.dev/
- Frontend: https://football-simulation-app-qlot6bn9.devinapps.com
- Session: https://app.devin.ai/sessions/8a30078891c844f78927c011562f2037
