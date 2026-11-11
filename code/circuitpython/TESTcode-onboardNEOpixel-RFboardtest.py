# SPDX-License-Identifier: MIT
# ScoutMakes RF Remote Receiver - NeoPixel demo (QT Py RP2040)
#
# Each fob button lights the QT Py's onboard NeoPixel a different colour:
#   Button 1 (D0) -> red
#   Button 2 (D1) -> green
#   Button 3 (D2) -> blue
#   Button 4 (D3) -> yellow
# The LED stays lit while the button is held and turns off when it's released.
#
# Wiring:
#   Breakout STEMMA QT/Qwiic -> QT Py RP2040 STEMMA QT port (one JST-SH cable)
#   Breakout VT -> QT Py A0  (optional, separate jumper wire)
#
# Files on CIRCUITPY:
#   code.py                      (this file)
#   lib/scoutmakes_rf_remote.py

import time
import board
import digitalio
import neopixel_write
from scoutmakes_rf_remote import ScoutMakes_RFRemote

# --- Onboard NeoPixel -------------------------------------------------------
# On the QT Py RP2040 the NeoPixel has its own power pin that must be switched on.
pixel_power = digitalio.DigitalInOut(board.NEOPIXEL_POWER)
pixel_power.direction = digitalio.Direction.OUTPUT
pixel_power.value = True

pixel = digitalio.DigitalInOut(board.NEOPIXEL)
pixel.direction = digitalio.Direction.OUTPUT

BRIGHTNESS = 0.2  # 0.0 - 1.0; the onboard pixel is very bright at full power

# (R, G, B) for buttons 1..4 - change these to any colours you like
BUTTON_COLORS = [
    (255, 0, 0),    # Button 1: red
    (0, 255, 0),    # Button 2: green
    (0, 0, 255),    # Button 3: blue
    (255, 180, 0),  # Button 4: yellow
]
OFF = (0, 0, 0)


def show(color):
    r, g, b = (int(c * BRIGHTNESS) for c in color)
    neopixel_write.neopixel_write(pixel, bytearray([g, r, b]))  # pixel expects GRB order


show(OFF)

# --- RF Remote Receiver -----------------------------------------------------
i2c = board.STEMMA_I2C()  # STEMMA QT port; use board.I2C() for the header SCL/SDA pins
VT_PIN = board.A0  # set to None if VT is not wired

# stable_reads=1: react on the first read (no glitch filter) for the fastest response.
# Raise to 2 if you see stray presses. Older library versions (before v0.2.0) have
# no glitch filter and don't accept stable_reads - they already react on the first read.
try:
    remote = ScoutMakes_RFRemote(i2c, vt_pin=VT_PIN, stable_reads=1)
except TypeError:
    remote = ScoutMakes_RFRemote(i2c, vt_pin=VT_PIN)

print("ScoutMakes RF Remote Receiver ready - press a FOB button")

pressed_at = [None] * 4

while True:
    remote.update()
    now = time.monotonic()
    for d in range(4):  # button 1..4 -> D0..D3
        if remote.was_pressed(d):
            pressed_at[d] = now
            show(BUTTON_COLORS[d])
            print("Button %d pressed   (D%d HIGH)  VT=%d" % (d + 1, d, remote.vt))
        if remote.was_released(d):
            held = now - pressed_at[d] if pressed_at[d] is not None else 0
            pressed_at[d] = None
            print("Button %d released  (held %.2f s)" % (d + 1, held))
            if remote.buttons == 0:  # turn off only when no button is held
                show(OFF)
    time.sleep(0.002)  # poll ~500 times a second
