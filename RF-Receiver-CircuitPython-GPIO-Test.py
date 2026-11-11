# SPDX-FileCopyrightText: 2026 TinkeringTech LLC
#
# SPDX-License-Identifier: MIT

"""CircuitPython QT Py RP2040 ScoutMakes RF Remote Receiver test code (direct GPIO)"""
import time
import board
from digitalio import DigitalInOut, Direction, Pull

# Receiver channel outputs D0-D3 wired to A0-A3
PINS = {"A": board.A0, "B": board.A1, "C": board.A2, "D": board.A3}

buttons = {}
for name, pin in PINS.items():
    io = DigitalInOut(pin)
    io.direction = Direction.INPUT
    io.pull = Pull.DOWN  # outputs are active high
    buttons[name] = io

last = {name: False for name in buttons}
print("RF Remote Receiver ready - press a button on the fob")

while True:
    for name, io in buttons.items():
        value = io.value
        if value != last[name]:
            print("Button", name, "pressed" if value else "released")
            last[name] = value
    time.sleep(0.05)  # debounce delay
