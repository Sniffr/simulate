from typing import Tuple, List, Optional
from app.models import MarketType, BetResult, BetSelection, ScoreProbability


class BettingEngine:
    def __init__(self, rtp: float = 0.96, rtp_window_size: int = 100):
        """
        Initialize betting engine with RTP control.
        
        Args:
            rtp: Target RTP (Return to Player) - typically 0.92 to 0.98
            rtp_window_size: Number of bets over which to balance RTP (default 100)
        """
        self.rtp = rtp
        self.rtp_window_size = rtp_window_size
    
    def adjust_probabilities_for_bet(
        self,
        score_probabilities: List[ScoreProbability],
        bet_selection: BetSelection,
        rng_value: float,
        player_total_staked: Optional[float] = None,
        player_total_payout: Optional[float] = None
    ) -> List[ScoreProbability]:
        """
        Adjust probabilities to control RTP using pooled RTP balancing.
        
        This implements a balanced RTP system:
        - If player's current RTP is below target, increase win probability
        - If player's current RTP is above target, decrease win probability
        - This ensures RTP converges to target over many bets
        
        Args:
            score_probabilities: List of possible score outcomes
            bet_selection: The bet being placed
            rng_value: Random number 0-1 for determining outcome
            player_total_staked: Player's total staked amount (for RTP balancing)
            player_total_payout: Player's total payout amount (for RTP balancing)
        """
        favorable_scores = []
        unfavorable_scores = []
        
        for sp in score_probabilities:
            if self._check_outcome_for_score(bet_selection, sp.home_score, sp.away_score):
                favorable_scores.append(sp)
            else:
                unfavorable_scores.append(sp)
        
        if not favorable_scores or not unfavorable_scores:
            return score_probabilities
        
        total_favorable_prob = sum(sp.probability for sp in favorable_scores)
        
        rtp_adjustment = self._calculate_rtp_adjustment(
            player_total_staked, 
            player_total_payout,
            bet_selection.stake
        )
        
        # Apply RTP adjustment to win probability
        adjusted_win_prob = total_favorable_prob * rtp_adjustment
        adjusted_win_prob = max(0.0, min(1.0, adjusted_win_prob))
        
        should_win = rng_value < adjusted_win_prob
        
        if should_win and favorable_scores:
            total_favorable = sum(sp.probability for sp in favorable_scores)
            total_unfavorable = sum(sp.probability for sp in unfavorable_scores)
            
            boost_factor = 2.0
            adjusted = []
            for sp in favorable_scores:
                new_prob = sp.probability * boost_factor
                adjusted.append(ScoreProbability(
                    home_score=sp.home_score,
                    away_score=sp.away_score,
                    probability=new_prob
                ))
            for sp in unfavorable_scores:
                new_prob = sp.probability * 0.5
                adjusted.append(ScoreProbability(
                    home_score=sp.home_score,
                    away_score=sp.away_score,
                    probability=new_prob
                ))
            
            total = sum(sp.probability for sp in adjusted)
            normalized = [
                ScoreProbability(
                    home_score=sp.home_score,
                    away_score=sp.away_score,
                    probability=sp.probability / total
                ) for sp in adjusted
            ]
            return normalized
        
        elif not should_win and unfavorable_scores:
            boost_factor = 2.0
            adjusted = []
            for sp in unfavorable_scores:
                new_prob = sp.probability * boost_factor
                adjusted.append(ScoreProbability(
                    home_score=sp.home_score,
                    away_score=sp.away_score,
                    probability=new_prob
                ))
            for sp in favorable_scores:
                new_prob = sp.probability * 0.5
                adjusted.append(ScoreProbability(
                    home_score=sp.home_score,
                    away_score=sp.away_score,
                    probability=new_prob
                ))
            
            total = sum(sp.probability for sp in adjusted)
            normalized = [
                ScoreProbability(
                    home_score=sp.home_score,
                    away_score=sp.away_score,
                    probability=sp.probability / total
                ) for sp in adjusted
            ]
            return normalized
        
        return score_probabilities
    
    def evaluate_bet(
        self,
        bet_selection: BetSelection,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int
    ) -> BetResult:
        outcome_occurred = self._check_outcome_for_score(
            bet_selection, home_score, away_score
        )
        
        bet_won = outcome_occurred
        
        has_stake_and_odds = bet_selection.stake is not None and bet_selection.odds is not None
        
        if has_stake_and_odds:
            payout = bet_selection.stake * bet_selection.odds if bet_won else 0.0
            profit = payout - bet_selection.stake
        else:
            payout = None
            profit = None
        
        explanation = self._generate_explanation(
            bet_selection, home_team, away_team, home_score, away_score,
            outcome_occurred, bet_won
        )
        
        return BetResult(
            market=bet_selection.market,
            outcome=bet_selection.outcome,
            stake=bet_selection.stake,
            odds=bet_selection.odds,
            won=bet_won,
            outcome_occurred=outcome_occurred,
            payout=payout,
            profit=profit,
            explanation=explanation
        )
    
    def _calculate_rtp_adjustment(
        self,
        player_total_staked: Optional[float],
        player_total_payout: Optional[float],
        current_stake: Optional[float]
    ) -> float:
        """
        Calculate RTP adjustment factor based on player's historical performance.
        
        Returns a multiplier to apply to win probability:
        - If player RTP < target RTP: return value > 1.0 (increase win chance)
        - If player RTP > target RTP: return value < 1.0 (decrease win chance)
        - If no history: return self.rtp (normal RTP)
        """
        if player_total_staked is None or player_total_payout is None:
            return self.rtp
        
        if player_total_staked < 10:
            return self.rtp
        
        current_rtp = player_total_payout / player_total_staked if player_total_staked > 0 else 0
        
        rtp_diff = self.rtp - current_rtp
        
        adjustment_strength = 0.3
        
        adjustment = 1.0 + (rtp_diff * adjustment_strength)
        
        adjustment = max(0.5, min(1.5, adjustment))
        
        return adjustment
    
    def _check_outcome_for_score(
        self,
        bet_selection: BetSelection,
        home_score: int,
        away_score: int
    ) -> bool:
        market = bet_selection.market
        outcome = bet_selection.outcome.lower()
        
        if market == MarketType.MATCH_RESULT_1X2:
            if outcome == "1" or outcome == "home":
                return home_score > away_score
            elif outcome == "x" or outcome == "draw":
                return home_score == away_score
            elif outcome == "2" or outcome == "away":
                return home_score < away_score
        
        elif market == MarketType.OVER_UNDER:
            total_goals = home_score + away_score
            try:
                threshold = float(outcome.replace("over_", "").replace("under_", ""))
                if "over" in outcome:
                    return total_goals > threshold
                elif "under" in outcome:
                    return total_goals < threshold
            except:
                pass
        
        elif market == MarketType.BOTH_TEAMS_TO_SCORE:
            if outcome == "yes":
                return home_score > 0 and away_score > 0
            elif outcome == "no":
                return home_score == 0 or away_score == 0
        
        elif market == MarketType.CORRECT_SCORE:
            try:
                expected_home, expected_away = outcome.split("-")
                return int(expected_home) == home_score and int(expected_away) == away_score
            except:
                pass
        
        return False
    
    def _get_base_odds_for_market(
        self,
        market: MarketType
    ) -> float:
        if market == MarketType.MATCH_RESULT_1X2:
            return 2.5
        elif market == MarketType.OVER_UNDER:
            return 1.9
        elif market == MarketType.BOTH_TEAMS_TO_SCORE:
            return 1.8
        elif market == MarketType.CORRECT_SCORE:
            return 10.0
        return 2.0
    
    def _generate_explanation(
        self,
        bet_selection: BetSelection,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int,
        outcome_occurred: bool,
        bet_won: bool
    ) -> str:
        result_str = f"{home_team} {home_score} - {away_score} {away_team}"
        market_name = bet_selection.market.value
        outcome_name = bet_selection.outcome
        
        has_stake_and_odds = bet_selection.stake is not None and bet_selection.odds is not None
        
        if bet_won:
            if has_stake_and_odds:
                payout = bet_selection.stake * bet_selection.odds
                profit = payout - bet_selection.stake
                return (f"✅ WON! {market_name}: {outcome_name}. Score: {result_str}. "
                       f"Stake: ${bet_selection.stake:.2f} @ {bet_selection.odds:.2f}x → Payout: ${payout:.2f} (Profit: ${profit:.2f})")
            else:
                return f"✅ WON! {market_name}: {outcome_name}. Score: {result_str}."
        else:
            if has_stake_and_odds:
                return (f"❌ LOST. {market_name}: {outcome_name}. Score: {result_str}. "
                       f"Stake: ${bet_selection.stake:.2f} lost.")
            else:
                return f"❌ LOST. {market_name}: {outcome_name}. Score: {result_str}."


