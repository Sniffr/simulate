#!/usr/bin/env python3
"""
Quick RTP Test - Simple version for local testing
Run with: python3 test_rtp_quick.py [num_bets] [api_url]
Example: python3 test_rtp_quick.py 50 http://localhost:8000
"""

import requests
import random
import sys

def main():
    num_bets = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    api_url = sys.argv[2] if len(sys.argv) > 2 else "https://app-pqyimwto.fly.dev"
    
    print(f"🎲 Quick RTP Test: {num_bets} bets on {api_url}")
    print()
    
    user_id = "test_user_quick"
    wins = 0
    losses = 0
    total_stake = 0.0
    total_payout = 0.0
    
    for i in range(1, num_bets + 1):
        payload = {
            "home_team": "Team A",
            "away_team": "Team B",
            "score_probabilities": [
                {"home_score": 1, "away_score": 0, "probability": 0.3},
                {"home_score": 0, "away_score": 1, "probability": 0.3},
                {"home_score": 1, "away_score": 1, "probability": 0.4}
            ],
            "bet_slip": [
                {
                    "market": "1X2",
                    "outcome": "1",
                    "stake": 10.0,
                    "odds": 2.5
                }
            ],
            "user_id": user_id,
            "volatility": "medium",
            "seed": i
        }
        
        try:
            response = requests.post(f"{api_url}/api/simulate", json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            won = result.get("bet_slip_won", False)
            stake = result.get("total_stake", 0)
            payout = result.get("total_payout", 0)
            
            total_stake += stake
            total_payout += payout
            
            if won:
                wins += 1
                print(f"[{i:3d}/{num_bets}] ✅ WIN  | RTP: {(total_payout/total_stake)*100:6.2f}%")
            else:
                losses += 1
                print(f"[{i:3d}/{num_bets}] ❌ LOSS | RTP: {(total_payout/total_stake)*100:6.2f}%")
                
        except Exception as e:
            print(f"[{i:3d}/{num_bets}] ❌ ERROR: {e}")
    
    print()
    print(f"Final Results:")
    print(f"  Wins: {wins}, Losses: {losses} ({wins/(wins+losses)*100:.1f}% win rate)")
    print(f"  Total Stake: ${total_stake:.2f}")
    print(f"  Total Payout: ${total_payout:.2f}")
    print(f"  Final RTP: {(total_payout/total_stake)*100:.2f}%")
    
    try:
        response = requests.get(f"{api_url}/api/players/{user_id}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print()
            print(f"Player Stats from API:")
            print(f"  Total Simulations: {stats.get('total_simulations', 0)}")
            print(f"  Actual RTP: {stats.get('actual_rtp', 0)*100:.2f}%")
            print(f"  Target RTP: {stats.get('avg_configured_rtp', 0)*100:.2f}%")
            print(f"  RTP Difference: {stats.get('rtp_difference', 0)*100:+.2f}%")
    except:
        pass

if __name__ == "__main__":
    main()
