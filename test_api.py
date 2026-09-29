import asyncio
import aiohttp
from config import API_FOOTBALL_KEY

async def test_raw():
    # Test api-football raw
    headers = {"x-rapidapi-key": API_FOOTBALL_KEY, "x-rapidapi-host": "api-football-v1.p.rapidapi.com"}
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all", headers=headers) as resp:
            print("API-FOOTBALL STATUS:", resp.status)
            data = await resp.json()
            print("API-FOOTBALL DATA:", data)
    
    # Test ESPN raw
    async with aiohttp.ClientSession() as session:
        async with session.get("https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard") as resp:
            print("\nESPN STATUS:", resp.status)
            data = await resp.json()
            print("ESPN EVENTS COUNT:", len(data.get("events", [])))
            if data.get("events"):
                print("FIRST EVENT:", data["events"][0])

asyncio.run(test_raw())