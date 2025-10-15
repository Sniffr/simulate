# Football Match Simulator API - Version 2.0

## Deployed API URL
**Base URL:** `https://app-pqyimwto.fly.dev`
**Interactive Docs:** `https://app-pqyimwto.fly.dev/docs`

---

## Overview

This API simulates football matches with betting outcomes based on **RTP (Return to Player)** principles from gambling mathematics. The RTP determines the house edge and win/loss probability over time, just like slot machines and casino games.

**Key Features:**
- ✅ Configurable RTP (Return to Player) percentage
- ✅ Multiple betting markets (1X2, Over/Under, Both Teams to Score, Correct Score)
- ✅ RNG-based outcome determination
- ✅ Play-by-play match simulation
- ✅ Win/Loss determination based on RTP and probability

---

## API Endpoints

### 1. Get Current RTP
```bash
curl https://app-pqyimwto.fly.dev/api/rtp
```

**Response:**
```json
{"rtp": 0.96}
```

### 2. Set RTP (Configure House Edge)
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.85}'
```

**Response:**
```json
{"rtp": 0.85}
```

**RTP Explained:**
- `1.0` (100%) = No house edge, pure probability
- `0.96` (96%) = 4% house edge (typical for slots)
- `0.85` (85%) = 15% house edge (higher profit margin)
- Lower RTP = Harder to win even if outcome occurs

### 3. Get Supported Markets
```bash
curl https://app-pqyimwto.fly.dev/api/markets
```

**Response includes:**
- **1X2** - Home win (1), Draw (X), Away win (2)
- **Over/Under** - Total goals over/under threshold (0.5, 1.5, 2.5, 3.5)
- **Both Teams To Score** - Yes or No
- **Correct Score** - Exact final score prediction

### 4. Simulate Match with Betting

```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Manchester United",
    "away_team": "Girona",
    "score_probabilities": [
      {"home_score": 0, "away_score": 0, "probability": 0.10},
      {"home_score": 1, "away_score": 0, "probability": 0.15},
      {"home_score": 2, "away_score": 0, "probability": 0.12},
      {"home_score": 2, "away_score": 1, "probability": 0.18},
      {"home_score": 1, "away_score": 1, "probability": 0.15},
      {"home_score": 3, "away_score": 1, "probability": 0.10},
      {"home_score": 0, "away_score": 1, "probability": 0.08},
      {"home_score": 1, "away_score": 2, "probability": 0.07},
      {"home_score": 3, "away_score": 2, "probability": 0.05}
    ],
    "bet_selection": {
      "market": "1X2",
      "outcome": "1"
    },
    "volatility": "medium"
  }'
```

---

## Complete Examples

### Example 1: Betting on Home Win (1X2)

**Step 1: Set RTP to 90%**
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.90}'
```

**Step 2: Simulate match betting on Manchester United to win**
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Manchester United",
    "away_team": "Girona",
    "score_probabilities": [
      {"home_score": 0, "away_score": 0, "probability": 0.10},
      {"home_score": 1, "away_score": 0, "probability": 0.15},
      {"home_score": 2, "away_score": 0, "probability": 0.12},
      {"home_score": 2, "away_score": 1, "probability": 0.18},
      {"home_score": 1, "away_score": 1, "probability": 0.15},
      {"home_score": 3, "away_score": 1, "probability": 0.10},
      {"home_score": 0, "away_score": 1, "probability": 0.08},
      {"home_score": 1, "away_score": 2, "probability": 0.07},
      {"home_score": 3, "away_score": 2, "probability": 0.05}
    ],
    "bet_selection": {
      "market": "1X2",
      "outcome": "1"
    },
    "volatility": "medium"
  }'
```

**Sample Response:**
```json
{
  "home_team": "Manchester United",
  "away_team": "Girona",
  "final_score": {
    "Manchester United": 2,
    "Girona": 1
  },
  "bet_result": {
    "won": true,
    "outcome_occurred": true,
    "payout_multiplier": 2.0,
    "explanation": "Bet WON! You bet on 1X2: 1. Final score: Manchester United 2 - 1 Girona. The outcome occurred and RTP (90%) favored a win. Payout at 2.00x odds."
  },
  "events": [...],
  "match_stats": {...}
}
```

### Example 2: Over/Under 2.5 Goals

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
    "bet_selection": {
      "market": "over_under",
      "outcome": "over_2.5"
    },
    "volatility": "high"
  }'
```

**Sample Response:**
```json
{
  "final_score": {
    "Barcelona": 3,
    "Real Madrid": 1
  },
  "bet_result": {
    "won": true,
    "outcome_occurred": true,
    "payout_multiplier": 1.9,
    "explanation": "Bet WON! You bet on over_under: over_2.5. Final score: Barcelona 3 - 1 Real Madrid. The outcome occurred and RTP (90%) favored a win. Payout at 1.90x odds."
  }
}
```

### Example 3: Both Teams To Score

