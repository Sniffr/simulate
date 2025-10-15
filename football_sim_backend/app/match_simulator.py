from typing import List, Tuple, Dict
from app.models import MatchEvent, EventType, ScoreProbability
from app.rng_engine import FootballRNG, ProbabilityEngine
import random


class FootballMatchSimulator:
    def __init__(self, home_team: str, away_team: str, 
                 score_probabilities: List[ScoreProbability],
                 rtp: float = 0.96, volatility: str = "medium", seed: int = None):
        self.home_team = home_team
        self.away_team = away_team
        self.score_probabilities = score_probabilities
        self.rtp = rtp
        self.volatility = volatility
        
        self.rng = FootballRNG(seed)
        self.prob_engine = ProbabilityEngine(self.rng, rtp, volatility)
        
        self.events: List[MatchEvent] = []
        self.home_score = 0
        self.away_score = 0
        self.home_goals_target = 0
        self.away_goals_target = 0
        
        self.player_names = self._generate_player_names()
    
    def _generate_player_names(self) -> Dict[str, List[str]]:
        home_forwards = [f"{self.home_team[0]}. Player {i}" for i in range(1, 4)]
        home_midfielders = [f"{self.home_team[0]}. Player {i}" for i in range(4, 8)]
        home_defenders = [f"{self.home_team[0]}. Player {i}" for i in range(8, 12)]
        
        away_forwards = [f"{self.away_team[0]}. Player {i}" for i in range(1, 4)]
        away_midfielders = [f"{self.away_team[0]}. Player {i}" for i in range(4, 8)]
        away_defenders = [f"{self.away_team[0]}. Player {i}" for i in range(8, 12)]
        
        return {
            'home_forwards': home_forwards,
            'home_midfielders': home_midfielders,
            'home_defenders': home_defenders,
            'away_forwards': away_forwards,
            'away_midfielders': away_midfielders,
            'away_defenders': away_defenders
        }
    
    def _get_random_player(self, team: str, position_bias: str = "forward") -> str:
        if team == self.home_team:
            if position_bias == "forward":
                pool = self.player_names['home_forwards'] + self.player_names['home_midfielders']
            elif position_bias == "midfielder":
                pool = self.player_names['home_midfielders']
            else:
                pool = self.player_names['home_defenders']
        else:
            if position_bias == "forward":
                pool = self.player_names['away_forwards'] + self.player_names['away_midfielders']
            elif position_bias == "midfielder":
                pool = self.player_names['away_midfielders']
            else:
                pool = self.player_names['away_defenders']
        
        return random.choice(pool)
    
    def simulate_match(self) -> Tuple[List[MatchEvent], Dict]:
        score_probs = [(
            (sp.home_score, sp.away_score), 
            sp.probability
        ) for sp in self.score_probabilities]
        
        final_score = self.prob_engine.select_final_score(score_probs)
        self.home_goals_target, self.away_goals_target = final_score
        
        self.events.append(MatchEvent(
            minute=0,
            event_type=EventType.KICKOFF,
            team=self.home_team,
            description=f"Match kicks off at the stadium! {self.home_team} vs {self.away_team}"
        ))
        
        total_goals_needed = self.home_goals_target + self.away_goals_target
        goals_scheduled = self._schedule_goals(total_goals_needed)
        
        current_minute = 1
        goal_index = 0
        
        while current_minute <= 90:
            if goal_index < len(goals_scheduled) and current_minute >= goals_scheduled[goal_index]['minute']:
                self._create_goal_sequence(
                    goals_scheduled[goal_index]['minute'],
                    goals_scheduled[goal_index]['team']
                )
                goal_index += 1
                current_minute = goals_scheduled[goal_index - 1]['minute'] + 1
            else:
                if self.rng.next_random() < 0.3:
                    self._create_regular_event(current_minute)
                
                current_minute += self.rng.next_int(1, 3)
            
            if current_minute == 45:
                self.events.append(MatchEvent(
                    minute=45,
                    event_type=EventType.HALFTIME,
                    team="",
                    description=f"Half-time: {self.home_team} {self.home_score} - {self.away_score} {self.away_team}"
                ))
                current_minute = 46
        
        self.events.append(MatchEvent(
            minute=90,
            event_type=EventType.FULLTIME,
            team="",
            description=f"Full-time: {self.home_team} {self.home_score} - {self.away_score} {self.away_team}"
        ))
        
        stats = self._calculate_match_stats()
        
        return self.events, stats
    
    def _schedule_goals(self, total_goals: int) -> List[Dict]:
        goals = []
        
        home_remaining = self.home_goals_target
        away_remaining = self.away_goals_target
        
        available_minutes = list(range(5, 90))
        self.rng.rng.shuffle(available_minutes)
        
        for i in range(total_goals):
            if home_remaining > 0 and away_remaining > 0:
                if self.rng.next_random() < 0.5:
                    team = self.home_team
                    home_remaining -= 1
                else:
                    team = self.away_team
                    away_remaining -= 1
            elif home_remaining > 0:
                team = self.home_team
                home_remaining -= 1
            else:
                team = self.away_team
                away_remaining -= 1
            
            goals.append({
                'minute': available_minutes[i],
                'team': team
            })
        
        goals.sort(key=lambda x: x['minute'])
        
        return goals
    
    def _create_goal_sequence(self, minute: int, scoring_team: str):
        player = self._get_random_player(scoring_team, "forward")
        
        buildup_events = [
            (EventType.PASS, f"Nice passing movement by {scoring_team}"),
            (EventType.PASS, f"{scoring_team} building up the attack"),
        ]
        
        for i, (event_type, desc) in enumerate(buildup_events):
            self.events.append(MatchEvent(
                minute=max(1, minute - len(buildup_events) + i),
                event_type=event_type,
                team=scoring_team,
                description=desc
            ))
        
        self.events.append(MatchEvent(
            minute=minute,
            event_type=EventType.SHOT,
            team=scoring_team,
            player=player,
            description=f"{player} takes a shot!"
        ))
        
        if scoring_team == self.home_team:
            self.home_score += 1
        else:
            self.away_score += 1
        
        self.events.append(MatchEvent(
            minute=minute,
            event_type=EventType.GOAL,
            team=scoring_team,
            player=player,
            description=f"⚽ GOAL! {player} scores for {scoring_team}! {self.home_team} {self.home_score} - {self.away_score} {self.away_team}"
        ))
    
    def _create_regular_event(self, minute: int):
        team = self.home_team if self.rng.next_random() < 0.5 else self.away_team
        
        event_choices = [
            (EventType.PASS, "passes the ball forward"),
            (EventType.SHOT, "attempts a shot", "forward"),
            (EventType.CORNER, "wins a corner kick"),
            (EventType.FOUL, "commits a foul", "midfielder"),
            (EventType.OFFSIDE, "caught offside", "forward"),
            (EventType.SAVE, "shot saved by the goalkeeper!", "forward"),
        ]
        
        choice = self.rng.weighted_choice([
            (event_choices[0], 0.35),
            (event_choices[1], 0.20),
            (event_choices[2], 0.15),
            (event_choices[3], 0.15),
            (event_choices[4], 0.10),
            (event_choices[5], 0.05),
        ])
        
        event_type = choice[0]
        action = choice[1]
        position = choice[2] if len(choice) > 2 else "midfielder"
        
        player = self._get_random_player(team, position)
        
        description = f"{player} {action}"
        
        self.events.append(MatchEvent(
            minute=minute,
            event_type=event_type,
            team=team,
            player=player,
            description=description
        ))
    
    def _calculate_match_stats(self) -> Dict:
        home_shots = sum(1 for e in self.events if e.team == self.home_team and e.event_type in [EventType.SHOT, EventType.GOAL])
        away_shots = sum(1 for e in self.events if e.team == self.away_team and e.event_type in [EventType.SHOT, EventType.GOAL])
        
        home_corners = sum(1 for e in self.events if e.team == self.home_team and e.event_type == EventType.CORNER)
        away_corners = sum(1 for e in self.events if e.team == self.away_team and e.event_type == EventType.CORNER)
        
        home_fouls = sum(1 for e in self.events if e.team == self.home_team and e.event_type == EventType.FOUL)
        away_fouls = sum(1 for e in self.events if e.team == self.away_team and e.event_type == EventType.FOUL)
        
        total_events = len([e for e in self.events if e.event_type in [EventType.PASS, EventType.SHOT, EventType.GOAL]])
        home_events = len([e for e in self.events if e.team == self.home_team and e.event_type in [EventType.PASS, EventType.SHOT, EventType.GOAL]])
        
        home_possession = (home_events / total_events * 100) if total_events > 0 else 50
        away_possession = 100 - home_possession
        
        return {
            'possession': {
                self.home_team: round(home_possession, 1),
                self.away_team: round(away_possession, 1)
            },
            'shots': {
                self.home_team: home_shots,
                self.away_team: away_shots
            },
            'corners': {
                self.home_team: home_corners,
                self.away_team: away_corners
            },
            'fouls': {
                self.home_team: home_fouls,
                self.away_team: away_fouls
            },
            'total_goals': self.home_score + self.away_score
        }
