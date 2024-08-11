from app import App
from machine import reset

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sprig import Sprig

def setup(sprig: Sprig):
    reset()

def loop(sprig: Sprig):
    pass

app = App('com.hackclub.sprig.Reset', 'Reset', setup, loop)
