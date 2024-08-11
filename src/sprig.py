from ili9341 import Display, color565
from keyboard import Keyboard
from machine import Pin, SPI
from bmp_reader import BMPReader
import framebuf
import os
import gc
import math

class Sprig:
    def __init__(self):
        gc.collect()
        self.spi = SPI(0, baudrate=40000000, sck=Pin(18), mosi=Pin(19))
        self.display = Display(self.spi, dc=Pin(22), cs=Pin(20), rst=Pin(26), width=160, height=128, mirror=True, bgr=False, rotation=90)
        self.fbuf = framebuf.FrameBuffer(bytearray(160 * 128 * 2), 160, 128, framebuf.RGB565)

        self.buttons = { 'w': { 'pin': Pin(5, Pin.IN, Pin.PULL_UP), 'state': False }, 'a': { 'pin': Pin(6, Pin.IN, Pin.PULL_UP), 'state': False }, 's': { 'pin': Pin(7, Pin.IN, Pin.PULL_UP), 'state': False }, 'd': { 'pin': Pin(8, Pin.IN, Pin.PULL_UP), 'state': False }, 'i': { 'pin': Pin(12, Pin.IN, Pin.PULL_UP), 'state': False }, 'j': { 'pin': Pin(13, Pin.IN, Pin.PULL_UP), 'state': False }, 'k': { 'pin': Pin(14, Pin.IN, Pin.PULL_UP), 'state': False }, 'l': { 'pin': Pin(15, Pin.IN, Pin.PULL_UP), 'state': False} }
        self._onpress = { 'w': [], 'a': [], 's': [], 'd': [], 'i': [], 'j': [], 'k': [], 'l': []} 
        self._onrelease = { 'w': [], 'a': [], 's': [], 'd': [], 'i': [], 'j': [], 'k': [], 'l': []} 
        self.kb = Keyboard(self, Keyboard.LAYOUTS['QWERTY'])

        self.lights = [Pin(28, Pin.OUT), Pin(4, Pin.OUT)]
        self.apps = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.display.cleanup()
        self.spi.deinit()
        del self.fbuf
        del self.display
        del self.spi
        del self.kb
        del self._onpress
        del self._onrelease
        del self.buttons
        del self.lights
        del self.apps
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
            if self.buttons[button]['state']:
                for x in self._onpress[button]:
                    x()
            else:
                for x in self._onrelease[button]:
                    x()

    def flip_buf(self):
        self.display.block(0, 0, 159, 127, self.fbuf)

    def file_or_dir_exists(self, filename):
        try:
            os.stat(filename)
            return True
        except OSError:
            return False

