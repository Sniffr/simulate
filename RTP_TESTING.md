# RTP Testing Scripts

This directory contains Python scripts to test the RTP (Return to Player) balancing system by simulating realistic betting behavior.

## Prerequisites

```bash
pip install requests
```

## Test Scripts

### 1. `test_rtp_simulation.py` - Full Simulation

Simulates realistic betting behavior with multiple users, varying stakes, different teams, and both single and multi-match bets.

**Features:**
- 5 simulated users with different betting patterns
- Mix of single bets (70%) and multi-match accumulators (30%)
- Varying stake amounts based on user profiles
- Random team matchups from 10 different teams
- Multiple betting markets (1X2, Over/Under)
- Detailed per-user and overall statistics

**Usage:**

```bash
# Run full simulation (200 bets, ~20 seconds with default delay)
python3 test_rtp_simulation.py

# Edit the script to customize:
# - API_URL: Change to http://localhost:8000 for local testing
# - TOTAL_BETS: Number of bets to simulate (default: 200)
# - DELAY_BETWEEN_REQUESTS: Seconds between requests (default: 0.1)
```

**Output:**
```
================================================================================
🎰 RTP Balancing System Test - Simulating Realistic Betting Behavior
================================================================================

Configuration:
  • API URL: https://app-pqyimwto.fly.dev
  • Total bets to simulate: 200
  • Number of users: 5
  • Delay between requests: 0.1s

📊 Initial Statistics:
  • Total simulations: 7
  • Actual RTP: 71.75%
  • Configured RTP: 96.00%

🎲 Starting simulation...

[  1/200] SINGLE | User: user_alice   | ✅ WIN | Stake: $ 47.04 | Running RTP: 251.20%
[  2/200] MULTI  | User: user_bob     | ❌ LOSS | Stake: $  0.00 | Running RTP: 251.20%
...

================================================================================
📊 FINAL RESULTS
================================================================================

Overall Statistics:
  • Total bets placed: 200
  • Single bets: 139 (69.5%)
  • Multi bets: 61 (30.5%)
  • Wins: 85 (42.5%)
  • Losses: 115 (57.5%)
  • Total staked: $9663.25
  • Total payout: $12599.12
  • Net profit/loss: $2935.87
  • Calculated RTP: 130.38%

Per-User Statistics:

  user_alice:
    • Bets placed: 69 (total simulations: 69)
    • Win rate: 43.5%
    • Total staked: $3459.26
    • Total payout: $3880.21
    • Actual RTP: 112.17%
    • Target RTP: 96.00%
    • RTP Difference: +16.17% ❌ OFF

  user_bob:
    • Bets placed: 29 (total simulations: 29)
    • Win rate: 34.5%
    • Total staked: $2758.75
    • Total payout: $2548.69
    • Actual RTP: 92.39%
    • Target RTP: 96.00%
    • RTP Difference: -3.61% ✅ GOOD
```

### 2. `test_rtp_quick.py` - Quick Test

Simple script for rapid testing with a single user and consistent bet parameters.

**Features:**
- Single user testing
- Fixed stake amount ($10) and odds (2.5x)
- Simple 1X2 betting market
- Fast execution for quick verification

**Usage:**

```bash
# Run with default settings (50 bets on production API)
python3 test_rtp_quick.py

# Custom number of bets
python3 test_rtp_quick.py 100

# Test against local server
python3 test_rtp_quick.py 100 http://localhost:8000

# Test against production
python3 test_rtp_quick.py 200 https://app-pqyimwto.fly.dev
```

**Output:**
```
🎲 Quick RTP Test: 50 bets on https://app-pqyimwto.fly.dev

[  1/ 50] ✅ WIN  | RTP: 250.00%
[  2/ 50] ❌ LOSS | RTP: 125.00%
[  3/ 50] ✅ WIN  | RTP: 166.67%
...
[ 50/ 50] ❌ LOSS | RTP:  96.20%

Final Results:
  Wins: 21, Losses: 29 (42.0% win rate)
  Total Stake: $500.00
  Total Payout: $481.00
  Final RTP: 96.20%

Player Stats from API:
  Total Simulations: 50
  Actual RTP: 96.20%
  Target RTP: 96.00%
  RTP Difference: +0.20%
```

## Understanding the Results

### RTP Status Indicators

