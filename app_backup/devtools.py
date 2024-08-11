from ili9341 import color565
from app import App, SelectorList, ListMenu, ListMenuItem
import json
import os
import machine

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sprig import Sprig

def setup(sprig: Sprig):
    sprig.fbuf.fill(color565(0, 0, 0))
    sprig.flip_buf()

    app.data['menu'] = ListMenu(
        sprig,
        ListMenuItem('', children=[
            ListMenuItem('Enter Bootloader', activate=bootloader),
            ListMenuItem('Toggle Splash', activate=splash, status=splash_status),
        ]),
        offset=12,
        height=128-12
    )

    app.on_press('w', w)
    app.on_press('s', s)
    app.on_press('k', k)
    app.on_release('l', l)

    draw()

def bootloader(item: ListMenuItem):
    machine.bootloader()

def splash(_item: ListMenuItem):
    app.sprig.settings['splash'] = not(app.sprig.settings['splash'])
    app.sprig.save_settings()

def splash_status(_item: ListMenuItem):
    return 'Splash is ' + ('Enabled' if app.sprig.settings['splash'] else 'Disabled')

def draw():
    if not(app.data['visible']): return
    app.data['menu'].draw()
    app.sprig.fbuf.text('Settings', 0, 0, color565(255, 0, 255))
    app.sprig.flip_buf()

def w():
    if not(app.data['visible']): return
    app.data['menu'].up()
    draw()

def s():
    if not(app.data['visible']): return
    app.data['menu'].down()
    draw()

def k():
    if not(app.data['visible']): return
    app.data['menu'].activate()
    draw()

def l():
    if not(app.data['visible']): return
    if len(app.data['menu'].path) == 0:
        app.sprig.launch('com.hackclub.sprig.Launcher')
    else:
        app.data['menu'].back()
        draw()

def loop(sprig: Sprig):
    pass

app = App('com.hackclub.sprig.Settings', 'Settings', setup, loop)
