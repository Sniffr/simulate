# Football Match Betting Simulation API

A probabilistic football match simulator with betting mechanics based on RTP (Return to Player) principles. This system simulates football matches and evaluates bets with configurable house edge.

## Features

- **Probabilistic Match Simulation**: Generates realistic play-by-play match events based on provided score probabilities
- **RTP Configuration**: Adjustable Return to Player percentage (50-100%) to control house edge
- **Betting Markets**: Support for 1X2, Over/Under, and Both Teams to Score
- **Bet Slip Functionality**: Place multiple bets at once (like a real betting slip)
- **Optional Stakes & Odds**: Flexible betting with or without monetary stakes
- **Reproducible Simulations**: Seed-based RNG for consistent results
- **Match Statistics**: Detailed stats including possession, shots, corners, and fouls
- **Beautiful Dashboard**: Real-time RTP tracking and simulation visualization

## Live URLs

**Dashboard**: https://football-simulation-app-qlot6bn9.devinapps.com

**API Backend**: https://app-pqyimwto.fly.dev

## Dashboard Features

The dashboard provides a stunning visual interface to interact with the simulation system:

- **Real-time RTP Tracking**: Compare configured RTP vs actual RTP across all simulations
- **Live Statistics**: Total bets, win/loss ratio, house profit
- **Interactive Controls**: One-click RTP adjustment (96%, 92%, 88%)
- **Simulation History**: View up to 20 recent simulations with full bet details
- **Beautiful UI**: Gradient design with dark theme and smooth animations
- **Bet Visualization**: Color-coded bet results with detailed payout information
- **Match Details**: Score, events, metadata for each simulation

## Quick Start

### 1. Set RTP (Return to Player)
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.96}'
```

### 2. Simulate a Match
```bash
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
    {
      "market": "1X2",
      "outcome": "1",
      "stake": 20.0,
      "odds": 2.1
    },
    {
      "market": "over_under",
      "outcome": "over_2.5"
    }
  ]
}'
```

## API Endpoints

- `GET /healthz` - Health check
- `GET /api/rtp` - Get current RTP configuration
- `POST /api/rtp` - Set RTP percentage
- `GET /api/markets` - Get supported betting markets
- `POST /api/simulate` - Simulate a match with bets
- `GET /api/example` - Get example request payloads

## How RTP Works

RTP (Return to Player) determines the house edge:

- **96% RTP** = Players get back 96% of stakes over time, house keeps 4%
- The system adjusts match probabilities **before** simulation to ensure the house edge
- Each bet's win probability is reduced by (100% - RTP)
- Over many bets, the house maintains its edge probabilistically

## Betting Markets

### 1X2 (Match Result)
- `"1"` - Home win
- `"X"` - Draw
- `"2"` - Away win

### Over/Under Goals
- `"over_2.5"` - Total goals > 2.5
- `"under_2.5"` - Total goals < 2.5

### Both Teams to Score
- `"yes"` - Both teams score
- `"no"` - One or both teams don't score

## Bet Slip Logic

The bet slip works like an accumulator/parlay:
- **All bets must win** for `bet_slip_won: true`
- **If any bet loses**, `bet_slip_won: false`
- Stakes and odds are optional per bet
- Totals only calculated when stakes are provided

## Response Example

```json
{
  "final_score": {"Manchester": 2, "Arsenal": 1},
  "bet_slip_won": true,
  "bet_results": [
    {
      "market": "1X2",
      "outcome": "1",
      "won": true,
      "stake": 20.0,
      "odds": 2.1,
      "payout": 42.0,
      "profit": 22.0,
      "explanation": "✅ WON! 1X2: 1. Score: Manchester 2 - 1 Arsenal. Stake: $20.00 @ 2.10x → Payout: $42.00 (Profit: $22.00)"
    },
    {
      "market": "over_under",
      "outcome": "over_2.5",
      "won": true,
      "stake": null,
      "odds": null,
      "payout": null,
      "profit": null,
      "explanation": "✅ WON! over_under: over_2.5. Score: Manchester 2 - 1 Arsenal."
    }
  ],
  "total_stake": 20.0,
  "total_payout": 42.0,
  "total_profit": 22.0,
  "events": [...],
  "match_stats": {...}
}
```

## Local Development

### Requirements
- Python 3.12+
- Poetry

### Setup
```bash
cd football_sim_backend
poetry install
poetry run uvicorn app.main:app --reload
```

### Run Tests
```bash
poetry run pytest
```

## Documentation

- [Production API Guide](PRODUCTION_API_GUIDE.md) - Complete API documentation
- [Updated API Examples](UPDATED_API_EXAMPLES.md) - Request/response examples
- [Reference Document](Simulated+Gambling_+Logic+and+Math.rtf) - Original gambling mathematics reference

## Tech Stack

### Backend
- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Poetry** - Dependency management
- **Fly.io** - Deployment platform

### Frontend (Dashboard)
- **React** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Lucide Icons** - Icon system

## License

MIT

## Author

Built by Devin for @Sniffr
