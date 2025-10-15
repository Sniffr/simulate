# Football Match Simulator API - Example Requests

## Deployed API URL
**Base URL:** `https://app-pqyimwto.fly.dev`

## API Endpoints

### 1. Health Check
```bash
curl https://app-pqyimwto.fly.dev/healthz
```

### 2. Get Example Request Format
```bash
curl https://app-pqyimwto.fly.dev/api/example
```

### 3. Simulate a Football Match

## Basic Example: Manchester United vs Girona
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Manchester United",
    "away_team": "Girona",
    "score_probabilities": [
      {"home_score": 0, "away_score": 0, "probability": 0.1},
      {"home_score": 1, "away_score": 0, "probability": 0.15},
      {"home_score": 2, "away_score": 0, "probability": 0.12},
      {"home_score": 2, "away_score": 1, "probability": 0.18},
      {"home_score": 1, "away_score": 1, "probability": 0.15},
      {"home_score": 3, "away_score": 1, "probability": 0.1},
      {"home_score": 0, "away_score": 1, "probability": 0.08},
      {"home_score": 1, "away_score": 2, "probability": 0.07},
      {"home_score": 3, "away_score": 2, "probability": 0.05}
    ],
    "rtp": 0.96,
    "volatility": "medium"
  }'
```

## High Volatility Example: Barcelona vs Real Madrid
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Barcelona",
    "away_team": "Real Madrid",
    "score_probabilities": [
      {"home_score": 0, "away_score": 0, "probability": 0.05},
      {"home_score": 1, "away_score": 0, "probability": 0.10},
      {"home_score": 2, "away_score": 0, "probability": 0.08},
      {"home_score": 2, "away_score": 1, "probability": 0.15},
      {"home_score": 1, "away_score": 1, "probability": 0.12},
      {"home_score": 3, "away_score": 1, "probability": 0.12},
      {"home_score": 0, "away_score": 1, "probability": 0.08},
      {"home_score": 1, "away_score": 2, "probability": 0.10},
      {"home_score": 3, "away_score": 2, "probability": 0.10},
      {"home_score": 4, "away_score": 2, "probability": 0.10}
    ],
    "rtp": 0.95,
    "volatility": "high",
    "seed": 12345
  }'
```

## Low Volatility Example with Reproducible Results
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Liverpool",
    "away_team": "Arsenal",
    "score_probabilities": [
      {"home_score": 0, "away_score": 0, "probability": 0.20},
      {"home_score": 1, "away_score": 0, "probability": 0.25},
      {"home_score": 1, "away_score": 1, "probability": 0.25},
      {"home_score": 0, "away_score": 1, "probability": 0.20},
      {"home_score": 2, "away_score": 1, "probability": 0.10}
    ],
    "rtp": 0.98,
    "volatility": "low",
    "seed": 99999
  }'
```

## Parameters Explained

### Required Parameters:
- **home_team** (string): Name of the home team
- **away_team** (string): Name of the away team
- **score_probabilities** (array): List of possible scores with their probabilities
  - Must sum to exactly 1.0 (or very close)
  - Each entry has: home_score, away_score, probability

### Optional Parameters:
- **rtp** (float, default: 0.96): Return to Player percentage (0.0 to 1.0)
  - Based on gambling RNG principles from the document
  - Higher RTP = more predictable outcomes
  
- **volatility** (string, default: "medium"): Game volatility
  - "low": More predictable, frequent low-scoring games
  - "medium": Balanced distribution
  - "high": Favors high-scoring, dramatic matches
  
- **seed** (integer, optional): Seed for reproducible results
  - Same seed + same parameters = same match outcome
  - Omit for random results every time

## Response Format

The API returns:
- **final_score**: The match result (e.g., Manchester United 2 - 1 Girona)
- **events**: Play-by-play timeline with:
  - Goals, shots, passes, fouls, corners, offsides, etc.
  - Minute-by-minute action
  - Player names
- **match_stats**: Possession, shots, corners, fouls statistics
- **simulation_metadata**: RTP, volatility, seed used, total events

## Pretty Print JSON (Optional)
Add `| python3 -m json.tool` or `| jq` to the end of any curl command to format the output nicely.