class Keyboard:
    def __init__(self, sprig, layout):
        self.sprig = sprig
        self.layout = layout
        self.x = 0
        self.y = 0
        self.shift = 0
        self.visible = False
        self.buffer = ''
        self.title = 'Untitled'
        self._on_key = None

        sprig.on_press('w', self._w)
        sprig.on_press('s', self._s)
        sprig.on_press('a', self._a)
        sprig.on_press('d', self._d)
        sprig.on_press('k', self._k)

    def _w(self):
        if self.visible:
            self.y -= 1
            if self.y < 0: self.y = len(self.layout[0]) - 1
            self.x = min(len(self.layout[0][self.y]) - 1, self.x)
            self._draw()

    def _s(self):
        if self.visible:
            self.y += 1
            if self.y >= len(self.layout[0]): self.y = 0
            self.x = min(len(self.layout[0][self.y]) - 1, self.x)
            self._draw()

    def _a(self):
        if self.visible:
            self.x -= 1 
            if self.x < 0: self.x = len(self.layout[0][self.y]) - 1
            self._draw()

    def _d(self):
        if self.visible:
            self.x += 1
            if self.x >= len(self.layout[0][self.y]): self.x = 0
            self._draw()

    def _k(self):
        if not(self.visible): return
        key = self.layout[1 if self.shift > 0 else 0][self.y][self.x]
        
        if key == '\r':
            self.shift += 1
            if self.shift > 2:
                self.shift = 0
            self._draw()
            return
        elif key == '\t':
            self.buffer = self.buffer[0:max(len(self.buffer)-2, 0)]
        elif key == '\n':
            pass
        else:
            self.buffer += key

        if self.shift == 1:
            self.shift = 0
        self._on_key(key)
        
        self._draw()

    def set_visible(self, vis: bool):
        self.visible = vis
        if self.visible:
            self._draw()

    def _draw(self):
        if not(self.visible): return
        self.sprig.fbuf.fill(color565(0, 0, 0))
        vspace = 12
        hspace = 12
        self.sprig.fbuf.text(self.title, 0, 0, color565(90, 90, 90))
        self.sprig.fbuf.text(self.buffer, 0, vspace, color565(255, 255, 255))
        self.sprig.fbuf.line(len(self.buffer)*8, vspace*2 - 1, len(self.buffer)*8+8, vspace*2 - 1, color565(255, 255, 255))

        for (ry, row) in enumerate(self.layout[1 if self.shift > 0 else 0]):
            y = ry+2
            for (x, char) in enumerate(row):
                color = color565(127, 127, 127) if self.x != x or self.y != ry else color565(0, 255, 0)
                if char == '\r':
                    self.sprig.fbuf.text('Shift', 0, y*vspace, color)
                elif char == ' ':
                    self.sprig.fbuf.text('Space', 6*8, y*vspace, color)
                elif char == '\t':
                    self.sprig.fbuf.text('<-', 12*8, y*vspace, color)
                elif char == '\n':
                    self.sprig.fbuf.text('Enter', 15*8, y*vspace, color)
                else:
                    self.sprig.fbuf.text(char, x*hspace, y*vspace, color)
        self.sprig.flip_buf()

    def on_key(self, callback):
        self._on_key = callback

    LAYOUTS = {
        'QWERTY': [
            ['`1234567890-=','qwertyuiop{}\\',"asdfghjkl;'",'zxcvbnm,./','\r \t\n'],
            ['~!@#$%^&*()_+','QWERTYUIOP{}|','ASDFGHJKL:"','ZXCVBNM<>?','\r \t\n']
        ],
        'WORKMAN': [
            ['`1234567890-=','qdrwbjfup;[]\\',"ashtgyneoi'",'zxmcvkl,./','\r \t\n'],
            ['~!@#$%^&*()_+','QDRWBJFUP:{}|','ASHTGYNEOI"','ZXMCVKL<>?','\r \t\n']
        ]
    }

class Tilemap:
    def __init__(self, sprig: Sprig, width: int, height: int, buf: framebuf.FrameBuffer):
        self.width = width
        self.height = height
        self._buf = buf
        self._tilebuf = framebuf.FrameBuffer(bytearray(16 * 16 * 2), 16, 16, framebuf.RGB565)
        self._sprig = sprig

    def draw_tile_by_id(self, id = 0, x = 0, y = 0):
        self._tilebuf.blit(self._buf, -((id*16) % self.width), -math.floor((id*16) / self.width))
        self._sprig.fbuf.blit(self._tilebuf, x, y)

    def draw_tile_by_xy(self, tile_x = 0, tile_y = 0, x = 0, y = 0):
        self._tilebuf.blit(self._buf, -x*16, -y*16)
        self._sprig.fbuf.blit(self._tilebuf, x, y)

    @staticmethod
    def from_bmp(sprig: Sprig, path: str):
        reader = BMPReader(path)
        buf = framebuf.FrameBuffer(bytearray(reader.width * reader.height * 2), reader.width, reader.height, framebuf.RGB565)
        for i in range(reader.width * reader.height):
            (pixel, x, y) = reader.read_pixel()
            buf.pixel(pixel, x, y)

        return Tilemap(sprig, reader.width, reader.height, buf)

