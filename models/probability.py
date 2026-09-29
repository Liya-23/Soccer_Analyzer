import math
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ModelWeights:
    xg_weight: float = 0.40
    form_weight: float = 0.25
    rest_weight: float = 0.15
    injuries_weight: float = 0.10
    h2h_weight: float = 0.10

def form_to_score(form: List[str], recency_weight: bool = True) -> float:
    if not form:
        return 0.5
    points = []
    for i, result in enumerate(reversed(form)):
        weight = (i + 1) / len(form) if recency_weight else 1.0
        if result == "W":
            points.append(1.0 * weight)
        elif result == "D":
            points.append(0.5 * weight)
        else:
            points.append(0.0 * weight)
    return sum(points) / len(points) if points else 0.5

def rest_adjustment(rest_days: int) -> float:
    if rest_days <= 2:
        return 0.92
    elif rest_days <= 5:
        return 1.00
    else:
        return 0.98

def injury_adjustment(injured_count: int) -> float:
    return max(0.80, 1.0 - (injured_count * 0.03))

def poisson_probability(lambda_: float, k: int) -> float:
    if lambda_ <= 0:
        return 0.0 if k > 0 else 1.0
    try:
        return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)
    except OverflowError:
        return 0.0

def calculate_1x2_probabilities(
    home_xg: float, away_xg: float,
    home_form: List[str], away_form: List[str],
    home_rest: int, away_rest: int,
    home_injuries: int, away_injuries: int,
    h2h_home_wins: int, h2h_total: int,
    weights: ModelWeights = ModelWeights(),
) -> Dict[str, float]:
    # 1. Base Expected Goals parameters
    home_advantage = 1.12
    lambda_home = home_xg * home_advantage
    lambda_away = away_xg
    
    # 2. Extract statistical trend parameters
    f_home = form_to_score(home_form)
    f_away = form_to_score(away_form)
    
    # 3. Apply performance modifiers directly to Goal Expectations
    lambda_home *= rest_adjustment(home_rest) * injury_adjustment(home_injuries) * (0.5 + f_home)
    lambda_away *= rest_adjustment(away_rest) * injury_adjustment(away_injuries) * (0.5 + f_away)
    
    lambda_home = max(0.2, lambda_home)
    lambda_away = max(0.2, lambda_away)
    
    # 4. Compile precise 8x8 score grid matrix
    max_goals = 8
    p_home, p_draw, p_away = 0.0, 0.0, 0.0
    
    for h in range(max_goals):
        for a in range(max_goals):
            prob = poisson_probability(lambda_home, h) * poisson_probability(lambda_away, a)
            if h > a:
                p_home += prob
            elif h == a:
                p_draw += prob
            else:
                p_away += prob
                
    total = p_home + p_draw + p_away
    return {
        "home": round(p_home / total, 3),
        "draw": round(p_draw / total, 3),
        "away": round(p_away / total, 3),
    }

def calculate_goals_probabilities(home_xg: float, away_xg: float, threshold: float = 2.5) -> Dict[str, float]:
    lambda_total = home_xg + away_xg
    p_under = sum(poisson_probability(lambda_total, k) for k in range(int(threshold) + 1))
    return {"over": round(1.0 - p_under, 3), "under": round(p_under, 3)}

def calculate_btts_probability(home_xg: float, away_xg: float) -> float:
    return round((1.0 - poisson_probability(home_xg, 0)) * (1.0 - poisson_probability(away_xg, 0)), 3)

def remove_overround(odds: Dict[str, float]) -> Dict[str, float]:
    implied = {k: 1.0 / max(v, 1.01) for k, v in odds.items()}
    total = sum(implied.values())
    return {k: round(p / total, 3) for k, p in implied.items()}

def calculate_edge(model_prob: float, market_prob: float) -> float:
    if market_prob <= 0:
        return 0.0
    return round(((model_prob - market_prob) / market_prob) * 100, 1)

def calculate_fair_odds(probability: float) -> float:
    return round(1.0 / probability, 2) if probability > 0 else 0.0

def confidence_score(xg_convergence: float, data_completeness: float) -> float:
    return round(data_completeness * (1.0 - min(abs(xg_convergence), 0.3) / 0.3), 2)
