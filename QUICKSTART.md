# Quick Start Guide

Get the Football Match Simulator up and running in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- Git installed

## Steps

### 1. Clone the Repository
```bash
git clone https://github.com/Sniffr/simulate.git
cd simulate
```

### 2. Start the Application
```bash
docker-compose up -d
```

This command will:
- Build both backend and frontend Docker images
- Start backend on port 8000
- Start frontend on port 3000
- Create a persistent volume for the database

### 3. Access the Application

**Frontend Dashboard:**
Open your browser and navigate to:
```
http://localhost:3000
```

**Backend API:**
```
http://localhost:8000
```

**API Documentation:**
```
http://localhost:8000/docs
```

### 4. Test the API

**Check health:**
```bash
curl http://localhost:8000/healthz
```

**Run a simulation:**
```bash
curl -X POST http://localhost:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Manchester United",
    "away_team": "Arsenal",
    "score_probabilities": [
      {"home_score": 1, "away_score": 0, "probability": 0.15},
      {"home_score": 2, "away_score": 0, "probability": 0.12},
      {"home_score": 2, "away_score": 1, "probability": 0.18},
      {"home_score": 1, "away_score": 1, "probability": 0.15},
      {"home_score": 0, "away_score": 1, "probability": 0.10},
      {"home_score": 0, "away_score": 0, "probability": 0.10},
      {"home_score": 3, "away_score": 1, "probability": 0.08},
      {"home_score": 1, "away_score": 2, "probability": 0.07},
      {"home_score": 3, "away_score": 2, "probability": 0.05}
    ],
    "bet_slip": [
      {
        "market": "1X2",
        "outcome": "1",
        "stake": 20.0,
        "odds": 2.1
      }
    ],
    "volatility": "medium"
  }'
```

### 5. View Logs

**All services:**
```bash
docker-compose logs -f
```

**Backend only:**
```bash
docker-compose logs -f backend
```

**Frontend only:**
```bash
docker-compose logs -f frontend
```

## Stop the Application

```bash
docker-compose down
```

To also remove the database volume:
```bash
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If port 8000 or 3000 is already in use, edit `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change left number
  frontend:
    ports:
      - "3001:8080"  # Change left number
```

### Rebuild After Code Changes

```bash
docker-compose up -d --build
```

### View Service Status

```bash
docker-compose ps
```

### Access Container Shell

**Backend:**
```bash
docker-compose exec backend /bin/sh
```

**Frontend:**
```bash
docker-compose exec frontend /bin/sh
```

## Next Steps

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment options
- Check [API_EXAMPLES_FINAL.md](API_EXAMPLES_FINAL.md) for more API examples
- Explore the dashboard at http://localhost:3000
- View API documentation at http://localhost:8000/docs

## Default Configuration

- **RTP (Return to Player):** 96%
- **Database:** SQLite (stored in Docker volume)
- **Workers:** 4 Gunicorn workers for backend
- **CORS:** Allows all origins (change for production)

## Configure Backend URL for Frontend

If you deploy backend separately, update frontend environment:

1. Copy example:
```bash
cp dashboard/.env.example dashboard/.env
```

2. Edit `dashboard/.env`:
```env
VITE_API_URL=http://your-backend-url:8000
```

3. Rebuild frontend:
```bash
cd dashboard
npm run build
```

4. Or rebuild Docker image:
```bash
docker-compose up -d --build frontend
```

## Support

- **Issues:** https://github.com/Sniffr/simulate/issues
- **Documentation:** See DEPLOYMENT.md and API_EXAMPLES_FINAL.md
