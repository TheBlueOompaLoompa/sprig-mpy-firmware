import gc
from system import System

system = System()
system.launch('com_hackclub_sprig_Launcher')

while system.app._loop() != True:
    pass
