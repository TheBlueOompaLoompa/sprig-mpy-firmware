import gc
import machine
machine.freq(133000000)
gc.enable()

print('Booting sprig')
import main