```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Liverpool",
    "away_team": "Arsenal",
    "score_probabilities": [
      {"home_score": 0, "away_score": 0, "probability": 0.15},
      {"home_score": 1, "away_score": 0, "probability": 0.20},
      {"home_score": 2, "away_score": 1, "probability": 0.25},
      {"home_score": 1, "away_score": 1, "probability": 0.20},
      {"home_score": 0, "away_score": 1, "probability": 0.10},
      {"home_score": 2, "away_score": 2, "probability": 0.10}
    ],
    "bet_selection": {
      "market": "both_teams_to_score",
      "outcome": "yes"
    },
    "volatility": "medium"
  }'
```

### Example 4: Correct Score Prediction

```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Chelsea",
    "away_team": "Tottenham",
    "score_probabilities": [
      {"home_score": 0, "away_score": 0, "probability": 0.10},
      {"home_score": 1, "away_score": 0, "probability": 0.15},
      {"home_score": 2, "away_score": 1, "probability": 0.30},
      {"home_score": 1, "away_score": 1, "probability": 0.20},
      {"home_score": 2, "away_score": 2, "probability": 0.15},
      {"home_score": 3, "away_score": 1, "probability": 0.10}
    ],
    "bet_selection": {
      "market": "correct_score",
      "outcome": "2-1"
    },
    "volatility": "low"
  }'
```

---

## Understanding the Betting Logic

### How RTP Works

The system uses a **two-step process** to determine if you win:

1. **Match Simulation**: Based on score probabilities, the match is simulated and a final score is determined
2. **Bet Evaluation**: 
   - First, check if your predicted outcome occurred
   - If YES, use RTP and odds to determine if you WIN or LOSE
   - If NO, you automatically LOSE

**Example:**
- You bet on "Home Win" with RTP = 0.90
- Match ends 2-1 (Home Win) ✓ Outcome occurred
- True odds = 2.0x, so fair probability = 50%
- Adjusted probability = 50% × 0.90 = 45%
- RNG generates a number; if < 45%, you WIN at 2.0x payout
- Otherwise, you LOSE despite the outcome occurring

**This mimics real gambling:** Even when your prediction is correct, the house edge (RTP) can still cause you to lose!

### Market Types and Outcomes

| Market | Possible Outcomes | Example |
|--------|------------------|---------|
| **1X2** | `1`, `X`, `2`, `home`, `draw`, `away` | `"1"` for home win |
| **Over/Under** | `over_0.5`, `under_0.5`, `over_1.5`, `under_1.5`, `over_2.5`, `under_2.5`, `over_3.5`, `under_3.5` | `"over_2.5"` |
| **Both Teams Score** | `yes`, `no` | `"yes"` |
| **Correct Score** | `"0-0"`, `"1-0"`, `"2-1"`, `"3-2"`, etc. | `"2-1"` |

---

## Response Format

All simulation responses include:

```json
{
  "home_team": "Team A",
  "away_team": "Team B",
  "final_score": {
    "Team A": 2,
    "Team B": 1
  },
  "bet_result": {
    "won": true/false,
    "outcome_occurred": true/false,
    "payout_multiplier": 2.0,
    "explanation": "Detailed explanation of win/loss"
  },
  "events": [
    {
      "minute": 23,
      "event_type": "goal",
      "team": "Team A",
      "description": "⚽ GOAL! Player scores...",
      "player": "A. Player 1"
    }
  ],
  "match_stats": {
    "possession": {...},
    "shots": {...},
    "corners": {...}
  },
  "simulation_metadata": {
    "rtp": 0.96,
    "volatility": "medium",
    "seed": 123456,
    "bet_market": "1X2",
    "bet_outcome": "1"
  }
}
```

---

## Parameters

### Required:
- `home_team` - Home team name
- `away_team` - Away team name  
- `score_probabilities` - Array of possible scores with probabilities (must sum to 1.0)
- `bet_selection` - Your bet choice
  - `market` - Type of bet (1X2, over_under, etc.)
  - `outcome` - Specific outcome you're betting on

### Optional:
- `volatility` - `"low"`, `"medium"`, `"high"` (default: `"medium"`)
- `seed` - Integer for reproducible results (default: random)

---

## Tips for Usage

1. **Always set RTP first** using `POST /api/rtp` before running simulations
2. **Check available markets** with `GET /api/markets` to see all options
3. **Score probabilities must sum to 1.0** or you'll get an error
4. **Lower RTP = harder to win**, even when outcomes occur
5. **Use seed parameter** to reproduce the same match multiple times

---

## Example Workflow

```bash
# 1. Set RTP to 85% (15% house edge)
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.85}'

# 2. Get available markets
curl https://app-pqyimwto.fly.dev/api/markets

# 3. Simulate a match with a bet
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d @your_request.json

# 4. Check if you won or lost in the response!
```

---

**Built with RNG principles from gambling mathematics** ⚽🎰
