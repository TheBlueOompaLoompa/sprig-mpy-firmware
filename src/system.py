from ili9341 import color565
import os
from app import App, list_apps

class System:
    def __init__(self):
        self.app: App = None
        self.apps = list_apps()

    def launch(self, appid: str):
        print("Launching " + appid)
        for app in self.apps:
            if app['appid'] == appid:
                self.app = __import__('/apps/' + appid + '/' + app['module']).app
                self.app._system = self
                self.app.setup()
