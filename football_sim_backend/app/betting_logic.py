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
        house_total_staked: Optional[float] = None,
        house_total_payout: Optional[float] = None
    ) -> List[ScoreProbability]:
        """
        Adjust probabilities to control RTP using GLOBAL house bankroll.
        
        This implements a GLOBAL RTP system using PAYOUT BUDGET:
        - Calculates how much house should pay out based on target RTP
        - Determines win probability based on available budget vs potential payout
        - Ensures exactly 96% of total stakes are paid out globally
        
        Args:
            score_probabilities: List of possible score outcomes
            bet_selection: The bet being placed
            rng_value: Random number 0-1 for determining outcome
            house_total_staked: Total staked across ALL players (for global RTP)
            house_total_payout: Total payout across ALL players (for global RTP)
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
        
        total_favorable_weight = sum(sp.probability for sp in favorable_scores)
        total_weight = sum(sp.probability for sp in score_probabilities)
        base_win_prob = total_favorable_weight / total_weight if total_weight > 0 else 0.5
        
        potential_payout = 0.0
        if bet_selection.stake and bet_selection.odds:
            potential_payout = bet_selection.stake * bet_selection.odds
        
        budget_win_prob = self._calculate_global_rtp_adjustment(
            house_total_staked, 
            house_total_payout,
            bet_selection.stake,
            potential_payout
        )
        
        # Use RTP budget probability more heavily (80%) vs base probability (20%)
        # This ensures RTP control is stronger than natural probabilities
        alpha = 0.2
        adjusted_win_prob = alpha * base_win_prob + (1 - alpha) * budget_win_prob
        adjusted_win_prob = max(0.05, min(0.95, adjusted_win_prob))
        
        should_win = rng_value < adjusted_win_prob
        
        # Use stronger probability adjustments to ensure outcome aligns with RTP requirements
        # Higher boost factor = more deterministic outcomes
        # IMPORTANT: Store raw probabilities first, normalize, THEN create ScoreProbability objects
        # This prevents validation errors from probabilities > 1.0
        if should_win and favorable_scores:
            # Boost favorable scores more aggressively to ensure win
            boost_factor = 5.0  # Increased from 2.0 for stronger control
            adjusted_raw = []  # Store tuples of (score, probability) before normalization
            
            for sp in favorable_scores:
                new_prob = sp.probability * boost_factor
                adjusted_raw.append((sp.home_score, sp.away_score, new_prob))
            
            for sp in unfavorable_scores:
                new_prob = sp.probability * 0.1  # Reduce unfavorable more aggressively
                adjusted_raw.append((sp.home_score, sp.away_score, new_prob))
            
            # Normalize probabilities before creating ScoreProbability objects
            total = sum(prob for _, _, prob in adjusted_raw)
            if total > 0:
                normalized = [
                    ScoreProbability(
                        home_score=home,
                        away_score=away,
                        probability=prob / total
                    ) for home, away, prob in adjusted_raw
                ]
                return normalized
        
        elif not should_win and unfavorable_scores:
            # Boost unfavorable scores to ensure loss
            boost_factor = 5.0  # Increased from 2.0 for stronger control
            adjusted_raw = []  # Store tuples of (score, probability) before normalization
            
            for sp in unfavorable_scores:
                new_prob = sp.probability * boost_factor
                adjusted_raw.append((sp.home_score, sp.away_score, new_prob))
            
            for sp in favorable_scores:
                new_prob = sp.probability * 0.1  # Reduce favorable more aggressively
                adjusted_raw.append((sp.home_score, sp.away_score, new_prob))
            
            # Normalize probabilities before creating ScoreProbability objects
            total = sum(prob for _, _, prob in adjusted_raw)
            if total > 0:
                normalized = [
                    ScoreProbability(
                        home_score=home,
                        away_score=away,
                        probability=prob / total
                    ) for home, away, prob in adjusted_raw
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
    
    def _calculate_global_rtp_adjustment(
        self,
        house_total_staked: Optional[float],
        house_total_payout: Optional[float],
        current_stake: Optional[float],
        potential_payout: Optional[float] = None
    ) -> float:
        """
        Calculate win probability using PAYOUT BUDGET method with stronger RTP control.
        
        This directly controls the house's global RTP by budgeting payouts:
        - Calculate how much the house SHOULD have paid out: target_paid = target_rtp * (total_staked + current_stake)
        - Calculate available budget: budget = target_paid - already_paid_out
        - Calculate allowed win probability: budget / potential_payout
        
        Uses stronger feedback mechanism to keep RTP within ±3% of target.
        
        Example: Target RTP = 96%, Total staked = 100k, Already paid = 98k
        - New bet: $10 stake at 2.0x odds = $20 potential payout
        - Target paid after this bet: 0.96 * (100k + 10) = $96,096
        - Budget available: $96,096 - $98,000 = -$1,904 (negative!)
        - Allowed win prob: -1904 / 20 = -95.2 → clamp to 0.01 (very unlikely to win)
        """
        S = house_total_staked or 0.0
        P = house_total_payout or 0.0
        s = current_stake or 0.0
        
        # If no stake/odds, use base probability
        if potential_payout is None or potential_payout == 0:
            # Still apply RTP feedback even without stake
            if S > 0:
                current_house_rtp = P / S
                rtp_diff = self.rtp - current_house_rtp
                # Stronger feedback: up to 30% adjustment
                feedback = rtp_diff * 0.3
                base_prob = 0.5 + feedback
                return max(0.01, min(0.99, base_prob))
            return 0.50
        
        # Calculate target payout after this bet
        target_paid_after = self.rtp * (S + s)
        
        # Calculate budget (how much we can afford to pay out)
        budget = target_paid_after - P
        
        # Calculate win probability based on budget
        # If budget is negative, we've overpaid - reduce win probability
        # If budget is positive, we can afford wins - increase win probability
        if abs(potential_payout) > 0.0001:
            allowed_win_prob = budget / potential_payout
        else:
            allowed_win_prob = 0.5
        
        # Calculate current RTP for feedback
        current_house_rtp = P / S if S > 0 else self.rtp
        rtp_diff = self.rtp - current_house_rtp
        
        # Stronger feedback mechanism - up to 40% adjustment
        # If RTP is too high (house losing money), reduce win probability more aggressively
        # If RTP is too low (house keeping too much), increase win probability more aggressively
        if abs(rtp_diff) > 0.03:  # More than 3% off target
            feedback_strength = 0.5  # 50% feedback for large deviations
        elif abs(rtp_diff) > 0.01:  # 1-3% off target
            feedback_strength = 0.3  # 30% feedback for medium deviations
        else:
            feedback_strength = 0.15  # 15% feedback for small deviations
        
        feedback = rtp_diff * feedback_strength
        
        # Combine budget-based probability with RTP feedback
        # Weight budget more heavily (70%) but use feedback to fine-tune (30%)
        final_prob = 0.7 * allowed_win_prob + 0.3 * (0.5 + feedback)
        
        # Clamp to reasonable bounds with tighter limits
        final_prob = max(0.05, min(0.95, final_prob))
        
        return final_prob
    
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
