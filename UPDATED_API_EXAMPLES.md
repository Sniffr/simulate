# Updated Football Betting Simulation API

## Changes
- **Bet Slip Support**: You can now place multiple bets at once (like a real bet slip)
- **Stake & Odds**: Each bet can optionally specify stake and odds (defaults: stake=10.0, odds=2.0)
- **Individual Results**: Each bet returns its own result with payout and profit
- **Total Summary**: Get total stake, total payout, and total profit across all bets

## API Endpoints

### 1. Set RTP (Return to Player)
```bash
curl -X POST http://localhost:8000/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.96}'
```

### 2. Get Current RTP
```bash
curl http://localhost:8000/api/rtp
```

### 3. Get Supported Markets
```bash
curl http://localhost:8000/api/markets
```

### 4a. Simulate Match with Single Bet (Default Stake & Odds)
```bash
curl -X POST http://localhost:8000/api/simulate \
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
  ],
  "volatility": "medium",
  "seed": 1
}'
```

### 4b. Simulate Match with Custom Stake & Odds
```bash
curl -X POST http://localhost:8000/api/simulate \
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
      "outcome": "1",
      "stake": 10.0,
      "odds": 2.5
    }
  ],
  "volatility": "medium",
  "seed": 1
}'
```

### 5. Simulate Match with Multiple Bets (Bet Slip)
```bash
curl -X POST http://localhost:8000/api/simulate \
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
  "volatility": "high",
  "seed": 42
}'
```

## Response Format

### Single Bet Response
```json
{
  "home_team": "Manchester",
  "away_team": "Arsenal",
  "final_score": {
    "Manchester": 1,
    "Arsenal": 0
  },
  "bet_results": [
    {
      "market": "1X2",
      "outcome": "1",
      "stake": 10.0,
      "odds": 2.5,
      "won": true,
      "outcome_occurred": true,
      "payout": 25.0,
      "profit": 15.0,
      "explanation": "✅ WON! 1X2: 1. Score: Manchester 1 - 0 Arsenal. Stake: $10.00 @ 2.50x → Payout: $25.00 (Profit: $15.00)"
    }
  ],
  "total_stake": 10.0,
  "total_payout": 25.0,
  "total_profit": 15.0,
  "events": [...],
  "match_stats": {...},
  "simulation_metadata": {
    "rtp": 0.96,
    "volatility": "medium",
    "seed": 1,
    "total_events": 15,
    "number_of_bets": 1
  }
}
```

### Multiple Bets Response
```json
{
  "home_team": "Barcelona",
  "away_team": "Real Madrid",
  "final_score": {
    "Barcelona": 3,
    "Real Madrid": 1
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
      "explanation": "✅ WON! 1X2: 1. Score: Barcelona 3 - 1 Real Madrid. Stake: $20.00 @ 2.10x → Payout: $42.00 (Profit: $22.00)"
    },
    {
      "market": "over_under",
      "outcome": "over_2.5",
      "stake": 15.0,
      "odds": 1.9,
      "won": true,
      "outcome_occurred": true,
      "payout": 28.5,
      "profit": 13.5,
      "explanation": "✅ WON! over_under: over_2.5. Score: Barcelona 3 - 1 Real Madrid. Stake: $15.00 @ 1.90x → Payout: $28.50 (Profit: $13.50)"
    },
    {
      "market": "both_teams_to_score",
      "outcome": "yes",
      "stake": 10.0,
      "odds": 1.8,
      "won": true,
      "outcome_occurred": true,
      "payout": 18.0,
      "profit": 8.0,
      "explanation": "✅ WON! both_teams_to_score: yes. Score: Barcelona 3 - 1 Real Madrid. Stake: $10.00 @ 1.80x → Payout: $18.00 (Profit: $8.00)"
    }
  ],
  "total_stake": 45.0,
  "total_payout": 88.5,
  "total_profit": 43.5,
  "events": [...],
  "match_stats": {...},
  "simulation_metadata": {
    "rtp": 0.96,
    "volatility": "high",
    "seed": 42,
    "total_events": 31,
    "number_of_bets": 3
  }
}
```

## Key Points

1. **Bet Slip**: `bet_slip` is now an array that accepts multiple bets
2. **Stake & Odds**: Each bet can optionally include:
   - `stake`: Amount wagered (default: 10.0, must be > 0)
   - `odds`: Payout multiplier if bet wins (default: 2.0, must be > 1.0)
3. **Individual Results**: Each bet gets its own result showing:
   - Whether it won or lost
   - Payout (stake × odds if won, 0 if lost)
   - Profit (payout - stake)
4. **Total Summary**:
   - `total_stake`: Sum of all stakes
   - `total_payout`: Sum of all payouts
   - `total_profit`: Total payout - total stake

## Supported Markets

- **1X2**: Home win (1), Draw (X), Away win (2)
- **over_under**: over_2.5, under_2.5
- **both_teams_to_score**: yes, no

## How RTP Works

The RTP (Return to Player) influences the simulation BEFORE the match occurs. The system:
1. Determines win/loss for each bet based on RTP percentage
2. Adjusts score probabilities to match the determined outcome
3. Simulates the match with the adjusted probabilities
4. Returns individual results for each bet plus totals
