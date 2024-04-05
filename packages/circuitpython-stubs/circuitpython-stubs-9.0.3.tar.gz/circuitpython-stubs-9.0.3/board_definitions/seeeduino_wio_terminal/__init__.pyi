# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Seeeduino Wio Terminal
 - port: atmel-samd
 - board_id: seeeduino_wio_terminal
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, samd, sdcardio, select, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PB08
A1: microcontroller.Pin  # PB09
A2: microcontroller.Pin  # PA07
A3: microcontroller.Pin  # PB04
A4: microcontroller.Pin  # PB05
A5: microcontroller.Pin  # PB06
A6: microcontroller.Pin  # PA04
A7: microcontroller.Pin  # PB07
A8: microcontroller.Pin  # PA06
D0: microcontroller.Pin  # PB08
D1: microcontroller.Pin  # PB09
D2: microcontroller.Pin  # PA07
D3: microcontroller.Pin  # PB04
D4: microcontroller.Pin  # PB05
D5: microcontroller.Pin  # PB06
D6: microcontroller.Pin  # PA04
D7: microcontroller.Pin  # PB07
D8: microcontroller.Pin  # PA06
D9: microcontroller.Pin  # PA17
D10: microcontroller.Pin  # PA16
D13: microcontroller.Pin  # PA15
TX: microcontroller.Pin  # PB26
RX: microcontroller.Pin  # PB27
MOSI: microcontroller.Pin  # PB02
SCK: microcontroller.Pin  # PB03
MISO: microcontroller.Pin  # PB00
CS: microcontroller.Pin  # PB01
SCL: microcontroller.Pin  # PA16
SDA: microcontroller.Pin  # PA17


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
