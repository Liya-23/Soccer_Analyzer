import tornado.web
import json
from datetime import datetime
from models.probability import (
    calculate_1x2_probabilities,
    calculate_goals_probabilities,
    calculate_btts_probability,
    remove_overround,
    calculate_edge,
    calculate_fair_odds,
    confidence_score,
)

class APIHandler(tornado.web.RequestHandler):
    """JSON API for match analysis."""
    
    def initialize(self):
        # Dynamically hook into the live data provider initialized in app.py
        self.provider = self.application.data_provider
    
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
    
    async def get(self):
        try:
            home = self.get_argument("home")
            away = self.get_argument("away")
            
            # Fetch all data asynchronously from the live application thread
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
            
            # Calculate true probabilities using the updated mathematical grid matrix
            market_1x2 = remove_overround(odds_dict["1x2"])
            model_1x2 = calculate_1x2_probabilities(
                home_xg, away_xg,
                home_form, away_form,
                home_rest, away_rest,
                len(home_injuries), len(away_injuries),
                h2h_home_wins, h2h_total,
            )
            
            model_goals = calculate_goals_probabilities(home_xg, away_xg)
            market_goals = remove_overround(odds_dict["over25"])
            
            model_btts = calculate_btts_probability(home_xg, away_xg)
            market_btts = remove_overround(odds_dict["btts"])
            
            # Calculate value edges
            edges = {
                "home": calculate_edge(model_1x2["home"], market_1x2["home"]),
                "draw": calculate_edge(model_1x2["draw"], market_1x2["draw"]),
                "away": calculate_edge(model_1x2["away"], market_1x2["away"]),
                "over": calculate_edge(model_goals["over"], market_goals["over"]),
                "under": calculate_edge(model_goals["under"], market_goals["under"]),
                "btts": calculate_edge(model_btts, market_btts["yes"]),
            }
            
            fair_odds = {
                k: calculate_fair_odds(v)
                for k, v in model_1x2.items()
            }
            
            # Calculate total API validation completeness percentage
            ver_list = [home_form_ver, away_form_ver, home_xg_ver, away_xg_ver, odds_ver, h2h_ver]
            completeness = ver_list.count("verified") / len(ver_list)
            
            conf = confidence_score(
                abs(home_xg - away_xg) / ((home_xg + away_xg) / 2),
                completeness,
            )
            
            # Safely grab value index items from the calculation loop dictionary
            best_edge = max(edges.items(), key=lambda x: x[1])
            recommendation = "BET" if best_edge[1] >= 3.0 else "MARGINAL" if best_edge[1] >= 1.0 else "NO BET"
            
            response = {
                "match": {
                    "home": home,
                    "away": away,
                },
                "analysis": {
                    "xg": {"home": home_xg, "away": away_xg},
                    "form": {"home": home_form, "away": away_form},
                    "injuries": {"home": home_injuries, "away": away_injuries},
                    "rest_days": {"home": home_rest, "away": away_rest},
                    "h2h_recent": h2h_results,
                },
                "probabilities": {
                    "1x2": {
                        "model": model_1x2,
                        "market": market_1x2,
                        "fair_odds": fair_odds,
                        "book_odds": odds_dict["1x2"],
                    },
                    "over_under": {
                        "model": model_goals,
                        "market": market_goals,
                        "book_odds": odds_dict["over25"],
                    },
                    "btts": {
                        "model": model_btts,
                        "market": market_btts["yes"],
                        "book_odds": odds_dict["btts"],
                    },
                },
                "value": {
                    "edges": edges,
                    "recommendation": recommendation,
                    "best_bet": best_edge[0],
                    "best_edge_percent": best_edge[1],
                },
                "confidence": conf,
                "verification": {
                    "form": {"home": home_form_ver, "away": away_form_ver},
                    "xg": {"home": home_xg_ver, "away": away_xg_ver},
                    "injuries": {"home": home_inj_ver, "away": away_inj_ver},
                    "rest": {"home": home_rest_ver, "away": away_rest_ver},
                    "odds": odds_ver,
                    "h2h": h2h_ver,
                },
            }
            
            self.write(json.dumps(response, indent=2))
        
        except Exception as e:
            self.set_status(400)
            self.write(json.dumps({"error": str(e)}))
