import random
import hashlib
import time
from typing import List, Tuple


class FootballRNG:
    def __init__(self, seed: int = None):
        if seed is None:
            seed = int(time.time() * 1000000) % (2**32)
        
        self.seed = seed
        self.rng = random.Random(seed)
    
    def get_seed(self) -> int:
        return self.seed
    
    def next_random(self) -> float:
        return self.rng.random()
    
    def next_int(self, min_val: int, max_val: int) -> int:
        return self.rng.randint(min_val, max_val)
    
    def weighted_choice(self, choices: List[Tuple[any, float]]) -> any:
        total = sum(weight for _, weight in choices)
        r = self.next_random() * total
        
        cumulative = 0
        for choice, weight in choices:
            cumulative += weight
            if r <= cumulative:
                return choice
        
        return choices[-1][0]
    
    def deterministic_hash_seed(self, data: str) -> int:
        hash_obj = hashlib.sha256(data.encode())
        hash_hex = hash_obj.hexdigest()
        seed = int(hash_hex[:8], 16)
        return seed


class ProbabilityEngine:
    def __init__(self, rng: FootballRNG, rtp: float = 0.96, volatility: str = "medium"):
        self.rng = rng
        self.rtp = rtp
        self.volatility = volatility
    
    def normalize_probabilities(self, probabilities: List[Tuple[any, float]]) -> List[Tuple[any, float]]:
        total = sum(prob for _, prob in probabilities)
        if total == 0:
            return probabilities
        
        return [(choice, prob / total) for choice, prob in probabilities]
    
    def select_final_score(self, score_probabilities: List[Tuple[Tuple[int, int], float]]) -> Tuple[int, int]:
        normalized = self.normalize_probabilities(score_probabilities)
        
        if self.volatility == "high":
            weighted_probs = []
            for score, prob in normalized:
                total_goals = score[0] + score[1]
                if total_goals >= 4:
                    weighted_probs.append((score, prob * 1.5))
                else:
                    weighted_probs.append((score, prob * 0.7))
            normalized = self.normalize_probabilities(weighted_probs)
        elif self.volatility == "low":
            weighted_probs = []
            for score, prob in normalized:
                total_goals = score[0] + score[1]
                if total_goals <= 2:
                    weighted_probs.append((score, prob * 1.3))
                else:
                    weighted_probs.append((score, prob * 0.8))
            normalized = self.normalize_probabilities(weighted_probs)
        
        return self.rng.weighted_choice(normalized)
    
    def calculate_event_probabilities(self, minute: int, target_goals: int, goals_scored: int) -> dict:
        remaining_minutes = 90 - minute
        remaining_goals = target_goals - goals_scored
        
        if remaining_minutes <= 0:
            return {
                'goal': 0.0,
                'shot': 0.1,
                'pass': 0.4,
                'corner': 0.1,
                'foul': 0.2,
                'offside': 0.1,
                'other': 0.1
            }
        
        base_goal_prob = remaining_goals / max(remaining_minutes, 1) if remaining_goals > 0 else 0.01
        base_goal_prob = min(base_goal_prob, 0.15)
        
        if minute < 15 or minute > 75:
            base_goal_prob *= 1.3
        
        return {
            'goal': base_goal_prob,
            'shot': 0.15,
            'pass': 0.35,
            'corner': 0.10,
            'foul': 0.15,
            'offside': 0.08,
            'other': 0.07
        }
