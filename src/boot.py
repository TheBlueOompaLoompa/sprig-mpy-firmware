import gc
from bootstrap import main
import machine
machine.freq(270000000)
gc.enable()

main(True)
