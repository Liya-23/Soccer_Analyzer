import tornado.web
from services.analysis import ESPNService

class HomeHandler(tornado.web.RequestHandler):
    async def get(self):
        espn = ESPNService()
        fixtures = await espn.get_fixtures()
        self.render("index.html", matches=fixtures)