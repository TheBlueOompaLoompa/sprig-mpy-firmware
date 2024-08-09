from ili9341 import color565

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
