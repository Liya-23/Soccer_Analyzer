import aiohttp

class ESPNService:
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer"
    
    async def get_fixtures(self, league="eng.1"):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.BASE_URL}/{league}/scoreboard", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
                    return [{
                        "home": e.get("competitors", [{}])[0].get("team", {}).get("displayName"),
                        "away": e.get("competitors", [{}])[1].get("team", {}).get("displayName"),
                        "status": e.get("status", {}).get("type", {}).get("description"),
                        "score": f"{e.get('competitors', [{}])[0].get('score')} - {e.get('competitors', [{}])[1].get('score')}",
                    } for e in data.get("events", [])]
            except Exception as e:
                return []