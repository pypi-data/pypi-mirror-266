# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Feather ESP32-C6 4MB Flash No PSRAM
 - port: espressif
 - board_id: adafruit_feather_esp32c6_4mbflash_nopsram
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, mdns, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, ssl, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
A2: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
A3: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
A4: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
A5: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
D7: microcontroller.Pin  # GPIO7
D8: microcontroller.Pin  # GPIO8
BUTTON: microcontroller.Pin  # GPIO9
NEOPIXEL: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
SCK: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
MOSI: microcontroller.Pin  # GPIO22
D22: microcontroller.Pin  # GPIO22
MISO: microcontroller.Pin  # GPIO23
D23: microcontroller.Pin  # GPIO23
RX: microcontroller.Pin  # GPIO17
D17: microcontroller.Pin  # GPIO17
TX: microcontroller.Pin  # GPIO16
D16: microcontroller.Pin  # GPIO16
LED: microcontroller.Pin  # GPIO15
D15: microcontroller.Pin  # GPIO16
SCL: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
SDA: microcontroller.Pin  # GPIO19
D19: microcontroller.Pin  # GPIO19
I2C_POWER: microcontroller.Pin  # GPIO20


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
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


# Unmapped:
#   none
