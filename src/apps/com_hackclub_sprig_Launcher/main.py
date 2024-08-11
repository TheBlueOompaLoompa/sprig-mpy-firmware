from ili9341 import color565
from app import App, ListMenu, ListMenuItem, list_apps
import json
import os

def setup():
    sprig = app.sprig
    sprig.fbuf.fill(color565(0, 0, 0))
    sprig.flip_buf()

    sprig.on_press('w', w)
    sprig.on_press('s', s)
    sprig.on_press('l', l)
    sprig.on_release('k', k_release)

    applist = []
    for a in list_apps():
        applist.append(ListMenuItem(a['name'], activate=launch, extra=a))
    app.data['menu'] = ListMenu(sprig, ListMenuItem('', children=applist), 12, 128-12)
    app.data['break'] = False

    draw()

def draw():
    app.data['menu'].draw()
    app.sprig.fbuf.text("Sprig Launcher", 0, 0, color565(0, 255, 0))
    app.sprig.flip_buf()

def w():
    app.data['menu'].up()
    draw()

def s():
    app.data['menu'].down()
    draw()

def l():
    app.data['break'] = True

def k_release():
    app.data['menu'].activate()

def launch(item: ListMenuItem):
    app._system.launch(item.extra['appid'])

def loop():
    return app.data['break']

app = App('com.hackclub.sprig.Launcher', 'Launcher', setup, loop)
