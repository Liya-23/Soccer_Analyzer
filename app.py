import os
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options

from handlers.home import HomeHandler
from handlers.analyze import AnalyzeHandler
from handlers.api import APIHandler
from services.data_provider import APIDataProvider, CachedDataProvider

define("port", default=2040, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/analyze", AnalyzeHandler),
            (r"/api/match", APIHandler),
        ]
        
        settings = {
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "debug": options.debug,
            "autoreload": options.debug,
        }
        
        # Replaced the broken placeholder with your real production data engine
        base_provider = APIDataProvider()
        self.data_provider = CachedDataProvider(base_provider)
        
        super().__init__(handlers, **settings)

def main():
    tornado.options.parse_command_line()
    app = Application()
    print(f"🔴 Soccer Analyzer running on http://localhost:{options.port}")
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
