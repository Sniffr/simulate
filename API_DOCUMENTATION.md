# Football Match Simulator - Complete API Documentation

## Table of Contents
- [Overview](#overview)
- [Base URLs](#base-urls)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [RTP Configuration](#rtp-configuration)
  - [Betting Markets](#betting-markets)
  - [Match Simulation](#match-simulation)
  - [Simulation History](#simulation-history)
  - [Statistics](#statistics)
  - [Player Management](#player-management)
- [Data Models](#data-models)
- [Complete Examples](#complete-examples)
- [Error Handling](#error-handling)

---

## Overview

The Football Match Simulator API provides probabilistic football match simulation with betting mechanics based on RTP (Return to Player) principles. Each simulation is tracked per player, allowing independent RTP calculation for each user.

**Key Features:**
- Per-player RTP tracking
- Multiple betting markets (1X2, Over/Under, BTTS, Correct Score)
- Bet slip functionality (multiple bets per simulation)
- Overround/underround probability support
- Reproducible simulations via seeds
- Comprehensive statistics and trends

---

## Base URLs

**Production:**
- Backend API: `https://app-pqyimwto.fly.dev`
- Dashboard: `https://football-simulation-app-qlot6bn9.devinapps.com`

**Local Development:**
- Backend API: `http://localhost:8000`
- Dashboard: `http://localhost:3000`

**API Documentation:**
- Swagger UI: `https://app-pqyimwto.fly.dev/docs`
- ReDoc: `https://app-pqyimwto.fly.dev/redoc`

---

## Authentication

Currently, no authentication is required. All endpoints are publicly accessible.

---

## API Endpoints

### Health Check

**`GET /healthz`**

Check if the API is running.

**Response:**
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl https://app-pqyimwto.fly.dev/healthz
```

---

### RTP Configuration

#### Get Current RTP

**`GET /api/rtp`**

Retrieve the currently configured RTP percentage.

**Response:**
```json
{
  "rtp": 0.96
}
```

**Example:**
```bash
curl https://app-pqyimwto.fly.dev/api/rtp
```

#### Set RTP

**`POST /api/rtp`**

Configure the RTP percentage for future simulations.

**Request Body:**
```json
{
  "rtp": 0.96
}
```

**Parameters:**
- `rtp` (float, required): RTP percentage between 0.0 and 1.0 (e.g., 0.96 = 96%)

**Response:**
```json
{
  "rtp": 0.96
}
```

**Examples:**
```bash
# Set RTP to 96%
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.96}'

# Set RTP to 92%
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.92}'

# Set RTP to 88%
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.88}'
```

---

### Betting Markets

**`GET /api/markets`**

Get all supported betting markets with descriptions and examples.

**Response:**
```json
{
  "markets": [
    {
      "market_type": "1X2",
      "name": "Match Result (1X2)",
      "description": "Predict the final result: Home win (1), Draw (X), or Away win (2)",
      "possible_outcomes": ["1", "X", "2", "home", "draw", "away"],
      "example": "1"
    },
    {
      "market_type": "over_under",
      "name": "Over/Under Goals",
      "description": "Predict if total goals will be over or under a threshold",
      "possible_outcomes": ["over_0.5", "under_0.5", "over_1.5", "under_1.5", "over_2.5", "under_2.5", "over_3.5", "under_3.5"],
      "example": "over_2.5"
    },
    {
      "market_type": "both_teams_to_score",
      "name": "Both Teams To Score",
      "description": "Predict if both teams will score at least one goal",
      "possible_outcomes": ["yes", "no"],
      "example": "yes"
    },
    {
      "market_type": "correct_score",
      "name": "Correct Score",
      "description": "Predict the exact final score",
      "possible_outcomes": ["0-0", "1-0", "2-0", "1-1", "2-1", "3-1", "0-1", "1-2", "2-2", "3-2", "etc."],
      "example": "2-1"
    }
  ],
  "description": "Supported betting markets for football match simulation"
}
```

**Example:**
```bash
curl https://app-pqyimwto.fly.dev/api/markets
```

---

### Match Simulation

**`POST /api/simulate`**

Simulate a football match with betting outcomes.

**Request Body:**
```json
{
  "user_id": "player123",
  "home_team": "Manchester United",
  "away_team": "Arsenal",
  "score_probabilities": [
    {"home_score": 1, "away_score": 0, "probability": 0.15},
    {"home_score": 2, "away_score": 1, "probability": 0.18},
    {"home_score": 1, "away_score": 1, "probability": 0.15},
    {"home_score": 0, "away_score": 0, "probability": 0.10},
    {"home_score": 0, "away_score": 1, "probability": 0.10},
    {"home_score": 2, "away_score": 0, "probability": 0.12},
    {"home_score": 3, "away_score": 1, "probability": 0.10},
    {"home_score": 1, "away_score": 2, "probability": 0.07},
    {"home_score": 3, "away_score": 2, "probability": 0.03}
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
    }
  ],
  "volatility": "medium",
  "seed": 12345
}
```

**Parameters:**
- `user_id` (string, required): Unique identifier for the player
- `home_team` (string, required): Home team name
- `away_team` (string, required): Away team name
- `score_probabilities` (array, required): List of possible scores with probabilities
  - Note: Probabilities can sum to more or less than 1.0 (overround/underround)
- `bet_slip` (array, required): List of bets to place
  - `market` (string, required): Betting market type
  - `outcome` (string, required): Specific outcome to bet on
  - `stake` (float, optional): Amount wagered
  - `odds` (float, optional): Payout multiplier
- `volatility` (string, optional): "low", "medium", or "high" (default: "medium")
- `seed` (integer, optional): Random seed for reproducible results

**Response:**
```json
{
  "home_team": "Manchester United",
  "away_team": "Arsenal",
  "final_score": {
    "Manchester United": 2,
    "Arsenal": 1
  },
  "bet_slip_won": true,
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
      "explanation": "✅ WON! 1X2: 1. Score: Manchester United 2 - 1 Arsenal. Stake: $20.00 @ 2.10x → Payout: $42.00 (Profit: $22.00)"
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
      "explanation": "✅ WON! over_under: over_2.5. Score: Manchester United 2 - 1 Arsenal. Stake: $15.00 @ 1.90x → Payout: $28.50 (Profit: $13.50)"
    }
  ],
  "total_stake": 35.0,
  "total_payout": 70.5,
  "total_profit": 35.5,
  "events": [
    {
      "minute": 0,
      "event_type": "kickoff",
      "team": "Manchester United",
      "description": "Match kicks off at the stadium! Manchester United vs Arsenal",
      "player": null
    },
    {
      "minute": 12,
      "event_type": "goal",
      "team": "Manchester United",
      "description": "⚽ GOAL! M. Player 7 scores for Manchester United! Manchester United 1 - 0 Arsenal",
      "player": "M. Player 7"
    }
  ],
  "match_stats": {
    "possession": {
      "Manchester United": 58.5,
      "Arsenal": 41.5
    },
    "shots": {
      "Manchester United": 12,
      "Arsenal": 8
    },
    "corners": {
      "Manchester United": 6,
      "Arsenal": 3
    },
    "fouls": {
      "Manchester United": 9,
      "Arsenal": 11
    },
    "total_goals": 3
  },
  "simulation_metadata": {
    "rtp": 0.96,
    "volatility": "medium",
    "seed": 12345,
    "total_events": 45,
    "number_of_bets": 2
  }
}
```

---

### Simulation History

**`GET /api/history`**

Retrieve historical simulations with filtering and pagination.

**Query Parameters:**
- `limit` (integer, optional): Number of results (1-200, default: 50)
- `offset` (integer, optional): Offset for pagination (default: 0)
- `team` (string, optional): Filter by team name
- `won` (boolean, optional): Filter by bet slip won/lost
- `user_id` (string, optional): Filter by player ID

**Examples:**
```bash
# Get last 20 simulations
curl "https://app-pqyimwto.fly.dev/api/history?limit=20"

# Get simulations for specific player
curl "https://app-pqyimwto.fly.dev/api/history?user_id=player123"

# Get won simulations for a team
curl "https://app-pqyimwto.fly.dev/api/history?team=Manchester&won=true"

# Pagination example
curl "https://app-pqyimwto.fly.dev/api/history?limit=10&offset=20"
```

**Response:**
```json
{
  "simulations": [
    {
      "id": 1,
      "user_id": "player123",
      "home_team": "Manchester United",
      "away_team": "Arsenal",
      "home_score": 2,
      "away_score": 1,
      "bet_slip_won": true,
      "total_stake": 35.0,
      "total_payout": 70.5,
      "total_profit": 35.5,
      "configured_rtp": 0.96,
      "timestamp": "2025-10-15T10:30:00Z"
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 150,
    "has_more": true
  }
}
```

---

### Statistics

#### Overall Statistics

**`GET /api/stats`**

Get overall simulation statistics including RTP analysis.

**Response:**
```json
{
  "total_simulations": 500,
  "total_with_stakes": 450,
  "total_won": 210,
  "total_lost": 240,
  "win_rate": 46.67,
  "total_staked": 25000.0,
  "total_paid_out": 23500.0,
  "actual_rtp": 94.0,
  "house_profit": 1500.0,
  "average_stake": 55.56,
  "configured_rtp": 0.96
}
```

**Example:**
```bash
curl https://app-pqyimwto.fly.dev/api/stats
```

#### RTP Trends

**`GET /api/rtp-trends`**

Get RTP trends over time with cumulative and rolling window calculations.

**Query Parameters:**
- `limit` (integer, optional): Number of recent simulations to analyze (10-500, default: 100)

**Example:**
```bash
curl "https://app-pqyimwto.fly.dev/api/rtp-trends?limit=50"
```

**Response:**
```json
{
  "trends": [
    {
      "simulation_id": 450,
      "timestamp": "2025-10-15T10:30:00Z",
      "configured_rtp": 0.96,
      "cumulative_actual_rtp": 94.5,
      "rolling_window_rtp": 95.2
    }
  ],
  "description": "RTP trends showing configured vs actual RTP over time"
}
```

---

### Player Management

#### Get All Players

**`GET /api/players`**

Get list of all players with their statistics.

**Response:**
```json
{
  "players": [
    {
      "user_id": "player123",
      "total_simulations": 50,
      "won_slips": 22,
      "total_staked": 1000.0,
      "actual_rtp": 92.5
    },
    {
      "user_id": "player456",
      "total_simulations": 30,
      "won_slips": 15,
      "total_staked": 750.0,
      "actual_rtp": 95.3
    }
  ],
  "description": "All players who have placed bets with their stats"
}
```

**Example:**
```bash
curl https://app-pqyimwto.fly.dev/api/players
```

#### Get Player Statistics

**`GET /api/players/{user_id}/stats`**

Get detailed statistics for a specific player.

**Path Parameters:**
- `user_id` (string, required): Player identifier

**Response:**
```json
{
  "user_id": "player123",
  "total_simulations": 50,
  "won_slips": 22,
  "lost_slips": 28,
  "win_rate": 44.0,
  "total_staked": 1000.0,
  "total_paid_out": 925.0,
  "actual_rtp": 92.5,
  "total_profit": -75.0
}
```

**Example:**
```bash
curl https://app-pqyimwto.fly.dev/api/players/player123/stats
```

---

## Data Models

### ScoreProbability
```json
{
  "home_score": 2,
  "away_score": 1,
  "probability": 0.18
}
```

### BetSelection
```json
{
  "market": "1X2",
  "outcome": "1",
  "stake": 20.0,
  "odds": 2.1
}
```

### Market Types
- `1X2` - Match result (1=Home, X=Draw, 2=Away)
- `over_under` - Total goals over/under threshold
- `both_teams_to_score` - Both teams score (yes/no)
- `correct_score` - Exact final score

---

## Complete Examples

### Example 1: Single Bet with Stake

```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "player123",
    "home_team": "Manchester United",
    "away_team": "Arsenal",
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
    "bet_slip": [
      {
        "market": "1X2",
        "outcome": "1",
        "stake": 10.0,
        "odds": 2.5
      }
    ],
    "volatility": "medium"
  }'
```

### Example 2: Multiple Bets (Accumulator)

```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "player456",
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

### Example 3: Bets Without Stakes

```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "player789",
    "home_team": "Liverpool",
    "away_team": "Chelsea",
    "score_probabilities": [
      {"home_score": 1, "away_score": 0, "probability": 0.20},
      {"home_score": 2, "away_score": 1, "probability": 0.25},
      {"home_score": 1, "away_score": 1, "probability": 0.20},
      {"home_score": 0, "away_score": 0, "probability": 0.10},
      {"home_score": 0, "away_score": 1, "probability": 0.15},
      {"home_score": 2, "away_score": 0, "probability": 0.10}
    ],
    "bet_slip": [
      {
        "market": "1X2",
        "outcome": "1"
      },
      {
        "market": "over_under",
        "outcome": "over_1.5"
      }
    ],
    "volatility": "low"
  }'
```

### Example 4: Correct Score Bet

```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "player999",
    "home_team": "Bayern Munich",
    "away_team": "Dortmund",
    "score_probabilities": [
      {"home_score": 2, "away_score": 1, "probability": 0.22},
      {"home_score": 3, "away_score": 1, "probability": 0.18},
      {"home_score": 1, "away_score": 0, "probability": 0.15},
      {"home_score": 2, "away_score": 0, "probability": 0.12},
      {"home_score": 1, "away_score": 1, "probability": 0.13},
      {"home_score": 3, "away_score": 2, "probability": 0.10},
      {"home_score": 0, "away_score": 0, "probability": 0.05},
      {"home_score": 0, "away_score": 1, "probability": 0.05}
    ],
    "bet_slip": [
      {
        "market": "correct_score",
        "outcome": "2-1",
        "stake": 50.0,
        "odds": 8.5
      }
    ]
  }'
```

### Example 5: Overround Probabilities

```bash
# Probabilities sum to 1.15 (overround - typical in betting)
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "player321",
    "home_team": "PSG",
    "away_team": "Monaco",
    "score_probabilities": [
      {"home_score": 1, "away_score": 0, "probability": 0.18},
      {"home_score": 2, "away_score": 0, "probability": 0.20},
      {"home_score": 2, "away_score": 1, "probability": 0.22},
      {"home_score": 3, "away_score": 1, "probability": 0.15},
      {"home_score": 1, "away_score": 1, "probability": 0.15},
      {"home_score": 0, "away_score": 0, "probability": 0.10},
      {"home_score": 0, "away_score": 1, "probability": 0.08},
      {"home_score": 1, "away_score": 2, "probability": 0.07}
    ],
    "bet_slip": [
      {
        "market": "1X2",
        "outcome": "1",
        "stake": 25.0,
        "odds": 1.85
      }
    ]
  }'
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

**400 Bad Request**
- Invalid request body
- Score probabilities sum to 0 or negative
- Invalid market type or outcome
- Invalid RTP value (must be 0.0-1.0)

**404 Not Found**
- Player not found
- No simulations found for filter criteria

**422 Unprocessable Entity**
- Missing required fields
- Invalid field types
- Validation errors

**500 Internal Server Error**
- Unexpected server error

### Example Error Responses

**Invalid RTP:**
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "rtp"],
      "msg": "Input should be less than or equal to 1.0"
    }
  ]
}
```

**Player Not Found:**
```json
{
  "detail": "No simulations found for player unknown_player"
}
```

---

## Rate Limits

Currently, no rate limits are enforced. For production use, consider implementing rate limiting on the client side.

---

## Changelog

### Version 2.0.0 (Current)
- Added per-player RTP tracking
- Added player statistics endpoints
- Added simulation history filtering
- Added overround/underround support
- Added dashboard with auto-refresh

### Version 1.0.0
- Initial release
- Basic simulation functionality
- RTP configuration
- Betting markets support

---

## Support

- **API Documentation:** https://app-pqyimwto.fly.dev/docs
- **GitHub Repository:** https://github.com/Sniffr/simulate
- **Dashboard:** https://football-simulation-app-qlot6bn9.devinapps.com

---

## License

MIT License - See repository for details
