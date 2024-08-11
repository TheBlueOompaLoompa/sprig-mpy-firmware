import gc

from sprig import Sprig
sprig = Sprig()
gc.collect()
sprig.launch('com.hackclub.sprig.Launcher')
gc.collect()

while sprig.loop():
    pass
