import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

DATABASE_PATH = "simulations.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                home_score INTEGER NOT NULL,
                away_score INTEGER NOT NULL,
                bet_slip_won BOOLEAN NOT NULL,
                total_stake REAL,
                total_payout REAL,
                total_profit REAL,
                configured_rtp REAL NOT NULL,
                seed INTEGER,
                volatility TEXT NOT NULL,
                total_events INTEGER NOT NULL,
                number_of_bets INTEGER NOT NULL,
                bet_results TEXT NOT NULL,
                events TEXT NOT NULL,
                match_stats TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON simulations(created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_home_team ON simulations(home_team)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_away_team ON simulations(away_team)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON simulations(user_id)
        """)
        
        conn.commit()

def save_simulation(simulation_data: Dict[str, Any]) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO simulations (
                user_id, home_team, away_team, home_score, away_score,
                bet_slip_won, total_stake, total_payout, total_profit,
                configured_rtp, seed, volatility, total_events, number_of_bets,
                bet_results, events, match_stats
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            simulation_data['user_id'],
            simulation_data['home_team'],
            simulation_data['away_team'],
            simulation_data['home_score'],
            simulation_data['away_score'],
            simulation_data['bet_slip_won'],
            simulation_data['total_stake'],
            simulation_data['total_payout'],
            simulation_data['total_profit'],
            simulation_data['configured_rtp'],
            simulation_data['seed'],
            simulation_data['volatility'],
            simulation_data['total_events'],
            simulation_data['number_of_bets'],
            json.dumps(simulation_data['bet_results']),
            json.dumps(simulation_data['events']),
            json.dumps(simulation_data['match_stats'])
        ))
        
        conn.commit()
        return cursor.lastrowid

def get_simulations(
    limit: int = 50,
    offset: int = 0,
    team: Optional[str] = None,
    bet_slip_won: Optional[bool] = None,
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM simulations WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if team:
            query += " AND (home_team LIKE ? OR away_team LIKE ?)"
            search_term = f"%{team}%"
            params.extend([search_term, search_term])
        
        if bet_slip_won is not None:
            query += " AND bet_slip_won = ?"
            params.append(bet_slip_won)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        simulations = []
        for row in rows:
            simulations.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'home_team': row['home_team'],
                'away_team': row['away_team'],
                'home_score': row['home_score'],
                'away_score': row['away_score'],
                'bet_slip_won': bool(row['bet_slip_won']),
                'total_stake': row['total_stake'],
                'total_payout': row['total_payout'],
                'total_profit': row['total_profit'],
                'configured_rtp': row['configured_rtp'],
                'seed': row['seed'],
                'volatility': row['volatility'],
                'total_events': row['total_events'],
                'number_of_bets': row['number_of_bets'],
                'bet_results': json.loads(row['bet_results']),
                'events': json.loads(row['events']),
                'match_stats': json.loads(row['match_stats']),
                'created_at': row['created_at']
            })
        
        return simulations

def get_simulation_stats() -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_simulations,
                SUM(CASE WHEN bet_slip_won = 1 THEN 1 ELSE 0 END) as won_slips,
                SUM(CASE WHEN bet_slip_won = 0 THEN 1 ELSE 0 END) as lost_slips,
                SUM(total_stake) as total_staked,
                SUM(total_payout) as total_paid_out,
                SUM(total_profit) as total_player_profit,
                SUM(number_of_bets) as total_bets,
                AVG(configured_rtp) as avg_configured_rtp
            FROM simulations
            WHERE total_stake IS NOT NULL
        """)
        
        row = cursor.fetchone()
        
        total_staked = float(row['total_staked']) if row['total_staked'] else 0
        total_paid_out = float(row['total_paid_out']) if row['total_paid_out'] else 0
        
        actual_rtp = (total_paid_out / total_staked) if total_staked > 0 else 0
        house_profit = total_staked - total_paid_out
        
        return {
            'total_simulations': row['total_simulations'],
            'won_slips': row['won_slips'],
            'lost_slips': row['lost_slips'],
            'total_bets': row['total_bets'],
            'total_staked': total_staked,
            'total_paid_out': total_paid_out,
            'house_profit': house_profit,
            'total_player_profit': float(row['total_player_profit']) if row['total_player_profit'] else 0,
            'actual_rtp': actual_rtp,
            'avg_configured_rtp': float(row['avg_configured_rtp']) if row['avg_configured_rtp'] else 0,
            'rtp_difference': actual_rtp - (float(row['avg_configured_rtp']) if row['avg_configured_rtp'] else 0)
        }

