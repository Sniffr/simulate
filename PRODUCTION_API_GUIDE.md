# Football Betting Simulation API - Production Guide

**Deployed URL:** `https://app-pqyimwto.fly.dev`

## Quick Start

### 1. Set RTP (Return to Player)
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.96}'
```

### 2. Simulate a Match with Bets

**Simple bet (uses default stake=10.0, odds=2.0):**
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
  "home_team": "Manchester",
  "away_team": "Arsenal",
  "score_probabilities": [
    {"home_score": 0, "away_score": 0, "probability": 0.10},
    {"home_score": 1, "away_score": 0, "probability": 0.25},
    {"home_score": 2, "away_score": 0, "probability": 0.20},
    {"home_score": 2, "away_score": 1, "probability": 0.15},
    {"home_score": 1, "away_score": 1, "probability": 0.10},
    {"home_score": 3, "away_score": 1, "probability": 0.05},
    {"home_score": 0, "away_score": 1, "probability": 0.05},
    {"home_score": 1, "away_score": 2, "probability": 0.05},
    {"home_score": 3, "away_score": 2, "probability": 0.05}
  ],
  "bet_slip": [
    {
      "market": "1X2",
      "outcome": "1"
    }
  ]
}'
```

**Multiple bets with custom stakes and odds:**
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
  "home_team": "Barcelona",
  "away_team": "Real Madrid",
  "score_probabilities": [
    {"home_score": 0, "away_score": 0, "probability": 0.05},
    {"home_score": 1, "away_score": 0, "probability": 0.10},
    {"home_score": 2, "away_score": 1, "probability": 0.20},
    {"home_score": 1, "away_score": 1, "probability": 0.15},
    {"home_score": 3, "away_score": 1, "probability": 0.15},
    {"home_score": 2, "away_score": 2, "probability": 0.15},
    {"home_score": 3, "away_score": 2, "probability": 0.10},
    {"home_score": 4, "away_score": 2, "probability": 0.10}
  ],
  "bet_slip": [
    {
      "market": "1X2",
      "outcome": "1",
      "stake": 20.0,
      "odds": 2.1
    },
    {
      "market": "over_under",
      "outcome": "over_2.5",
      "stake": 15.0,
      "odds": 1.9
    },
    {
      "market": "both_teams_to_score",
      "outcome": "yes",
      "stake": 10.0,
      "odds": 1.8
    }
  ],
  "volatility": "high"
}'
```

## API Endpoints

### GET /healthz
Check API health status
```bash
curl https://app-pqyimwto.fly.dev/healthz
```

### GET /api/rtp
Get current RTP configuration
```bash
curl https://app-pqyimwto.fly.dev/api/rtp
```

### POST /api/rtp
Set RTP (Return to Player) percentage
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.96}'
```
- `rtp`: Float between 0.5 and 1.0 (e.g., 0.96 = 96% RTP)

### GET /api/markets
Get supported betting markets and outcomes
```bash
curl https://app-pqyimwto.fly.dev/api/markets
```

### GET /api/example
Get example request payloads
```bash
curl https://app-pqyimwto.fly.dev/api/example
```

### POST /api/simulate
Simulate a football match with betting

**Request Body:**
```json
{
  "home_team": "string",
  "away_team": "string",
  "score_probabilities": [
    {
      "home_score": 0,
      "away_score": 0,
      "probability": 0.10
    }
  ],
  "bet_slip": [
    {
      "market": "1X2",
      "outcome": "1",
      "stake": 10.0,     // optional, default: 10.0
      "odds": 2.0        // optional, default: 2.0
    }
  ],
  "volatility": "medium",  // optional: low, medium, high
  "seed": 123             // optional: for reproducibility
}
```

**Response:**
```json
{
  "home_team": "Manchester",
  "away_team": "Arsenal",
  "final_score": {
    "Manchester": 2,
    "Arsenal": 1
  },
  "bet_results": [
    {
      "market": "1X2",
      "outcome": "1",
      "stake": 20.0,
      "odds": 2.1,
      "won": true,
      "outcome_occurred": true,
      "payout": 42.0,
      "profit": 22.0,
      "explanation": "✅ WON! 1X2: 1. Score: Manchester 2 - 1 Arsenal. Stake: $20.00 @ 2.10x → Payout: $42.00 (Profit: $22.00)"
    }
  ],
  "total_stake": 20.0,
  "total_payout": 42.0,
  "total_profit": 22.0,
  "events": [...],      // play-by-play events
  "match_stats": {...}, // possession, shots, corners, fouls
  "simulation_metadata": {...}
}
```

## Supported Markets

### 1X2 (Match Result)
- `"1"`: Home win
- `"X"`: Draw
- `"2"`: Away win

### Over/Under
- `"over_2.5"`: Total goals > 2.5
- `"under_2.5"`: Total goals < 2.5

### Both Teams to Score
- `"yes"`: Both teams score
- `"no"`: One or both teams don't score

## Features

### Bet Slip Support
Place multiple bets at once, just like a real betting slip:
```json
"bet_slip": [
  {"market": "1X2", "outcome": "1", "stake": 20, "odds": 2.1},
  {"market": "over_under", "outcome": "over_2.5", "stake": 15, "odds": 1.9},
  {"market": "both_teams_to_score", "outcome": "yes"}  // uses defaults
]
```

### Optional Stake & Odds
- If not specified, defaults to: `stake=10.0`, `odds=2.0`
- Mix and match: some bets with custom values, others with defaults

### RTP (Return to Player)
- Configurable between 50% and 100%
- Influences match outcome BEFORE simulation
- Determines win/loss for each bet based on RTP percentage
- Adjusts probabilities to match predetermined outcomes

### Reproducible Results
- Use `seed` parameter for consistent results
- Same seed + same inputs = same match outcome

### Volatility Control
- `"low"`: More predictable, fewer extreme events
- `"medium"`: Balanced simulation (default)
- `"high"`: More unpredictable, exciting matches

## Example Workflow

```bash
# 1. Set RTP to 96%
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.96}'

# 2. Check supported markets
curl https://app-pqyimwto.fly.dev/api/markets

# 3. Simulate match with multiple bets
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
  "home_team": "Manchester",
  "away_team": "Arsenal",
  "score_probabilities": [
    {"home_score": 1, "away_score": 0, "probability": 0.3},
    {"home_score": 2, "away_score": 1, "probability": 0.25},
    {"home_score": 1, "away_score": 1, "probability": 0.2},
    {"home_score": 0, "away_score": 0, "probability": 0.15},
    {"home_score": 0, "away_score": 1, "probability": 0.1}
  ],
  "bet_slip": [
    {"market": "1X2", "outcome": "1", "stake": 50, "odds": 2.2},
    {"market": "over_under", "outcome": "over_2.5"}
  ]
}'
```

## Notes

- Score probabilities must sum to 1.0 (±0.01 tolerance)
- Stake must be > 0
- Odds must be > 1.0
- RTP must be between 0.5 and 1.0
- Seed is optional but recommended for testing/debugging

## Error Handling

**422 Validation Error:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "bet_slip"],
      "msg": "Field required"
    }
  ]
}
```

**400 Bad Request:**
```json
{
  "detail": "Score probabilities must sum to 1.0 (currently 0.95)"
}
```

## Support

For issues or questions, refer to the documentation or contact the development team.
