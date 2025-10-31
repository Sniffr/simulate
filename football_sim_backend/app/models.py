from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum


class MarketType(str, Enum):
    MATCH_RESULT_1X2 = "1X2"
    OVER_UNDER = "over_under"
    BOTH_TEAMS_TO_SCORE = "both_teams_to_score"
    CORRECT_SCORE = "correct_score"


class EventType(str, Enum):
    KICKOFF = "kickoff"
    PASS = "pass"
    SHOT = "shot"
    GOAL = "goal"
    CORNER = "corner"
    FOUL = "foul"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"
    OFFSIDE = "offside"
    SAVE = "save"
    MISS = "miss"
    HALFTIME = "halftime"
    FULLTIME = "fulltime"


class MatchEvent(BaseModel):
    minute: int
    event_type: EventType
    team: str
    description: str
    player: Optional[str] = None


class ScoreProbability(BaseModel):
    home_score: int = Field(example=2)
    away_score: int = Field(example=1)
    probability: float = Field(ge=0.0, le=1.0, example=0.18)


class BetSelection(BaseModel):
    market: MarketType = Field(example="1X2")
    outcome: str = Field(example="1")
    stake: Optional[float] = Field(default=None, gt=0, description="Amount wagered on this bet", example=20.0)
    odds: Optional[float] = Field(default=None, gt=1.0, description="Payout multiplier if bet wins", example=2.1)


class MatchSimulationRequest(BaseModel):
    user_id: str = Field(description="Unique identifier for the player/user", example="player123")
    home_team: str = Field(example="Manchester United")
    away_team: str = Field(example="Arsenal")
    score_probabilities: List[ScoreProbability] = Field(
        description="List of possible score outcomes with probabilities (can sum to more or less than 1.0)",
        example=[
            {"home_score": 1, "away_score": 0, "probability": 0.15},
            {"home_score": 2, "away_score": 1, "probability": 0.18},
            {"home_score": 1, "away_score": 1, "probability": 0.15},
            {"home_score": 0, "away_score": 0, "probability": 0.10},
            {"home_score": 0, "away_score": 1, "probability": 0.10}
        ]
    )
    bet_slip: List[BetSelection] = Field(
        min_length=1, 
        description="List of bets placed (all must win for bet_slip_won=true)",
        example=[
            {"market": "1X2", "outcome": "1", "stake": 20.0, "odds": 2.1},
            {"market": "over_under", "outcome": "over_2.5"}
        ]
    )
    volatility: str = Field(default="medium", description="low, medium, or high", example="medium")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducible results", example=12345)


class BetResult(BaseModel):
    market: MarketType
    outcome: str
    stake: Optional[float] = None
    odds: Optional[float] = None
    won: bool
    outcome_occurred: bool
    payout: Optional[float] = None
    profit: Optional[float] = None
    explanation: str


class MatchSimulationResponse(BaseModel):
    home_team: str
    away_team: str
    final_score: Dict[str, int]
    bet_results: List[BetResult]
    bet_slip_won: bool
    total_stake: Optional[float] = None
    total_payout: Optional[float] = None
    total_profit: Optional[float] = None
    events: List[MatchEvent]
    match_stats: Dict[str, Any]
    simulation_metadata: Dict[str, Any]


class RTPConfig(BaseModel):
    rtp: float = Field(ge=0.0, le=1.0, description="Return to Player percentage (0.0-1.0, e.g., 0.96 = 96%)", example=0.96)


class Market(BaseModel):
    market_type: MarketType
    name: str
    description: str
    possible_outcomes: List[str]
    example: str