- ✅ **GOOD**: RTP difference < ±5% (very close to target)
- ⚠️ **OK**: RTP difference < ±10% (acceptable, will converge)
- ❌ **OFF**: RTP difference > ±10% (needs more bets to converge)

### Expected Behavior

1. **Initial Variance**: With few bets (< 50), RTP can vary significantly due to randomness
2. **Convergence**: As bets increase (100-500), RTP should converge toward the configured target (96%)
3. **Per-User Balancing**: Each user's RTP is tracked independently and adjusted dynamically
4. **Natural Fluctuation**: Some variance is expected - the system aims for ±2-5% of target RTP

### What "Good" Results Look Like

After **200+ bets** per user:
- Overall RTP: 92-100% (within ±4% of 96% target)
- Per-user RTP: 90-102% (within ±6% of 96% target)
- RTP Difference: -5% to +5%

### RTP Balancing Mechanism

The system adjusts win probabilities dynamically:

1. **Player below target** (e.g., 85% RTP when target is 96%)
   - System **increases** their win probability by up to 50%
   - Helps them catch up to the target RTP

2. **Player above target** (e.g., 105% RTP when target is 96%)
   - System **decreases** their win probability by up to 50%
   - Pulls them back down to the target RTP

3. **Adjustment strength**: 30% of the RTP difference
   - Example: 10% below target → 3% adjustment (10% × 0.3)

## Tips for Testing

### Test RTP Convergence
```bash
# Run multiple test cycles and observe RTP trends
for i in {1..5}; do
  echo "=== Test Cycle $i ==="
  python3 test_rtp_quick.py 100
  sleep 2
done
```

### Test Different User Scenarios

Edit `test_rtp_simulation.py` to create specific scenarios:

```python
# Heavy bettor who should be pulled down
USERS = [
    {"id": "whale_user", "bet_frequency": 1.0, "avg_stake": 500},
]
```

### Monitor in Real-Time

Open the dashboard while running tests:
- Production: https://football-simulation-app-qlot6bn9.devinapps.com
- Watch RTP trends update in real-time
- View per-player statistics

### Test Local Changes

```bash
# 1. Start local backend
cd football_sim_backend
poetry run fastapi dev app/main.py

# 2. In another terminal, run tests
python3 test_rtp_quick.py 100 http://localhost:8000
```

## Troubleshooting

### Connection Errors
```
❌ Error sending request: HTTPConnectionPool...
```
**Solution:** Check API URL is correct and server is running

### Slow Execution
```
Taking too long (> 1 minute for 50 bets)
```
**Solution:** Reduce `DELAY_BETWEEN_REQUESTS` in `test_rtp_simulation.py` or check network latency

### RTP Not Converging
```
RTP stays at 110% after 500 bets
```
**Possible causes:**
1. Not enough bets yet - try 1000+
2. Check `_calculate_rtp_adjustment()` logic in `betting_logic.py`
3. Verify player stats are being fetched correctly in `main.py`

### Multi-Bet Showing $0 Stake
```
[ 10/200] MULTI  | User: user_bob | ❌ LOSS | Stake: $  0.00
```
**Expected behavior:** Multi-match bets have a single stake for the entire betslip, not per selection. The display shows $0 for individual selections but the actual stake is tracked correctly.

## Advanced Testing

### Stress Test
```bash
# 1000 bets, minimal delay
# Edit test_rtp_simulation.py:
TOTAL_BETS = 1000
DELAY_BETWEEN_REQUESTS = 0.01
```

### User Migration Test
```python
# Simulate user who quits and returns
# Edit test_rtp_simulation.py to add inactive periods:
if bet_num == 100:
    print("User taking a break...")
    time.sleep(10)
```

### Market Distribution Test
```python
# Test specific markets
MARKETS = ["1X2"]  # Only test 1X2 market
# or
MARKETS = ["over_under"]  # Only test over/under
```

## Expected RTP Trends

With the default 96% RTP configuration:

| Bets  | Expected RTP Range | Status |
|-------|-------------------|---------|
| 10    | 70-140%          | Normal variance |
| 50    | 85-110%          | Converging |
| 100   | 90-105%          | Good |
| 200   | 92-100%          | Excellent |
| 500+  | 94-98%           | Optimal |

## Links

- Backend API: https://app-pqyimwto.fly.dev
- Dashboard: https://football-simulation-app-qlot6bn9.devinapps.com
- API Documentation: https://app-pqyimwto.fly.dev/docs
