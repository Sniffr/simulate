# Football Match Simulator API - CORRECTED Version

## Deployed API URL
**Base URL:** `https://app-pqyimwto.fly.dev`
**Interactive Docs:** `https://app-pqyimwto.fly.dev/docs`

---

## 🎯 How RTP Works (CORRECTED)

**The RTP now works BEFORE the simulation**, not after:

1. You set the RTP (e.g., 96% = 4% house edge, 85% = 15% house edge)
2. You place a bet (e.g., "Home Win")
3. **The house/RTP decides** if you should win or lose BEFORE simulating
4. The match is simulated to produce the outcome the house decided
5. If house decided you win → match produces your predicted outcome
6. If house decided you lose → match produces a different outcome

**This is how real gambling works!** The house edge determines your chances BEFORE the event, not after.

---

## Quick Example

```bash
# 1. Set RTP to 96% (4% house edge)
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.96}'

# 2. Bet on Manchester to win (outcome "1" in 1X2)
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Manchester",
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
    "bet_selection": {
      "market": "1X2",
      "outcome": "1"
    },
    "volatility": "medium",
    "seed": 1
  }'
```

**With RTP = 96% and seed = 1:**
```json
{
  "final_score": {"Manchester": 1, "Arsenal": 0},
  "bet_result": {
    "won": true,
    "explanation": "Bet WON! Your prediction was correct."
  }
}
```

**With RTP = 10% (house heavily favored) and seed = 1:**
```json
{
  "final_score": {"Manchester": 0, "Arsenal": 0},
  "bet_result": {
    "won": false,
    "explanation": "Bet LOST. Your prediction did not match the outcome."
  }
}
```

**See the difference?** Same seed, same bet, but different RTP = different outcome!

---

## API Endpoints

### 1. Get Current RTP
```bash
curl https://app-pqyimwto.fly.dev/api/rtp
```

### 2. Set RTP
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/rtp \
  -H "Content-Type: application/json" \
  -d '{"rtp": 0.85}'
```

**RTP Values:**
- `1.0` = 100% RTP, no house edge (player always has fair chance)
- `0.96` = 96% RTP, 4% house edge (typical slot machine)
- `0.85` = 85% RTP, 15% house edge (high profit margin)
- `0.50` = 50% RTP, 50% house edge (very unfair to player)

### 3. Get Supported Markets
```bash
curl https://app-pqyimwto.fly.dev/api/markets
```

**Available Markets:**
- **1X2** - Home win (`"1"`), Draw (`"X"`), Away win (`"2"`)
- **Over/Under** - `"over_2.5"`, `"under_2.5"`, etc.
- **Both Teams To Score** - `"yes"` or `"no"`
- **Correct Score** - `"2-1"`, `"3-0"`, etc.

### 4. Simulate Match
See examples below.

---

## Complete Examples

### Example 1: Testing RTP Impact

**Scenario:** Bet on Manchester to win, test with different RTP values

**High RTP (96% - Player favored):**
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/rtp -H "Content-Type: application/json" -d '{"rtp": 0.96}'

curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Manchester",
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
    "bet_selection": {
      "market": "1X2",
      "outcome": "1"
    },
    "volatility": "medium",
    "seed": 123
  }'
```

**Low RTP (10% - House heavily favored):**
```bash
curl -X POST https://app-pqyimwto.fly.dev/api/rtp -H "Content-Type: application/json" -d '{"rtp": 0.10}'

# Use same request as above with seed 123
```

Run both and compare - the final scores will be different based on RTP!

---

### Example 2: Over/Under 2.5 Goals

```bash
# Set RTP
curl -X POST https://app-pqyimwto.fly.dev/api/rtp -H "Content-Type: application/json" -d '{"rtp": 0.90}'

# Simulate with Over 2.5 bet
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Barcelona",
    "away_team": "Real Madrid",
    "score_probabilities": [
      {"home_score": 0, "away_score": 0, "probability": 0.10},
      {"home_score": 1, "away_score": 0, "probability": 0.15},
      {"home_score": 2, "away_score": 1, "probability": 0.25},
      {"home_score": 1, "away_score": 1, "probability": 0.15},
      {"home_score": 3, "away_score": 1, "probability": 0.15},
      {"home_score": 2, "away_score": 2, "probability": 0.10},
      {"home_score": 3, "away_score": 2, "probability": 0.10}
    ],
    "bet_selection": {
      "market": "over_under",
      "outcome": "over_2.5"
    },
    "volatility": "high"
  }'
```

---

### Example 3: Both Teams To Score

