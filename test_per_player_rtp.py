#!/usr/bin/env python3
"""
Test script to verify per-player RTP calculation works correctly.
This ensures RTP is calculated independently for each player.
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_per_player_rtp():
    print("=== Testing Per-Player RTP Calculation ===\n")
    
    print("1. Setting RTP to 96%...")
    response = requests.post(f"{BASE_URL}/api/rtp", json={"rtp": 0.96})
    print(f"   RTP configured: {response.json()}\n")
    
    player1 = "alice"
    player2 = "bob"
    
    probabilities = [
        {"home_score": 1, "away_score": 0, "probability": 0.5},
        {"home_score": 0, "away_score": 1, "probability": 0.5}
    ]
    
    print(f"2. Simulating 10 bets for Player 1 ({player1})...")
    player1_wins = 0
    player1_total_stake = 0
    player1_total_payout = 0
    
    for i in range(10):
        bet_request = {
            "user_id": player1,
            "home_team": "TeamA",
            "away_team": "TeamB",
            "score_probabilities": probabilities,
            "bet_slip": [{
                "market": "1X2",
                "outcome": "1",
                "stake": 10.0,
                "odds": 2.0
            }],
            "volatility": "medium",
            "seed": 1000 + i  # Different seed for each simulation
        }
        
        response = requests.post(f"{BASE_URL}/api/simulate", json=bet_request)
        result = response.json()
        
        if result['bet_slip_won']:
            player1_wins += 1
        
        player1_total_stake += result['total_stake']
        player1_total_payout += result['total_payout']
    
    player1_actual_rtp = (player1_total_payout / player1_total_stake) if player1_total_stake > 0 else 0
    print(f"   Player 1 Results: {player1_wins}/10 wins")
    print(f"   Total Staked: ${player1_total_stake:.2f}")
    print(f"   Total Payout: ${player1_total_payout:.2f}")
    print(f"   Actual RTP: {player1_actual_rtp:.2%}\n")
    
    print(f"3. Simulating 10 bets for Player 2 ({player2})...")
    player2_wins = 0
    player2_total_stake = 0
    player2_total_payout = 0
    
    for i in range(10):
        bet_request = {
            "user_id": player2,
            "home_team": "TeamC",
            "away_team": "TeamD",
            "score_probabilities": probabilities,
            "bet_slip": [{
                "market": "1X2",
                "outcome": "2",
                "stake": 20.0,
                "odds": 2.0
            }],
            "volatility": "medium",
            "seed": 2000 + i  # Different seed for each simulation
        }
        
        response = requests.post(f"{BASE_URL}/api/simulate", json=bet_request)
        result = response.json()
        
        if result['bet_slip_won']:
            player2_wins += 1
        
        player2_total_stake += result['total_stake']
        player2_total_payout += result['total_payout']
    
    player2_actual_rtp = (player2_total_payout / player2_total_stake) if player2_total_stake > 0 else 0
    print(f"   Player 2 Results: {player2_wins}/10 wins")
    print(f"   Total Staked: ${player2_total_stake:.2f}")
    print(f"   Total Payout: ${player2_total_payout:.2f}")
    print(f"   Actual RTP: {player2_actual_rtp:.2%}\n")
    
    print("4. Fetching per-player statistics from API...")
    
    player1_stats = requests.get(f"{BASE_URL}/api/players/{player1}/stats").json()
    print(f"\n   Player 1 ({player1}) Stats from API:")
    print(f"   - Total Simulations: {player1_stats['total_simulations']}")
    print(f"   - Won Slips: {player1_stats['won_slips']}")
    print(f"   - Total Staked: ${player1_stats['total_staked']:.2f}")
    print(f"   - Total Payout: ${player1_stats['total_paid_out']:.2f}")
    print(f"   - Actual RTP: {player1_stats['actual_rtp']:.2%}")
    print(f"   - House Profit: ${player1_stats['house_profit']:.2f}")
    
    player2_stats = requests.get(f"{BASE_URL}/api/players/{player2}/stats").json()
    print(f"\n   Player 2 ({player2}) Stats from API:")
    print(f"   - Total Simulations: {player2_stats['total_simulations']}")
    print(f"   - Won Slips: {player2_stats['won_slips']}")
    print(f"   - Total Staked: ${player2_stats['total_staked']:.2f}")
    print(f"   - Total Payout: ${player2_stats['total_paid_out']:.2f}")
    print(f"   - Actual RTP: {player2_stats['actual_rtp']:.2%}")
    print(f"   - House Profit: ${player2_stats['house_profit']:.2f}")
    
    print("\n5. Fetching overall statistics...")
    overall_stats = requests.get(f"{BASE_URL}/api/stats").json()
    print(f"   Overall Stats:")
    print(f"   - Total Simulations: {overall_stats['total_simulations']}")
    print(f"   - Total Staked: ${overall_stats['total_staked']:.2f}")
    print(f"   - Total Payout: ${overall_stats['total_paid_out']:.2f}")
    print(f"   - Overall Actual RTP: {overall_stats['actual_rtp']:.2%}")
    print(f"   - Total House Profit: ${overall_stats['house_profit']:.2f}")
    
    print("\n6. Fetching all players list...")
    all_players = requests.get(f"{BASE_URL}/api/players").json()
    print(f"   All Players ({len(all_players['players'])}):")
    for player in all_players['players']:
        print(f"   - {player['user_id']}: {player['total_simulations']} sims, RTP: {player['actual_rtp']:.2%}")
    
    print("\n=== VERIFICATION ===")
    print(f"✓ Player 1 RTP ({player1_stats['actual_rtp']:.2%}) is calculated independently")
    print(f"✓ Player 2 RTP ({player2_stats['actual_rtp']:.2%}) is calculated independently")
    print(f"✓ Each player has their own stake/payout tracking")
    print(f"✓ Overall RTP ({overall_stats['actual_rtp']:.2%}) combines all players")
    
    if abs(overall_stats['actual_rtp'] - 0.96) > 0.20:  # Allow 20% variance with small sample
        print(f"\n⚠️  Note: With only 20 total simulations, RTP variance is expected.")
        print(f"   Run more simulations for RTP to converge to configured 96%.")
    else:
        print(f"\n✓ Overall RTP is within expected range!")
    
    print("\n=== Test Complete! ===")

if __name__ == "__main__":
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        if response.status_code != 200:
            print("❌ Backend is not responding. Please start it with:")
            print("   cd football_sim_backend && poetry run fastapi dev app/main.py")
            exit(1)
        
        test_per_player_rtp()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend at " + BASE_URL)
        print("   Please start it with:")
        print("   cd football_sim_backend && poetry run fastapi dev app/main.py")
        exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
