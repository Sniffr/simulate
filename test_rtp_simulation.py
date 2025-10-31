#!/usr/bin/env python3
"""
RTP Testing Script - Simulates realistic betting behavior
This script sends multiple simulation requests to test the RTP balancing system
"""

import requests
import random
import time
from typing import List, Dict, Any
import json

API_URL = "http://localhost:8000"  # Change to http://localhost:8000 for local testing
TOTAL_BETS = 10000  # Total number of bets to simulate
DELAY_BETWEEN_REQUESTS = 0.000000001  # Seconds between requests (to avoid overwhelming the server)

USERS = [
    {"id": "user_alice", "bet_frequency": 0.3, "avg_stake": 50},
    {"id": "user_bob", "bet_frequency": 0.25, "avg_stake": 100},
    {"id": "user_charlie", "bet_frequency": 0.2, "avg_stake": 25},
    {"id": "user_diana", "bet_frequency": 0.15, "avg_stake": 75},
    {"id": "user_eve", "bet_frequency": 0.1, "avg_stake": 150},  # High roller
    {"id": "user_sidongo", "bet_frequency": 0.1, "avg_stake": 150},  # High roller
    {"id": "user_atse", "bet_frequency": 0.4, "avg_stake": 30},  # High roller
    {"id": "user_lolo", "bet_frequency": 0.2, "avg_stake": 10},  # High roller
    {"id": "user_suko", "bet_frequency": 0.1, "avg_stake": 15},  # High roller
    {"id": "user_appolo", "bet_frequency": 0.6, "avg_stake": 20},  # High roller
    {"id": "user_selee", "bet_frequency": 0.1, "avg_stake": 50},  # High roller
    {"id": "user_mele", "bet_frequency": 0.7, "avg_stake": 5},  # High roller
]

TEAMS = [
    ("Manchester United", "Arsenal"),
    ("Liverpool", "Chelsea"),
    ("Barcelona", "Real Madrid"),
    ("Bayern Munich", "Borussia Dortmund"),
    ("PSG", "Lyon"),
    ("Juventus", "AC Milan"),
    ("Atletico Madrid", "Sevilla"),
    ("Tottenham", "Manchester City"),
    ("Inter Milan", "Napoli"),
    ("Ajax", "PSV"),
]

MARKETS = ["1X2", "over_under"]

def generate_score_probabilities() -> List[Dict[str, Any]]:
    """Generate realistic score probabilities that sum to ~1.0"""
    probabilities = []
    
    probabilities.extend([
        {"home_score": 1, "away_score": 0, "probability": random.uniform(0.10, 0.15)},
        {"home_score": 2, "away_score": 0, "probability": random.uniform(0.06, 0.10)},
        {"home_score": 2, "away_score": 1, "probability": random.uniform(0.06, 0.10)},
        {"home_score": 3, "away_score": 0, "probability": random.uniform(0.02, 0.04)},
        {"home_score": 3, "away_score": 1, "probability": random.uniform(0.02, 0.04)},
    ])
    
    probabilities.extend([
        {"home_score": 0, "away_score": 0, "probability": random.uniform(0.08, 0.12)},
        {"home_score": 1, "away_score": 1, "probability": random.uniform(0.10, 0.15)},
        {"home_score": 2, "away_score": 2, "probability": random.uniform(0.03, 0.06)},
    ])
    
    probabilities.extend([
        {"home_score": 0, "away_score": 1, "probability": random.uniform(0.08, 0.12)},
        {"home_score": 0, "away_score": 2, "probability": random.uniform(0.04, 0.07)},
        {"home_score": 1, "away_score": 2, "probability": random.uniform(0.05, 0.08)},
        {"home_score": 0, "away_score": 3, "probability": random.uniform(0.01, 0.03)},
        {"home_score": 1, "away_score": 3, "probability": random.uniform(0.02, 0.04)},
    ])
    
    total = sum(p["probability"] for p in probabilities)
    for p in probabilities:
        p["probability"] = p["probability"] / total
    
    return probabilities