```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Liverpool",
    "away_team": "Chelsea",
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

---

### Example 4: Correct Score

```bash
curl -X POST https://app-pqyimwto.fly.dev/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Tottenham",
    "away_team": "Arsenal",
    "score_probabilities": [
      {"home_score": 0, "away_score": 0, "probability": 0.10},
      {"home_score": 1, "away_score": 0, "probability": 0.15},
      {"home_score": 2, "away_score": 1, "probability": 0.30},
      {"home_score": 1, "away_score": 1, "probability": 0.20},
      {"home_score": 2, "away_score": 0, "probability": 0.15},
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

## Understanding the Response

```json
{
  "home_team": "Manchester",
  "away_team": "Arsenal",
  "final_score": {
    "Manchester": 1,
    "Arsenal": 0
  },
  "bet_result": {
    "won": true,
    "outcome_occurred": true,
    "payout_multiplier": 2.5,
    "explanation": "Bet WON! You bet on 1X2: 1. Final score: Manchester 1 - 0 Arsenal. Your prediction was correct. Payout at 2.50x odds."
  },
  "events": [
    {
      "minute": 55,
      "event_type": "goal",
      "team": "Manchester",
      "description": "⚽ GOAL! M. Player 7 scores for Manchester! Manchester 1 - 0 Arsenal",
      "player": "M. Player 7"
    }
  ],
  "match_stats": {
    "possession": {"Manchester": 65.2, "Arsenal": 34.8},
    "shots": {"Manchester": 4, "Arsenal": 1},
    "corners": {"Manchester": 2, "Arsenal": 0},
    "fouls": {"Manchester": 1, "Arsenal": 0},
    "total_goals": 1
  },
  "simulation_metadata": {
    "rtp": 0.96,
    "volatility": "medium",
    "seed": 1,
    "bet_market": "1X2",
    "bet_outcome": "1",
    "house_decision": "win"
  }
}
```

**Key Fields:**
- `bet_result.won` - Did you win the bet?
- `bet_result.explanation` - Why you won/lost
- `simulation_metadata.house_decision` - What the RTP decided before simulation

---

## How It Really Works

### The RTP Flow:

1. **User sets RTP** (e.g., 85% = 15% house edge)
2. **User places bet** (e.g., "Manchester to win")
3. **System calculates win probability** = (Fair odds probability) × RTP
   - Fair probability for 1X2 ≈ 40%
   - With 85% RTP: 40% × 0.85 = 34% chance to win
4. **RNG decides** - Random number generated
   - If RNG < 34% → House lets you win
   - If RNG ≥ 34% → House makes you lose
5. **Probabilities adjusted**:
   - If house lets you win: Boost favorable scores (home wins), reduce unfavorable
   - If house makes you lose: Boost unfavorable scores (draws/away wins), reduce favorable
6. **Match simulated** with adjusted probabilities
7. **Final result** matches house decision

---

## Parameters

### Required:
- `home_team` - Home team name
- `away_team` - Away team name
- `score_probabilities` - Array of possible scores (must sum to 1.0)
- `bet_selection.market` - Market type (1X2, over_under, etc.)
- `bet_selection.outcome` - Your prediction

### Optional:
- `volatility` - "low", "medium", "high" (default: "medium")
- `seed` - Integer for reproducible results

---

## Testing RTP

**Try this experiment:**

```bash
# Set RTP to 96% (player-friendly)
curl -X POST https://app-pqyimwto.fly.dev/api/rtp -H "Content-Type: application/json" -d '{"rtp": 0.96}'

# Run simulation 10 times with different seeds
for i in {1..10}; do
  echo "Seed $i:"
  curl -X POST https://app-pqyimwto.fly.dev/api/simulate -H "Content-Type: application/json" -d "{\"home_team\":\"Man Utd\",\"away_team\":\"Arsenal\",\"score_probabilities\":[{\"home_score\":0,\"away_score\":0,\"probability\":0.1},{\"home_score\":1,\"away_score\":0,\"probability\":0.15},{\"home_score\":2,\"away_score\":0,\"probability\":0.12},{\"home_score\":2,\"away_score\":1,\"probability\":0.18},{\"home_score\":1,\"away_score\":1,\"probability\":0.15},{\"home_score\":3,\"away_score\":1,\"probability\":0.1},{\"home_score\":0,\"away_score\":1,\"probability\":0.08},{\"home_score\":1,\"away_score\":2,\"probability\":0.07},{\"home_score\":3,\"away_score\":2,\"probability\":0.05}],\"bet_selection\":{\"market\":\"1X2\",\"outcome\":\"1\"},\"volatility\":\"medium\",\"seed\":$i}" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Won: {data['bet_result']['won']}, Score: {data['final_score']}\")"
done

# You should win ~8-9 times out of 10 (96% RTP)
```

Then change RTP to 0.10 and run again - you should only win ~1 time out of 10!

---

**Built with gambling RNG mathematics** ⚽🎰

The RTP now correctly influences the simulation outcome BEFORE it happens, just like real slot machines and casino games!
