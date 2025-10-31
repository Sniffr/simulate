#!/usr/bin/env python3
"""
Test script to verify GLOBAL RTP implementation.

This script simulates multiple players betting simultaneously and verifies that:
1. The TOTAL payout across ALL players converges to ~96% of TOTAL stakes
2. Individual player results can vary (some win, some lose)
3. The house maintains its edge across the entire player base
"""

import requests
import random
import time
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000"

NUM_PLAYERS = 10
BETS_PER_PLAYER = 50
STAKE_AMOUNT = 10.0

def get_random_match_data():
    """Generate random match data for testing"""
    home_teams = ["Manchester", "Liverpool", "Chelsea", "Arsenal", "Tottenham"]
    away_teams = ["Newcastle", "Brighton", "Fulham", "Everton", "Southampton"]
    
    return {
        "home_team": random.choice(home_teams),
        "away_team": random.choice(away_teams),
        "score_probabilities": [
            {"home_score": 1, "away_score": 0, "probability": 0.15},
            {"home_score": 2, "away_score": 0, "probability": 0.10},
            {"home_score": 2, "away_score": 1, "probability": 0.12},
            {"home_score": 0, "away_score": 0, "probability": 0.10},
            {"home_score": 1, "away_score": 1, "probability": 0.15},
            {"home_score": 0, "away_score": 1, "probability": 0.12},
            {"home_score": 0, "away_score": 2, "probability": 0.08},
            {"home_score": 3, "away_score": 0, "probability": 0.05},
            {"home_score": 3, "away_score": 1, "probability": 0.05},
            {"home_score": 1, "away_score": 2, "probability": 0.08},
        ]
    }

def place_bet(player_id: str, bet_number: int) -> Dict[str, Any]:
    """Place a single bet for a player"""
    match_data = get_random_match_data()
    
    bet_types = [
        {"market": "1X2", "outcome": "1", "odds": 2.1},
        {"market": "1X2", "outcome": "X", "odds": 3.2},
        {"market": "1X2", "outcome": "2", "odds": 3.5},
        {"market": "over_under", "outcome": "over_2.5", "odds": 1.9},
        {"market": "over_under", "outcome": "under_2.5", "odds": 1.95},
    ]
    
    bet = random.choice(bet_types)
    bet["stake"] = STAKE_AMOUNT
    
    payload = {
        **match_data,
        "bet_slip": [bet],
        "user_id": player_id,
        "seed": random.randint(1, 1000000)
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/simulate", json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error placing bet for {player_id}: {e}")
        return None