def get_rtp_trends(limit: int = 100) -> List[Dict[str, Any]]:
    """Calculate RTP trends over time with rolling windows"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                created_at,
                configured_rtp,
                total_stake,
                total_payout,
                bet_slip_won
            FROM simulations
            WHERE total_stake IS NOT NULL
            ORDER BY created_at ASC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        trends = []
        cumulative_stake = 0
        cumulative_payout = 0
        
        for idx, row in enumerate(rows):
            cumulative_stake += float(row['total_stake']) if row['total_stake'] else 0
            cumulative_payout += float(row['total_payout']) if row['total_payout'] else 0
            
            actual_rtp = (cumulative_payout / cumulative_stake) if cumulative_stake > 0 else 0
            
            window_size = min(10, idx + 1)
            window_start = max(0, idx - window_size + 1)
            window_stake = sum(float(rows[i]['total_stake']) if rows[i]['total_stake'] else 0 
                             for i in range(window_start, idx + 1))
            window_payout = sum(float(rows[i]['total_payout']) if rows[i]['total_payout'] else 0 
                              for i in range(window_start, idx + 1))
            
            window_rtp = (window_payout / window_stake) if window_stake > 0 else 0
            
            trends.append({
                'simulation_number': idx + 1,
                'created_at': row['created_at'],
                'configured_rtp': float(row['configured_rtp']),
                'cumulative_actual_rtp': actual_rtp,
                'rolling_window_rtp': window_rtp,
                'cumulative_stake': cumulative_stake,
                'cumulative_payout': cumulative_payout,
                'bet_slip_won': bool(row['bet_slip_won'])
            })
        
        return trends

def get_player_stats(user_id: str) -> Dict[str, Any]:
    """Get statistics for a specific player"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_simulations,
                SUM(CASE WHEN bet_slip_won = 1 THEN 1 ELSE 0 END) as won_slips,
                SUM(CASE WHEN bet_slip_won = 0 THEN 1 ELSE 0 END) as lost_slips,
                SUM(total_stake) as total_staked,
                SUM(total_payout) as total_paid_out,
                SUM(total_profit) as total_player_profit,
                SUM(number_of_bets) as total_bets,
                AVG(configured_rtp) as avg_configured_rtp
            FROM simulations
            WHERE user_id = ? AND total_stake IS NOT NULL
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if not row or row['total_simulations'] == 0:
            return {
                'user_id': user_id,
                'total_simulations': 0,
                'won_slips': 0,
                'lost_slips': 0,
                'total_bets': 0,
                'total_staked': 0,
                'total_paid_out': 0,
                'house_profit': 0,
                'total_player_profit': 0,
                'actual_rtp': 0,
                'avg_configured_rtp': 0,
                'rtp_difference': 0
            }
        
        total_staked = float(row['total_staked']) if row['total_staked'] else 0
        total_paid_out = float(row['total_paid_out']) if row['total_paid_out'] else 0
        
        actual_rtp = (total_paid_out / total_staked) if total_staked > 0 else 0
        house_profit = total_staked - total_paid_out
        avg_configured_rtp = float(row['avg_configured_rtp']) if row['avg_configured_rtp'] else 0
        
        return {
            'user_id': user_id,
            'total_simulations': row['total_simulations'],
            'won_slips': row['won_slips'],
            'lost_slips': row['lost_slips'],
            'total_bets': row['total_bets'],
            'total_staked': total_staked,
            'total_paid_out': total_paid_out,
            'house_profit': house_profit,
            'total_player_profit': float(row['total_player_profit']) if row['total_player_profit'] else 0,
            'actual_rtp': actual_rtp,
            'avg_configured_rtp': avg_configured_rtp,
            'rtp_difference': actual_rtp - avg_configured_rtp
        }

def get_all_players() -> List[Dict[str, Any]]:
    """Get list of all players with their basic stats"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                user_id,
                COUNT(*) as total_simulations,
                SUM(CASE WHEN bet_slip_won = 1 THEN 1 ELSE 0 END) as won_slips,
                SUM(total_stake) as total_staked,
                SUM(total_payout) as total_paid_out,
                MAX(created_at) as last_simulation
            FROM simulations
            WHERE total_stake IS NOT NULL
            GROUP BY user_id
            ORDER BY last_simulation DESC
        """)
        
        rows = cursor.fetchall()
        
        players = []
        for row in rows:
            total_staked = float(row['total_staked']) if row['total_staked'] else 0
            total_paid_out = float(row['total_paid_out']) if row['total_paid_out'] else 0
            actual_rtp = (total_paid_out / total_staked) if total_staked > 0 else 0
            
            players.append({
                'user_id': row['user_id'],
                'total_simulations': row['total_simulations'],
                'won_slips': row['won_slips'],
                'total_staked': total_staked,
                'total_paid_out': total_paid_out,
                'actual_rtp': actual_rtp,
                'last_simulation': row['last_simulation']
            })
        
        return players

def get_count(team: Optional[str] = None, bet_slip_won: Optional[bool] = None, user_id: Optional[str] = None) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) as count FROM simulations WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if team:
            query += " AND (home_team LIKE ? OR away_team LIKE ?)"
            search_term = f"%{team}%"
            params.extend([search_term, search_term])
        
        if bet_slip_won is not None:
            query += " AND bet_slip_won = ?"
            params.append(bet_slip_won)
        
        cursor.execute(query, params)
        return cursor.fetchone()['count']

init_db()
