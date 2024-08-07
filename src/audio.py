from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sprig import Sprig

from machine import I2S, Pin
import struct
import cmath

class Audio:
    def __init__(self, sprig: Sprig):
        self.sample_rate = 24000
        self.audio = I2S(0,
            sck=Pin(10), ws=Pin(11), sd=Pin(9),
            mode=I2S.TX,
            bits=16,
            format=I2S.MONO,
            rate=self.sample_rate,
            ibuf=256*8)

    def make_tone(self, frequency):
        bits = 16
        # create a buffer containing the pure tone samples
        samples_per_cycle = self.sample_rate // frequency
        sample_size_in_bytes = bits // 8
        samples = bytearray(samples_per_cycle * sample_size_in_bytes)
        volume_reduction_factor = 32
        rang = pow(2, bits) // 2 // volume_reduction_factor
        
        format = "<h"
        
        for i in range(samples_per_cycle*50):
            sample = rang + int((rang - 1) * cmath.sin(2 * cmath.pi * i / samples_per_cycle))
            struct.pack_into(format, samples, i * sample_size_in_bytes, sample)

        self.audio.write(samples)

    def triangle(self, freq: int, amp: float, length: float):
        real_length = length*self.sample_rate * 2
        buf = bytearray(real_length)
        for x in range(real_length):
            t = float(x) / float(freq)
            buf[x] = 4.0*abs(t/float(freq)-floor(t/float(freq)-0.5))-1.0

        self.audio.write(buf)




