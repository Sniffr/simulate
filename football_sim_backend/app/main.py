from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg
from typing import Optional
from app.models import MatchSimulationRequest, MatchSimulationResponse, RTPConfig, Market
from app.match_simulator import FootballMatchSimulator
from app.betting_logic import BettingEngine, get_supported_markets
from app.database import save_simulation, get_simulations, get_simulation_stats, get_rtp_trends, get_count, get_player_stats, get_all_players

app = FastAPI(
    title="Football Match Simulator API",
    description="Simulates football matches with betting outcomes based on RTP and probability inputs",
    version="2.0.0"
)

current_rtp = 0.96

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/rtp", response_model=RTPConfig)
async def get_rtp():
    global current_rtp
    return RTPConfig(rtp=current_rtp)


@app.post("/api/rtp", response_model=RTPConfig)
async def set_rtp(config: RTPConfig):
    global current_rtp
    current_rtp = config.rtp
    return RTPConfig(rtp=current_rtp)


@app.get("/api/markets")
async def get_markets():
    return {
        "markets": get_supported_markets(),
        "description": "Supported betting markets for football match simulation"
    }


@app.post("/api/simulate", response_model=MatchSimulationResponse)
async def simulate_match(request: MatchSimulationRequest):
    try:
        global current_rtp
        
        total_probability = sum(sp.probability for sp in request.score_probabilities)
        if total_probability <= 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Score probabilities must sum to a positive number (currently {total_probability})"
            )
        
        betting_engine = BettingEngine(rtp=current_rtp)
        
        from app.rng_engine import FootballRNG
        temp_rng = FootballRNG(request.seed)
        
        adjusted_probabilities = request.score_probabilities
        for bet in request.bet_slip:
            rng_value = temp_rng.next_random()
            adjusted_probabilities = betting_engine.adjust_probabilities_for_bet(
                score_probabilities=adjusted_probabilities,
                bet_selection=bet,
                rng_value=rng_value
            )
        
        simulator = FootballMatchSimulator(
            home_team=request.home_team,
            away_team=request.away_team,
            score_probabilities=adjusted_probabilities,
            rtp=current_rtp,
            volatility=request.volatility,
            seed=request.seed
        )
        
        events, stats = simulator.simulate_match()
        
        bet_results = []
        for bet in request.bet_slip:
            result = betting_engine.evaluate_bet(
                bet_selection=bet,
                home_team=request.home_team,
                away_team=request.away_team,
                home_score=simulator.home_score,
                away_score=simulator.away_score
            )
            bet_results.append(result)
        
        bet_slip_won = all(result.won for result in bet_results)
        
        any_bet_has_stake = any(bet.stake is not None for bet in request.bet_slip)
        
        if any_bet_has_stake:
            total_stake = sum(bet.stake for bet in request.bet_slip if bet.stake is not None)
            total_payout = sum(result.payout for result in bet_results if result.payout is not None)
            total_profit = total_payout - total_stake
        else:
            total_stake = None
            total_payout = None
            total_profit = None
        
        response = MatchSimulationResponse(
            home_team=request.home_team,
            away_team=request.away_team,
            final_score={
                request.home_team: simulator.home_score,
                request.away_team: simulator.away_score
            },
            bet_results=bet_results,
            bet_slip_won=bet_slip_won,
            total_stake=total_stake,
            total_payout=total_payout,
            total_profit=total_profit,
            events=events,
            match_stats=stats,
            simulation_metadata={
                "rtp": current_rtp,
                "volatility": request.volatility,
                "seed": simulator.rng.get_seed(),
                "total_events": len(events),
                "number_of_bets": len(request.bet_slip)
            }
        )
        
        simulation_data = {
            'user_id': request.user_id,
            'home_team': request.home_team,
            'away_team': request.away_team,
            'home_score': simulator.home_score,
            'away_score': simulator.away_score,
            'bet_slip_won': bet_slip_won,
            'total_stake': total_stake,
            'total_payout': total_payout,
            'total_profit': total_profit,
            'configured_rtp': current_rtp,
            'seed': simulator.rng.get_seed(),
            'volatility': request.volatility,
            'total_events': len(events),
            'number_of_bets': len(request.bet_slip),
            'bet_results': [result.dict() for result in bet_results],
            'events': [event.dict() for event in events],
            'match_stats': stats
        }
        save_simulation(simulation_data)
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_simulation_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    team: Optional[str] = Query(None, description="Filter by team name"),
    won: Optional[bool] = Query(None, description="Filter by bet slip won/lost"),
    user_id: Optional[str] = Query(None, description="Filter by user/player ID")
):
    """Get historical simulations with pagination and filtering"""
    simulations = get_simulations(limit=limit, offset=offset, team=team, bet_slip_won=won, user_id=user_id)
    total_count = get_count(team=team, bet_slip_won=won, user_id=user_id)
    
    return {
        "simulations": simulations,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total_count,
            "has_more": offset + limit < total_count
        }
    }


@app.get("/api/stats")
async def get_stats():
    """Get overall simulation statistics including RTP analysis"""
    return get_simulation_stats()


@app.get("/api/rtp-trends")
async def get_rtp_trend_data(
    limit: int = Query(100, ge=10, le=500, description="Number of recent simulations to analyze")
):
    """Get RTP trends over time with cumulative and rolling window calculations"""
    return {
        "trends": get_rtp_trends(limit=limit),
        "description": "RTP trends showing configured vs actual RTP over time"
    }


@app.get("/api/players")
async def get_players():
    """Get list of all players with their statistics"""
    return {
        "players": get_all_players(),
        "description": "All players who have placed bets with their stats"
    }


@app.get("/api/players/{user_id}/stats")
async def get_player_statistics(user_id: str):
    """Get detailed statistics for a specific player"""
    stats = get_player_stats(user_id)
    
    if stats['total_simulations'] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No simulations found for player {user_id}"
        )
    
    return stats


@app.get("/api/example")
async def get_example_request():
    return {
        "single_bet": {
            "user_id": "player123",
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
            "bet_slip": [
                {
                    "market": "1X2",
                    "outcome": "1",
                    "stake": 10.0,
                    "odds": 2.5
                }
            ],
            "volatility": "medium"
        },
        "multiple_bets": {
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
        },
        "description": "POST any of these examples to /api/simulate. Set RTP first using POST /api/rtp"
    }
