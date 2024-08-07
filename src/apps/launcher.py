from ili9341 import color565
from app import App, ListMenu, ListMenuItem
import json
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sprig import Sprig

def setup(sprig: Sprig):
    sprig.fbuf.fill(color565(0, 0, 0))
    sprig.flip_buf()

    app.on_press('w', w)
    app.on_press('s', s)
    app.on_release('k', k_release)

    applist = []
    for a in sprig.apps:
        applist.append(ListMenuItem(a['name'], activate=launch, extra=a))
    app.data['menu'] = ListMenu(sprig, ListMenuItem('', children=applist), 12, 128-12)

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

def k_release():
    app.data['menu'].activate()

def launch(item: ListMenuItem):
    app.sprig.launch(item.extra['appid'])

def loop(sprig: Sprig):
    pass

app = App('com.hackclub.sprig.Launcher', 'Launcher', setup, loop)