def generate_single_bet(user: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a single match bet request"""
    home_team, away_team = random.choice(TEAMS)
    stake = max(1.0, random.gauss(user["avg_stake"], user["avg_stake"] * 0.3))
    stake = max(1.0, round(stake, 2))  # Ensure stake is at least 1.0 after rounding
    
    market = random.choice(MARKETS)
    
    if market == "1X2":
        outcome = random.choice(["1", "X", "2"])
        odds = random.uniform(1.8, 3.5)
    else:  # over_under
        outcome = random.choice(["over_2.5", "under_2.5"])
        odds = random.uniform(1.7, 2.2)
    
    return {
        "home_team": home_team,
        "away_team": away_team,
        "score_probabilities": generate_score_probabilities(),
        "bet_slip": [
            {
                "market": market,
                "outcome": outcome,
                "stake": stake,
                "odds": round(odds, 2)
            }
        ],
        "user_id": user["id"],
        "volatility": random.choice(["low", "medium", "high"]),
        "seed": random.randint(1, 1000000)
    }

def generate_multi_bet(user: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a multi-match accumulator bet"""
    num_matches = random.randint(2, 4)
    stake = max(1.0, random.gauss(user["avg_stake"] * 0.7, user["avg_stake"] * 0.2))
    stake = max(1.0, round(stake, 2))  # Ensure stake is at least 1.0 after rounding
    
    matches = []
    bet_slip = []
    
    for i in range(num_matches):
        home_team, away_team = random.choice(TEAMS)
        match_id = f"match_{i}"
        
        matches.append({
            "match_id": match_id,
            "home_team": home_team,
            "away_team": away_team,
            "score_probabilities": generate_score_probabilities()
        })
        
        market = random.choice(MARKETS)
        
        if market == "1X2":
            outcome = random.choice(["1", "X", "2"])
            odds = random.uniform(1.8, 3.5)
        else:  # over_under
            outcome = random.choice(["over_2.5", "under_2.5"])
            odds = random.uniform(1.7, 2.2)
        
        bet_slip.append({
            "match_id": match_id,
            "home_team": home_team,
            "away_team": away_team,
            "market": market,
            "outcome": outcome,
            "odds": round(odds, 2)
        })
    
    return {
        "matches": matches,
        "bet_slip": bet_slip,
        "stake": stake,
        "user_id": user["id"],
        "volatility": random.choice(["low", "medium", "high"]),
        "seed": random.randint(1, 1000000)
    }

def send_simulation(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send simulation request to API"""
    try:
        response = requests.post(f"{API_URL}/api/{endpoint}", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending request: {e}")
        return None

def get_stats() -> Dict[str, Any]:
    """Get current statistics from API"""
    try:
        response = requests.get(f"{API_URL}/api/stats", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching stats: {e}")
        return None

def get_player_stats(user_id: str) -> Dict[str, Any]:
    """Get statistics for a specific player"""
    try:
        response = requests.get(f"{API_URL}/api/players/{user_id}/stats", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching player stats: {e}")
        return None

def main():
    print("=" * 80)
    print("🎰 RTP Balancing System Test - Simulating Realistic Betting Behavior")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  • API URL: {API_URL}")
    print(f"  • Total bets to simulate: {TOTAL_BETS}")
    print(f"  • Number of users: {len(USERS)}")
    print(f"  • Delay between requests: {DELAY_BETWEEN_REQUESTS}s")
    print()
    
    user_bet_counts = {user["id"]: 0 for user in USERS}
    results = {
        "total_bets": 0,
        "single_bets": 0,
        "multi_bets": 0,
        "wins": 0,
        "losses": 0,
        "total_staked": 0.0,
        "total_payout": 0.0,
    }
    
    print("📊 Initial Statistics:")
    initial_stats = get_stats()
    if initial_stats:
        print(f"  • Total simulations: {initial_stats.get('total_simulations', 0)}")
        print(f"  • Actual RTP: {initial_stats.get('actual_rtp', 0):.2%}")
        print(f"  • Configured RTP: {initial_stats.get('avg_configured_rtp', 0):.2%}")
    print()
    
    print("🎲 Starting simulation...")
    print()
    
    for bet_num in range(1, TOTAL_BETS + 1):
        user = random.choices(USERS, weights=[u["bet_frequency"] for u in USERS])[0]
        user_bet_counts[user["id"]] += 1
        
        is_multi = random.random() < 0.3
        
        if is_multi:
            endpoint = "simulate-multi"
            payload = generate_multi_bet(user)
            bet_type = "MULTI"
            results["multi_bets"] += 1
        else:
            endpoint = "simulate"
            payload = generate_single_bet(user)
            bet_type = "SINGLE"
            results["single_bets"] += 1
        
        response = send_simulation(endpoint, payload)
        
        if response:
            results["total_bets"] += 1
            
            won = response.get("bet_slip_won", False)
            # Get stake from response, fallback to payload stake, ensure minimum of 1.0
            stake = response.get("total_stake")
            if stake is None or stake == 0:
                # Fallback to payload stake for multi bets or bet_slip stake for single bets
                if is_multi:
                    stake = payload.get("stake", 1.0)
                else:
                    stake = payload.get("bet_slip", [{}])[0].get("stake", 1.0)
            stake = max(1.0, stake)  # Ensure minimum stake of 1.0
            payout = response.get("total_payout") or 0
            
            results["total_staked"] += stake
            results["total_payout"] += payout
            
            if won:
                results["wins"] += 1
                status = "✅ WIN"
            else:
                results["losses"] += 1
                status = "❌ LOSS"
            
            if bet_num % 10 == 0 or bet_num <= 5:
                current_rtp = (results["total_payout"] / results["total_staked"]) if results["total_staked"] > 0 else 0
                print(f"[{bet_num:3d}/{TOTAL_BETS}] {bet_type:6s} | User: {user['id']:12s} | {status} | Stake: ${stake:6.2f} | Running RTP: {current_rtp:.2%}")
        
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    print()
    print("=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)
    print()
    
    print("Overall Statistics:")
    print(f"  • Total bets placed: {results['total_bets']}")
    if results['total_bets'] > 0:
        print(f"  • Single bets: {results['single_bets']} ({results['single_bets']/results['total_bets']*100:.1f}%)")
        print(f"  • Multi bets: {results['multi_bets']} ({results['multi_bets']/results['total_bets']*100:.1f}%)")
        print(f"  • Wins: {results['wins']} ({results['wins']/results['total_bets']*100:.1f}%)")
        print(f"  • Losses: {results['losses']} ({results['losses']/results['total_bets']*100:.1f}%)")
    else:
        print("  ⚠️  No bets were placed - backend may not be running!")
        print("  Please start the backend with: cd football_sim_backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print(f"  • Total staked: ${results['total_staked']:.2f}")
    print(f"  • Total payout: ${results['total_payout']:.2f}")
    print(f"  • Net profit/loss: ${results['total_payout'] - results['total_staked']:.2f}")
    
    current_rtp = (results["total_payout"] / results["total_staked"]) if results["total_staked"] > 0 else 0
    print(f"  • Calculated RTP: {current_rtp:.2%}")
    print()
    
    print("Per-User Statistics:")
    for user in USERS:
        player_stats = get_player_stats(user["id"])
        if player_stats and player_stats.get("total_simulations", 0) > 0:
            print(f"\n  {user['id']}:")
            print(f"    • Bets placed: {user_bet_counts[user['id']]} (total simulations: {player_stats['total_simulations']})")
            print(f"    • Win rate: {player_stats.get('win_rate', 0):.1f}%")
            print(f"    • Total staked: ${player_stats.get('total_staked', 0):.2f}")
            print(f"    • Total payout: ${player_stats.get('total_paid_out', 0):.2f}")
            print(f"    • Actual RTP: {player_stats.get('actual_rtp', 0):.2%}")
            print(f"    • Target RTP: {player_stats.get('avg_configured_rtp', 0):.2%}")
            
            rtp_diff = player_stats.get('rtp_difference', 0)
            if abs(rtp_diff) < 0.05:
                status = "✅ GOOD"
            elif abs(rtp_diff) < 0.10:
                status = "⚠️  OK"
            else:
                status = "❌ OFF"
            print(f"    • RTP Difference: {rtp_diff:+.2%} {status}")
    
    print()
    
    print("API Statistics:")
    final_stats = get_stats()
    if final_stats:
        print(f"  • Total simulations in DB: {final_stats.get('total_simulations', 0)}")
        print(f"  • Won slips: {final_stats.get('won_slips', 0)}")
        print(f"  • Lost slips: {final_stats.get('lost_slips', 0)}")
        print(f"  • Total staked (all users): ${final_stats.get('total_staked', 0):.2f}")
        print(f"  • Total paid out (all users): ${final_stats.get('total_paid_out', 0):.2f}")
        print(f"  • House profit: ${final_stats.get('house_profit', 0):.2f}")
        print(f"  • Actual RTP: {final_stats.get('actual_rtp', 0):.2%}")
        print(f"  • Configured RTP: {final_stats.get('avg_configured_rtp', 0):.2%}")
        print(f"  • RTP Difference: {final_stats.get('rtp_difference', 0):+.2%}")
    
    print()
    print("=" * 80)
    print("✅ Simulation complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
