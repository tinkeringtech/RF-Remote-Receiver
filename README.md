# ScoutMakes RF Remote Receiver Breakout

A compact, beginner-friendly breakout that adds a **4-button 315 MHz wireless remote** to any microcontroller project. A 315 MHz 4-channel receiver module decodes the key fob. An **NXP PCA9536** I/O expander then puts all four buttons on the **I2C bus at address `0x41`**, so the whole remote takes just two wires over Qwiic / STEMMA QT. If you'd rather skip I2C, you can route the four channel outputs straight to four GPIO pins.

The fob comes pre-paired, so it works out of the box. You don't need Bluetooth, Wi-Fi or a pairing app.

## Where to Buy

Coming soon to our distributor partners. See the [product page](https://scoutmakes.com/products/rf-remote-receiver/) for updates, or [contact us](https://scoutmakes.com/contact) with questions.

## Use Cases

Remote-trigger a robot, toggle lights or relays, start and stop animations, open a prop door, or give a wearable a hidden "mode" button. It works anywhere you want a wireless button without building an app or a Bluetooth stack.

## Images

<!-- Replace with product photos and demo video -->
![RF Remote Receiver breakout](images/rf-remote-receiver-1.jpg)
![Key fob and receiver](images/rf-remote-receiver-2.jpg)

## Features

- **4-button 315 MHz key fob included**, pre-paired to the receiver
- **I2C via NXP PCA9536** at address `0x41`: all four buttons over two wires
- **Qwiic / STEMMA QT connector** for plug-and-play, solderless wiring
- **Direct GPIO option**: wire the four channel outputs to four pins if you don't want I2C
- **3.3 V to 5 V operation**
- **2.54 mm (0.1") header** for breadboards (5-pin header included)
- **CircuitPython ready**, and also works from MicroPython, Arduino or anything that speaks I2C
- **OSHWA certified** open-source hardware
- [NXP PCA9536 product page](https://www.nxp.com/part/PCA9536D)

## What's in the Box

- RF Remote Receiver breakout board
- 4-button 315 MHz remote control key fob (pre-paired)
- 5-pin 2.54 mm header

**Not included:** antenna and Qwiic / STEMMA QT cable.

## Compatibility

Works with Adafruit boards (QT Py, Feather, Metro), Raspberry Pi, Arduino, SparkFun Qwiic boards, and any microcontroller with 3.3 V or 5 V I2C or digital inputs.

## Pinout

> **TODO (verify against the schematic before publishing):** The pin order below is a placeholder.

| Pin | Function |
| --- | --- |
| VIN | 3.3 V – 5 V power |
| GND | Ground |
| SDA | I2C data (also on the Qwiic / STEMMA QT connector) |
| SCL | I2C clock (also on the Qwiic / STEMMA QT connector) |
| …   | … |

### PCA9536 Channel Mapping

The examples assume this mapping. Adjust `BUTTONS` in the code if the board differs.

| Fob button | Receiver channel | PCA9536 pin | Input register bit |
| --- | --- | --- | --- |
| A | D0 | IO0 | bit 0 (`0x01`) |
| B | D1 | IO1 | bit 1 (`0x02`) |
| C | D2 | IO2 | bit 2 (`0x04`) |
| D | D3 | IO3 | bit 3 (`0x08`) |

## Wiring

### I2C (recommended)

Plug a Qwiic / STEMMA QT cable between the breakout and your board. That's it. The board answers at `0x41`, so you can run `i2c.scan()` to confirm it's there.

### Direct GPIO

Wire VIN and GND, then connect the four channel outputs to four digital input pins. See `RF-Receiver-CircuitPython-GPIO-Test.py`.

## Example Code

| File | What it does |
| --- | --- |
| `RF-Receiver-CircuitPython-Test.py` | CircuitPython over I2C (PCA9536). Prints button presses and lights the NeoPixel a different colour per button. Written for the QT Py RP2040. No extra libraries needed beyond `neopixel`. |
| `RF-Receiver-CircuitPython-GPIO-Test.py` | CircuitPython reading the four channel outputs directly on A0–A3. |
| `RF-Receiver-Arduino-Test/RF-Receiver-Arduino-Test.ino` | Arduino over I2C using `Wire`. Prints press and release events to Serial. |

### CircuitPython Quick Start

1. Install CircuitPython on your board.
2. Copy `neopixel.mpy` from the [CircuitPython library bundle](https://circuitpython.org/libraries) into `CIRCUITPY/lib`.
3. Copy `RF-Receiver-CircuitPython-Test.py` to the board as `code.py`.
4. Open the serial console and press the fob buttons.

### Reading the PCA9536 from Any Platform

The PCA9536 is simple enough to drive with no library:

1. Write `0x0F` to register `0x03` (Configuration) to make IO0–IO3 inputs. This is the power-on default anyway.
2. Read register `0x00` (Input Port). Bits 0–3 hold the current state of channels D0–D3.

## A Note on Momentary vs Latching Outputs

315 MHz 4-channel receiver modules come in **momentary** versions, where an output is high only while the button is held, and **latching or toggle** versions, where each press flips the output. The examples report both press and release edges, so they work either way. Check which behaviour your board has before designing around it.

## A Note on the Antenna

No antenna is included. For usable range, solder a quarter-wave wire antenna to the ANT pad. At 315 MHz that's about **23.8 cm (9.4")** of solid-core wire, kept straight and away from ground planes. Without an antenna, range drops to a few centimetres.

## A Note on Frequency and Region

315 MHz is common for remotes in North America and parts of Asia. In the UK and EU, short-range devices generally use 433.92 MHz or 868 MHz instead. Check your local rules before using a 315 MHz transmitter outside the regions it's intended for.

## License

Hardware design files and documentation: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). See `LICENSE`.
Example code: MIT, as noted in each file's SPDX header.

ScoutMakes™ is a brand of TinkeringTech LLC.
