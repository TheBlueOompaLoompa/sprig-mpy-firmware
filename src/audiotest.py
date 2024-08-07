import os
import math
import struct
from machine import Pin, I2S
import uasyncio as asyncio

SCK_PIN = 10
WS_PIN = 11
SD_PIN = 9
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 2000
# ======= AUDIO CONFIGURATION =======
TONE_FREQUENCY_IN_HZ = 440
SAMPLE_SIZE_IN_BITS = 16
FORMAT = I2S.MONO  # only MONO supported in this example
SAMPLE_RATE_IN_HZ = 24_000
# ======= AUDIO CONFIGURATION =======

SAMPLE_SIZE_IN_BYTES = SAMPLE_SIZE_IN_BITS // 8

class Audio:
    def __init__(self):
        self.audio = I2S(
            I2S_ID,
            sck=Pin(SCK_PIN),
            ws=Pin(WS_PIN),
            sd=Pin(SD_PIN),
            mode=I2S.TX,
            bits=SAMPLE_SIZE_IN_BITS,
            format=FORMAT,
            rate=SAMPLE_RATE_IN_HZ,
            ibuf=BUFFER_LENGTH_IN_BYTES,
        )

    def generate(self, wave: Wave, freq = 440, volume = 3, length = 1.0):
        out = None
        if wave == Wave.SINE:
            out = self._sine_wave(freq, volume, length)

        return out

    def _sine_wave(self, freq: int, volume: int, length: float):
        (samples_per_cycle, range, samples) = self._sample_setup(freq, volume, length)

        for i in range(samples_per_cycle):
            sample = range + int((range - 1) * math.sin(2 * math.pi * i / samples_per_cycle))
            self._pack(sample, i, samples)

        return samples

    def _pack(self, sample: int, i: int, samples: bytearray):
        struct.pack_into('<h', samples, i * SAMPLE_SIZE_IN_BYTES, sample)

    def _sample_setup(self, freq: int, volume: int, length: float):
        samples_per_cycle = SAMPLE_RATE_IN_HZ // TONE_FREQUENCY_IN_HZ
        return (
            samples_per_cycle,
            pow(2, SAMPLE_SIZE_IN_BITS) // 2 // volume,
            bytearray(samples_per_cycle * SAMPLE_SIZE_IN_BYTES)
        )

class Wave:
    SINE = 0
    SAW = 1

audio = Audio()
while True:
    audio.audio.write(audio.generate(Wave.SINE))


#for i in range(samples_per_cycle):
#    sample = range + int((range - 1) * (i / samples_per_cycle % 1 - .5))
    #sample = range + int((range - 1) * math.sin(2 * math.pi * i / samples_per_cycle))
#    struct.pack_into(format, samples, i * sample_size_in_bytes, sample)

# continuously write tone sample buffer to an I2S DAC
#print("==========  START PLAYBACK ==========")
#try:
#    while True:
#        num_written = audio_out.write(samples)

#except (KeyboardInterrupt, Exception) as e:
#    print("caught exception {} {}".format(type(e).__name__, e))

# cleanup
#audio_out.deinit()
#print("Done")
