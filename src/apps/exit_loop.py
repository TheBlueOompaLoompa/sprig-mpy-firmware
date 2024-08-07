from app import App
import json
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sprig import Sprig

def setup(sprig: Sprig):
    sprig.quit = True

def loop(sprig: Sprig):
    pass

app = App('com.hackclub.sprig.Exit', 'Break Loop', setup, loop)
