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
    home_score: int
    away_score: int
    probability: float = Field(ge=0.0, le=1.0)


class BetSelection(BaseModel):
    market: MarketType
    outcome: str
    stake: Optional[float] = Field(default=None, gt=0, description="Amount wagered on this bet")
    odds: Optional[float] = Field(default=None, gt=1.0, description="Payout multiplier if bet wins")


class MatchSimulationRequest(BaseModel):
    user_id: str = Field(description="Unique identifier for the player/user")
    home_team: str
    away_team: str
    score_probabilities: List[ScoreProbability]
    bet_slip: List[BetSelection] = Field(min_length=1, description="List of bets placed")
    volatility: str = Field(default="medium", description="low, medium, or high")
    seed: Optional[int] = None


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
    rtp: float = Field(ge=0.0, le=1.0, description="Return to Player percentage")


class Market(BaseModel):
    market_type: MarketType
    name: str
    description: str
    possible_outcomes: List[str]
    example: str
