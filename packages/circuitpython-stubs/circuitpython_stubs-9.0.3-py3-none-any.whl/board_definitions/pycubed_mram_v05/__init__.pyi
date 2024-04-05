# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PyCubedv05-MRAM
 - port: atmel-samd
 - board_id: pycubed_mram_v05
 - NVM size: 256
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, board, builtins, builtins.pow3, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, errno, floppyio, frequencyio, getpass, i2ctarget, io, json, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, samd, sdcardio, select, storage, struct, supervisor, synthio, sys, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, warnings, watchdog, zlib
 - Frozen libraries: adafruit_register, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
VBUS_RST: microcontroller.Pin  # PA18
NEOPIXEL: microcontroller.Pin  # PA21


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
