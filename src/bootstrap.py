from sprig import Sprig

def main(manual = True):
    sprig = Sprig()

    if sprig.settings['autostart'] or manual:
        sprig.launch('com.hackclub.sprig.Launcher')
        while True:
            if sprig.loop(): return
