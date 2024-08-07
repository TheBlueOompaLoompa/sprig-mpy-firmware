from app import App
import json
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sprig import Sprig

from sprig import Tilemap
from ili9341 import color565

def setup(sprig: Sprig):
    app.data['tilemap'] = Tilemap.from_png("/apps/getting_started/spritesheet.png")

    # Fill the screen with the color black (For better performance you can just sprig.fbuf.fill(0))
    sprig.fbuf.fill(color565(0, 0, 0))

    # Draw tile to back framebuffer
    app.data['tilemap'].draw_tile_by_id(id=1, x=0, y=0)

    # Blit backbuffer to display
    sprig.flip_buf()


def loop(sprig: Sprig):
    pass

app = App('com.hackclub.sprig.GettingStarted', 'Getting Started', setup, loop)
