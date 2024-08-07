# Hose - Sprig MicroPython Firmware

This isn't being made as any sort of replacement or anything, just a fun project. The goal is to have a platform similar to the original with the same amount ofhackability, but with MicroPython. This has the added bonus of being able to draw stuff directly.

## Setup:
1. Put the sprig into bootloader mode by holding the BOOTSEL button while plugging it into your computer
2. Go to https://micropython.org/download/RPI_PICO_W/ and download the latest firmware uf2 (Not preview)
3. Upload the MicroPython uf2 and wait for it to reboot
4. Follow this guide to install ampy: https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy
5. Clone this repository and cd into it
6. Run `ampy -p YOUR_PORT_HERE put src /`
7. Reboot the device and happy hacking!

## TODO:
- [x] Create basic setup with settings and launcher
- [ ] Add audio support
~~- [ ] Add network support~~
- [ ] Add wired serial communication
- [ ] Graphics helpers
    - [ ] Tilemap
    - [ ] Custom MicroPython firmware with native draw functions and display driver

## Apps I Want to Make:
- [ ] Software gallery (when) if networking is added
- [ ] Chat App
- [ ] Games
    - [ ] Flappy Bird clone
    - [ ] Chip-8 Emulator
