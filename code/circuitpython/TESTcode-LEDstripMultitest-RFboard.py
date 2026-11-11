# SPDX-License-Identifier: MIT
# ScoutMakes 315 MHz RF Remote Receiver (PCA I/O expander @ 0x41) -> NeoPixel strip
# QT Py RP2040 + Adafruit NeoPixel Driver BFF (#5645) + 10-pixel strip
#
# Wiring:
#   RF board     -> QT Py STEMMA QT port (I2C1), PCA expander at 0x41
#   NeoPixel BFF -> soldered to QT Py, data on MOSI ("MO") via solder jumper
#   Strip        -> BFF JST-PH connector
#
# Assumes the RF decoder's D0..D3 outputs go to PCA pins P0..P3:
#   P0 = A, P1 = B, P2 = C, P3 = D   (swap BTN_* below if yours differ)
#
# Fob buttons:
#   A = on / off
#   B = next colour
#   C = next animation (solid, rainbow, chase, breathe)
#   D = next brightness level
#
# Libraries needed in /lib: neopixel.mpy, adafruit_bus_device/

import math
import time

import board
import neopixel
from adafruit_bus_device.i2c_device import I2CDevice
from rainbowio import colorwheel

# ---------------- User settings ----------------
PCA_ADDR = 0x41
ACTIVE_LOW = False            # True if the outputs read 0 when a button is held
NUM_PIXELS = 30
PIXEL_PIN = board.A3        # "MO" pin; BFF jumper moved from A3 to MOSI
PIXEL_ORDER = neopixel.GRB    # use neopixel.GRBW for RGBW strips
POLL_INTERVAL = 0.02          # seconds between I2C polls (50 Hz)

COLORS = [
    (255, 140, 40),   # warm white
    (255, 0, 0),      # red
    (255, 80, 0),     # orange
    (0, 255, 0),      # green
    (0, 200, 255),    # cyan
    (0, 0, 255),      # blue
    (160, 0, 255),    # purple
]
BRIGHTNESS_LEVELS = [0.05, 0.15, 0.35, 0.7]
MODES = ["solid", "rainbow", "chase", "breathe"]

# PCA9536 / PCA9554-style registers (same layout for the first four)
REG_INPUT = 0x00
REG_CONFIG = 0x03             # 1 = input

BTN_A, BTN_B, BTN_C, BTN_D = 0x01, 0x02, 0x04, 0x08
BTN_MASK = 0x0F


class PCAButtons:
    """Reads 4 buttons from a PCA I/O expander and detects press edges."""

    def __init__(self, i2c, address=PCA_ADDR):
        self.dev = I2CDevice(i2c, address)   # raises ValueError if not found
        self._buf = bytearray(1)
        # Make P0..P3 inputs, leave any other pins as they are
        cfg = self._read(REG_CONFIG)
        self._write(REG_CONFIG, cfg | BTN_MASK)
        self.prev = self.read_buttons()      # quiet start: no phantom press

    def _read(self, reg):
        with self.dev as d:
            d.write_then_readinto(bytes((reg,)), self._buf)
        return self._buf[0]

    def _write(self, reg, value):
        with self.dev as d:
            d.write(bytes((reg, value & 0xFF)))

    def read_buttons(self):
        raw = self._read(REG_INPUT)
        if ACTIVE_LOW:
            raw = ~raw
        return raw & BTN_MASK

    def update(self):
        """Returns (held, pressed) where pressed = buttons that just went down."""
        now = self.read_buttons()
        pressed = now & ~self.prev
        self.prev = now
        return now, pressed


# ---------------- Setup ----------------
pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS, brightness=1.0, auto_write=False, pixel_order=PIXEL_ORDER
)
pixels.fill(0)
pixels.show()

i2c = board.STEMMA_I2C()

rf = None
while rf is None:
    try:
        rf = PCAButtons(i2c)
    except (ValueError, OSError) as e:
        print("Waiting for RF board at 0x{:02X}:".format(PCA_ADDR), e)
        pixels[0] = (40, 0, 0)          # dim red = board missing
        pixels.show()
        time.sleep(0.5)
        pixels[0] = 0
        pixels.show()
        time.sleep(0.5)

print("RF board found at 0x{:02X}".format(PCA_ADDR))

# Startup sweep so you know it's alive
for i in range(NUM_PIXELS):
    pixels.fill(0)
    pixels[i] = (0, 0, 30)
    pixels.show()
    time.sleep(0.03)
pixels.fill(0)
pixels.show()

# ---------------- State ----------------
lights_on = True
color_index = 0
mode_index = 0
bright_index = 1
anim_step = 0
last_poll = 0.0
last_frame = 0.0
flash_until = 0.0     # brief white flash on pixel 0 as press feedback


def scale(color, k):
    return tuple(int(c * k) for c in color)


def render(now):
    global anim_step
    if not lights_on:
        pixels.fill(0)
        return

    level = BRIGHTNESS_LEVELS[bright_index]
    color = COLORS[color_index]
    mode = MODES[mode_index]

    if mode == "solid":
        pixels.fill(scale(color, level))

    elif mode == "rainbow":
        for i in range(NUM_PIXELS):
            wheel = colorwheel((i * 256 // NUM_PIXELS + anim_step) & 0xFF)
            r, g, b = (wheel >> 16) & 0xFF, (wheel >> 8) & 0xFF, wheel & 0xFF
            pixels[i] = scale((r, g, b), level)
        anim_step = (anim_step + 2) & 0xFF

    elif mode == "chase":
        head = (anim_step // 3) % NUM_PIXELS
        for i in range(NUM_PIXELS):
            dist = (head - i) % NUM_PIXELS
            tail = max(0.0, 1.0 - dist * 0.3)
            pixels[i] = scale(color, level * tail)
        anim_step += 1

    elif mode == "breathe":
        k = (math.sin(now * 2.0) + 1.0) / 2.0     # 0..1, ~3 s period
        pixels.fill(scale(color, level * (0.08 + 0.92 * k)))

    if now < flash_until:
        pixels[0] = (60, 60, 60)


def handle_press(pressed):
    global lights_on, color_index, mode_index, bright_index, anim_step
    if pressed & BTN_A:
        lights_on = not lights_on
        print("A: lights", "on" if lights_on else "off")
    if pressed & BTN_B:
        color_index = (color_index + 1) % len(COLORS)
        lights_on = True
        print("B: colour", color_index)
    if pressed & BTN_C:
        mode_index = (mode_index + 1) % len(MODES)
        anim_step = 0
        lights_on = True
        print("C: mode", MODES[mode_index])
    if pressed & BTN_D:
        bright_index = (bright_index + 1) % len(BRIGHTNESS_LEVELS)
        lights_on = True
        print("D: brightness", BRIGHTNESS_LEVELS[bright_index])


# ---------------- Main loop ----------------
while True:
    now = time.monotonic()

    if now - last_poll >= POLL_INTERVAL:
        last_poll = now
        try:
            held, pressed = rf.update()
        except OSError as e:
            print("I2C error:", e)
            pressed = 0

        if pressed:
            handle_press(pressed)
            flash_until = now + 0.08

    if now - last_frame >= 0.02:       # ~50 fps
        last_frame = now
        render(now)
        pixels.show()
