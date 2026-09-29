import tornado.web
from datetime import datetime
from models.probability import (
    calculate_1x2_probabilities, calculate_goals_probabilities, 
    calculate_btts_probability, remove_overround, calculate_edge, 
    calculate_fair_odds, confidence_score
)

class AnalyzeHandler(tornado.web.RequestHandler):
    def initialize(self):
        # Dynamically pulls from the core pipeline instantiated during launch sequence
        self.provider = self.application.data_provider
    
    async def get(self):
        home = self.get_argument("home", default="Liverpool")
        away = self.get_argument("away", default="Arsenal")
        
        home_form, home_form_ver = await self.provider.get_team_form(home)
        away_form, away_form_ver = await self.provider.get_team_form(away)
        home_xg, home_xg_ver = await self.provider.get_xg(home)
        away_xg, away_xg_ver = await self.provider.get_xg(away)
        home_injuries, home_inj_ver = await self.provider.get_injuries(home)
        away_injuries, away_inj_ver = await self.provider.get_injuries(away)
        home_rest, home_rest_ver = await self.provider.get_rest_days(home, datetime.now())
        away_rest, away_rest_ver = await self.provider.get_rest_days(away, datetime.now())
        odds_dict, odds_ver = await self.provider.get_odds(home, away)
        h2h_results, h2h_ver = await self.provider.get_h2h(home, away)
        
        h2h_home_wins = h2h_results.count("HW")
        h2h_total = len(h2h_results)
        
        market_1x2 = remove_overround(odds_dict["1x2"])
        model_1x2 = calculate_1x2_probabilities(
            home_xg, away_xg, home_form, away_form,
            home_rest, away_rest, len(home_injuries), len(away_injuries),
            h2h_home_wins, h2h_total
        )
        
        model_goals = calculate_goals_probabilities(home_xg, away_xg)
        market_goals = remove_overround(odds_dict["over25"])
        model_btts = calculate_btts_probability(home_xg, away_xg)
        market_btts = remove_overround(odds_dict["btts"])
        
        edges = {
            "home": calculate_edge(model_1x2["home"], market_1x2["home"]),
            "draw": calculate_edge(model_1x2["draw"], market_1x2["draw"]),
            "away": calculate_edge(model_1x2["away"], market_1x2["away"]),
            "over": calculate_edge(model_goals["over"], market_goals["over"]),
            "under": calculate_edge(model_goals["under"], market_goals["under"]),
            "btts": calculate_edge(model_btts, market_btts["yes"]),
        }
        
        fair_odds = {k: calculate_fair_odds(v) for k, v in model_1x2.items()}
        
        # Determine verification completeness percentage fraction
        ver_list = [home_form_ver, away_form_ver, home_xg_ver, away_xg_ver, odds_ver, h2h_ver]
        completeness = ver_list.count("verified") / len(ver_list)
        conf = confidence_score(abs(home_xg - away_xg) / ((home_xg + away_xg) / 2), completeness)
        
        # Fixed Tuple unpack logic sorting parameters precisely by dict value item
        best_edge = max(edges.items(), key=lambda x: x[1])
        recommendation = "BET" if best_edge[1] >= 3.0 else "MARGINAL" if best_edge[1] >= 1.0 else "NO BET"
        
        data = {
            "home": home, "away": away,
            "home_xg": home_xg, "away_xg": away_xg,
            "home_form": home_form, "away_form": away_form,
            "home_injuries": home_injuries, "away_injuries": away_injuries,
            "home_rest": home_rest, "away_rest": away_rest, "h2h": h2h_results,
            "model_1x2": model_1x2, "market_1x2": market_1x2, "fair_odds_1x2": fair_odds,
            "odds_1x2": odds_dict["1x2"], "model_goals": model_goals, "market_goals": market_goals,
            "odds_goals": odds_dict["over25"], "model_btts": model_btts, "market_btts": market_btts["yes"],
            "odds_btts": odds_dict["btts"], "edges": edges, "confidence": conf,
            "recommendation": recommendation, "best_bet": best_edge[0], "best_edge": best_edge[1],
            "verification": {
                "form": (home_form_ver, away_form_ver), "xg": (home_xg_ver, away_xg_ver),
                "injuries": (home_inj_ver, away_inj_ver), "rest": (home_rest_ver, away_rest_ver),
                "odds": odds_ver, "h2h": h2h_ver,
            }
        }
        self.render("analysis.html", data=data)
