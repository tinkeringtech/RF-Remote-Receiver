# SPDX-FileCopyrightText: 2026 TinkeringTech LLC
#
# SPDX-License-Identifier: MIT

"""CircuitPython QT Py RP2040 ScoutMakes RF Remote Receiver test code (I2C / PCA9536)"""
import time
import board
import neopixel

PCA9536_ADDR = 0x41
REG_INPUT = 0x00   # Input Port register
REG_CONFIG = 0x03  # Configuration register (1 = input)

# Fob button -> (PCA9536 bit mask, NeoPixel colour). Adjust if your board's mapping differs.
BUTTONS = {
    "A": (0x01, (255, 0, 0)),
    "B": (0x02, (0, 255, 0)),
    "C": (0x04, (0, 0, 255)),
    "D": (0x08, (255, 255, 0)),
}
ACTIVE_HIGH = True  # receiver outputs go high when a button is pressed

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.1  # Set brightness

i2c = board.STEMMA_I2C()  # Use board.I2C() on boards without a STEMMA QT port
buf = bytearray(1)


def write_reg(reg, value):
    while not i2c.try_lock():
        pass
    try:
        i2c.writeto(PCA9536_ADDR, bytes([reg, value]))
    finally:
        i2c.unlock()


def read_reg(reg):
    while not i2c.try_lock():
        pass
    try:
        i2c.writeto_then_readfrom(PCA9536_ADDR, bytes([reg]), buf)
    finally:
        i2c.unlock()
    return buf[0]


# Check the board is there
while not i2c.try_lock():
    pass
found = PCA9536_ADDR in i2c.scan()
i2c.unlock()
if not found:
    raise RuntimeError("RF Remote Receiver not found at 0x41 - check the cable")

write_reg(REG_CONFIG, 0x0F)  # IO0-IO3 as inputs
print("RF Remote Receiver ready - press a button on the fob")

last = 0
while True:
    state = read_reg(REG_INPUT) & 0x0F
    if not ACTIVE_HIGH:
        state = ~state & 0x0F

    if state != last:
        for name, (mask, colour) in BUTTONS.items():
            if state & mask and not last & mask:
                print("Button", name, "pressed")
            elif last & mask and not state & mask:
                print("Button", name, "released")
        last = state

    # Light the colour of the lowest pressed button, or turn off
    pixel.fill((0, 0, 0))
    for name, (mask, colour) in BUTTONS.items():
        if state & mask:
            pixel.fill(colour)
            break

    time.sleep(0.05)  # debounce delay
