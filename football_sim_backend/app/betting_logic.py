from typing import Tuple, List
from app.models import MarketType, BetResult, BetSelection, ScoreProbability


class BettingEngine:
    def __init__(self, rtp: float = 0.96):
        self.rtp = rtp
    
    def adjust_probabilities_for_bet(
        self,
        score_probabilities: List[ScoreProbability],
        bet_selection: BetSelection,
        rng_value: float
    ) -> List[ScoreProbability]:
        true_odds = self._get_base_odds_for_market(bet_selection.market)
        fair_probability = 1.0 / true_odds if true_odds > 0 else 0.5
        
        win_probability = fair_probability * self.rtp
        
        should_win = rng_value < win_probability
        
        favorable_scores = []
        unfavorable_scores = []
        
        for sp in score_probabilities:
            if self._check_outcome_for_score(bet_selection, sp.home_score, sp.away_score):
                favorable_scores.append(sp)
            else:
                unfavorable_scores.append(sp)
        
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
