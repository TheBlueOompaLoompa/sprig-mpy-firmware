from ili9341 import Display, color565
from keyboard import Keyboard
from machine import Pin, SPI
from bmp_reader import BMPReader
import framebuf
import os
import json
import gc
import sys
import network
import math
from time import sleep
from audio import Audio

class Sprig:
    def __init__(self):
        self.spi = SPI(0, baudrate=40000000, sck=Pin(18), mosi=Pin(19))
        self.display = Display(self.spi, dc=Pin(22), cs=Pin(20), rst=Pin(26), width=160, height=128, mirror=True, bgr=False, rotation=90)
        self.fbuf = framebuf.FrameBuffer(bytearray(160 * 128 * 2), 160, 128, framebuf.RGB565)

        self.buttons = { 'w': { 'pin': Pin(5, Pin.IN, Pin.PULL_UP), 'state': False }, 'a': { 'pin': Pin(6, Pin.IN, Pin.PULL_UP), 'state': False }, 's': { 'pin': Pin(7, Pin.IN, Pin.PULL_UP), 'state': False }, 'd': { 'pin': Pin(8, Pin.IN, Pin.PULL_UP), 'state': False }, 'i': { 'pin': Pin(12, Pin.IN, Pin.PULL_UP), 'state': False }, 'j': { 'pin': Pin(13, Pin.IN, Pin.PULL_UP), 'state': False }, 'k': { 'pin': Pin(14, Pin.IN, Pin.PULL_UP), 'state': False }, 'l': { 'pin': Pin(15, Pin.IN, Pin.PULL_UP), 'state': False} }
        self._onpress = { 'w': [], 'a': [], 's': [], 'd': [], 'i': [], 'j': [], 'k': [], 'l': []} 
        self._onrelease = { 'w': [], 'a': [], 's': [], 'd': [], 'i': [], 'j': [], 'k': [], 'l': []} 
        self.kb = Keyboard(self, Keyboard.LAYOUTS['WORKMAN'])

        self.lights = [Pin(28, Pin.OUT), Pin(4, Pin.OUT)]
        self.lights[0].high()

        self.settings = {
            "networks": [],
            "autostart": False,
            "splash": True,
            "wifi": False
        }

        if not(self.file_or_dir_exists('/settings.json')):
            open('/settings.json', 'x').close()

        with open('/settings.json') as file:
            settings = {}
            try:
                settings = json.loads(file.read())
            except ValueError:
                settings = {}

            for key in dict.keys(self.settings):
                if key in settings:
                    self.settings[key] = settings[key]
            
            file.close()
        
        self.save_settings()

        self.audio = None

        self.app = None
        self.quit = False
        self.apps = []
        self.update_app_list()
        if self.settings['splash']:
            self.splash()

        self.lights[0].low()

    def init_audio(self):
        self.audio = Audio(self)

    def update_app_list(self):
        self.apps = []
        for app in os.listdir('/apps'):
            if app.endswith('.py'):
                temp_app = __import__('/apps/'+ app.replace('.py', '')).app
                self.apps.append({
                    'path': app.replace('.py', ''),
                    'name': ''+ temp_app.name,
                    'appid': ''+ temp_app.appid
                })
                del temp_app

    def launch(self, appid: str):
        del self.app
        gc.collect()
        path = ''
        for app in self.apps:
            if app['appid'] == appid:
                path = app['path']
                break
        try:
            self.app = __import__("/apps/" + path).app
            self.app._setup(self)
        except Exception:
            print('Failed to launch ' + appid)

    def loop(self):
        self._input()
        self.app.loop(self)

        if self.quit:
            return True
        else:
            return False

    def splash(self):
        splash = BMPReader('splash.bmp')

        splash_buf = framebuf.FrameBuffer(bytearray(160 * 128 * 2), 160, 128, framebuf.RGB565)
        for i in range(splash.width*splash.height):
            (pixel, x, y) = splash.read_pixel()
            splash_buf.pixel(x, y, pixel & 0xffff)

        offset = 0
        speed = 16
        while offset < 160 and offset > -200:
            self.fbuf.fill(0)
            self.fbuf.blit(splash_buf, offset, int(math.sin(float(offset)/30.0)*10.0))
            self.flip_buf()
            offset += speed
            speed -= 1
            sleep(0.01)

        del splash_buf
        gc.collect()

    def on_press(self, button: str, callback):
        self._onpress[button].append(callback)

    def on_release(self, button: str, callback):
        self._onrelease[button].append(callback)

    def _input(self):
        self._input_toggle('w')
        self._input_toggle('a')
        self._input_toggle('s')
        self._input_toggle('d')

        self._input_toggle('i')
        self._input_toggle('j')
        self._input_toggle('k')
        self._input_toggle('l')

    def _input_toggle(self, button):
        if not(self.buttons[button]['pin'].value()) != self.buttons[button]['state']:
            self.buttons[button]['state'] = not(self.buttons[button]['state'])
            app = self.app
            if self.buttons[button]['state']:
                for x in self._onpress[button]:
                    x()
                for x in app._onpress[button]:
                    x()
            else:
                for x in self._onrelease[button]:
                    x()
                for x in app._onrelease[button]:
                    x()

    def flip_buf(self):
        self.display.block(0, 0, 159, 127, self.fbuf)

    def save_settings(self):
        with open('/settings.json', 'w+') as file:
            file.write(json.dumps(self.settings))
            file.close()

    def file_or_dir_exists(self, filename):
        try:
            os.stat(filename)
            return True
        except OSError:
            return False

class Tilemap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
    @staticmethod
    def from_bmp(path: str):
        reader = BMPReader(path)

