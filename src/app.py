from ili9341 import color565
from sprig import Sprig
import os
import json

class App:
    def __init__(self, appid: str, name: str, setup, loop):
        self.appid = appid
        self.name = name
        self.setup = setup
        self.loop = loop
        self.data = {}
        self.sprig: Sprig = Sprig()
        self._system = None
        self._onpress = { 'w': [], 'a': [], 's': [], 'd': [], 'i': [], 'j': [], 'k': [], 'l': []} 
        self._onrelease = { 'w': [], 'a': [], 's': [], 'd': [], 'i': [], 'j': [], 'k': [], 'l': []} 

    def _setup(self):
        self._onpress = { 'w': [], 'a': [], 's': [], 'd': [], 'i': [], 'j': [], 'k': [], 'l': []} 
        self._onrelease = { 'w': [], 'a': [], 's': [], 'd': [], 'i': [], 'j': [], 'k': [], 'l': []} 
        return self.setup()

    def _loop(self):
        self.sprig._input()
        return self.loop()

    def on_press(self, button: str, callback):
        self._onpress[button].append(callback)

    def on_release(self, button: str, callback):
        self._onrelease[button].append(callback)

def list_apps():
    apps = []
    for app_dir in os.listdir('/apps'):
        try:
            manifest = open_manifest(app_dir)
            manifest['appid'] = app_dir
            apps.append(manifest)
            print('Found app ' + app_dir)
        except Exception:
            print('Error: Missing manifest - ' + app_dir)

    return apps

def open_manifest(appid):
    manifest = None
    with open('/apps/' + appid + '/manifest.json', 'rt') as manifest_file:
        manifest = json.loads(manifest_file.read())
    return manifest

class ListMenu:
    def __init__(self, sprig: Sprig, item: ListMenuItem, offset=0, height=128):
        self.path: [str] = []
        self.item = item
        self.sprig = sprig
        self.offset = offset
        self.height = height
        childs = []
        for x in item.children:
            childs.append(x.text)
        self.list = SelectorList(self.sprig, childs, offset + 12, height)
    
    def _find_path(self, path: [str], level: ListMenuItem):
        if len(path) == 0: return level

        for item in level.children:
            if item.text == path[0]:
                if len(path) > 0:
                    return self._find_path(path[1:(len(path))], item)
                else:
                    return item

    def draw(self):
        item = self._find_path(self.path, self.item)
        view = item.children
        self.list.draw()
        hovered_item = view[self.list.index]
        status_call = hovered_item.status
        if status_call != None:
            self.sprig.fbuf.text(status_call(hovered_item), 0, self.offset, color565(0, 0, 255))

    def activate(self):
        self.path.append(self.list.items[self.list.index])
        item = self._find_path(self.path, self.item)
        if item.activate == None:
            childs = []
            for x in item.children:
                childs.append(x.text)
            self.list = SelectorList(self.sprig, childs, self.offset + 12, self.height)
        else:
            self.path.pop()
            item.activate(item)

    def back(self):
        self.path.pop()
        childs = []
        for x in self._find_path(self.path, self.item).children:
            childs.append(x.text)
        self.list = SelectorList(self.sprig, childs, self.offset + 12, self.height)

    def up(self):
        self.list.up()

    def down(self):
        self.list.down()


class ListMenuItem:
    def __init__(self, text: str, status = None, activate = None, children: [ListMenuItem] = [], extra = None):
        self.status = status
        self.activate = activate
        self.children = children
        self.text = text
        self.extra = extra

class SelectorList:
    def __init__(self, sprig: Sprig, items: [str], y_pos = 0, height = 128):
        self.items = items
        self.index = 0
        self.offset = 0
        self.y_pos = y_pos
        self.height = height
        self.sprig = sprig

    def draw(self):
        vspacing = 12
        self.sprig.fbuf.fill(color565(0, 0, 0))
        for (row, text) in enumerate(self.items):
            if row == self.index:
                self.sprig.fbuf.rect(0, (self.index - self.offset) * vspacing + self.y_pos, 160, vspacing, color565(255, 255, 255), True)
            if row >= self.offset:
                self.sprig.fbuf.text(text, 0, (row - self.offset) * vspacing + int((vspacing-8)/2) + self.y_pos, color565(255, 255, 255) if row != self.index else color565(0, 0, 0))

    def up(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.items) - 1

    def down(self):
        self.index += 1
        if self.index >= len(self.items):
            self.index = 0