def get_supported_markets():
    return [
        {
            "market_type": MarketType.MATCH_RESULT_1X2,
            "name": "Match Result (1X2)",
            "description": "Predict the final result: Home win (1), Draw (X), or Away win (2)",
            "possible_outcomes": ["1", "X", "2", "home", "draw", "away"],
            "example": "1"
        },
        {
            "market_type": MarketType.OVER_UNDER,
            "name": "Over/Under Goals",
            "description": "Predict if total goals will be over or under a threshold",
            "possible_outcomes": ["over_0.5", "under_0.5", "over_1.5", "under_1.5", "over_2.5", "under_2.5", "over_3.5", "under_3.5"],
            "example": "over_2.5"
        },
        {
            "market_type": MarketType.BOTH_TEAMS_TO_SCORE,
            "name": "Both Teams To Score",
            "description": "Predict if both teams will score at least one goal",
            "possible_outcomes": ["yes", "no"],
            "example": "yes"
        },
        {
            "market_type": MarketType.CORRECT_SCORE,
            "name": "Correct Score",
            "description": "Predict the exact final score",
            "possible_outcomes": ["0-0", "1-0", "2-0", "1-1", "2-1", "3-1", "0-1", "1-2", "2-2", "3-2", "etc."],
            "example": "2-1"
        }
    ]