def run_simulation():
    """Run the complete simulation"""
    print("=" * 80)
    print("GLOBAL RTP BACKTEST")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  Players: {NUM_PLAYERS}")
    print(f"  Bets per player: {BETS_PER_PLAYER}")
    print(f"  Stake per bet: ${STAKE_AMOUNT:.2f}")
    print(f"  Total bets: {NUM_PLAYERS * BETS_PER_PLAYER}")
    print(f"  Total stakes: ${NUM_PLAYERS * BETS_PER_PLAYER * STAKE_AMOUNT:.2f}")
    print("=" * 80)
    print()
    
    player_results = {}
    for i in range(NUM_PLAYERS):
        player_id = f"test_player_{i+1}"
        player_results[player_id] = {
            "total_staked": 0.0,
            "total_won": 0.0,
            "bets_placed": 0,
            "bets_won": 0
        }
    
    total_bets = NUM_PLAYERS * BETS_PER_PLAYER
    current_bet = 0
    
    for bet_num in range(BETS_PER_PLAYER):
        for player_id in player_results.keys():
            current_bet += 1
            print(f"Bet {current_bet}/{total_bets} - {player_id}...", end="\r")
            
            result = place_bet(player_id, bet_num)
            if result and result.get("bet_results"):
                player_results[player_id]["bets_placed"] += 1
                player_results[player_id]["total_staked"] += STAKE_AMOUNT
                
                for bet_result in result["bet_results"]:
                    if bet_result.get("won"):
                        player_results[player_id]["bets_won"] += 1
                        if bet_result.get("payout"):
                            player_results[player_id]["total_won"] += bet_result["payout"]
            
            time.sleep(0.05)  # Small delay to avoid overwhelming the API
    
    print("\n")
    print("=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)
    print()
    
    global_total_staked = sum(p["total_staked"] for p in player_results.values())
    global_total_won = sum(p["total_won"] for p in player_results.values())
    global_house_profit = global_total_staked - global_total_won
    global_rtp = (global_total_won / global_total_staked * 100) if global_total_staked > 0 else 0
    global_house_edge = 100 - global_rtp
    
    print("GLOBAL RESULTS (All Players Combined):")
    print(f"  Total Staked:     ${global_total_staked:.2f}")
    print(f"  Total Paid Out:   ${global_total_won:.2f}")
    print(f"  House Profit:     ${global_house_profit:.2f}")
    print(f"  Global RTP:       {global_rtp:.2f}%")
    print(f"  House Edge:       {global_house_edge:.2f}%")
    print()
    
    expected_rtp = 96.0
    expected_payout = global_total_staked * (expected_rtp / 100)
    rtp_deviation = abs(global_rtp - expected_rtp)
    
    print(f"TARGET: {expected_rtp}% RTP")
    print(f"  Expected Payout:  ${expected_payout:.2f}")
    print(f"  Actual Payout:    ${global_total_won:.2f}")
    print(f"  Deviation:        {rtp_deviation:.2f}%")
    print()
    
    print("=" * 80)
    print("PER-PLAYER RESULTS (Individual Variance)")
    print("=" * 80)
    for player_id, stats in sorted(player_results.items()):
        player_rtp = (stats["total_won"] / stats["total_staked"] * 100) if stats["total_staked"] > 0 else 0
        win_rate = (stats["bets_won"] / stats["bets_placed"] * 100) if stats["bets_placed"] > 0 else 0
        profit_loss = stats["total_won"] - stats["total_staked"]
        
        status = "🟢 WINNING" if profit_loss > 0 else "🔴 LOSING"
        
        print(f"{player_id}:")
        print(f"  Staked: ${stats['total_staked']:.2f} | Won: ${stats['total_won']:.2f} | P/L: ${profit_loss:+.2f}")
        print(f"  RTP: {player_rtp:.1f}% | Win Rate: {win_rate:.1f}% | Status: {status}")
        print()
    
    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    tolerance = 2.0  # Allow 2% deviation for statistical variance
    
    if abs(global_rtp - expected_rtp) <= tolerance:
        print(f"✅ PASS: Global RTP ({global_rtp:.2f}%) is within {tolerance}% of target ({expected_rtp}%)")
    else:
        print(f"❌ FAIL: Global RTP ({global_rtp:.2f}%) deviates more than {tolerance}% from target ({expected_rtp}%)")
    
    print()
    
    if global_house_profit > 0:
        print(f"✅ PASS: House is profitable (${global_house_profit:.2f} profit)")
    else:
        print(f"❌ FAIL: House is losing money (${global_house_profit:.2f} loss)")
    
    print()
    
    player_rtps = [
        (stats["total_won"] / stats["total_staked"] * 100) if stats["total_staked"] > 0 else 0
        for stats in player_results.values()
    ]
    rtp_variance = max(player_rtps) - min(player_rtps)
    print(f"📊 Player RTP variance: {rtp_variance:.1f}% (range: {min(player_rtps):.1f}% - {max(player_rtps):.1f}%)")
    print(f"   This variance is EXPECTED - individual players can win or lose while house maintains edge")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    print("\nStarting global RTP backtest...")
    print("Make sure the backend is running on http://localhost:8000")
    print()
    
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=5)
        response.raise_for_status()
        print("✅ Backend is running\n")
    except:
        print("❌ Cannot connect to backend. Please start it first:")
        print("   cd football_sim_backend && uvicorn app.main:app --reload")
        exit(1)
    
    run_simulation()
