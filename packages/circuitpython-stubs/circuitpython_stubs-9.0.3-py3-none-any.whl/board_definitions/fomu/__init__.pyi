# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Fomu
 - port: litex
 - board_id: fomu
 - NVM size: 0
 - Included modules: _asyncio, _pixelmap, adafruit_pixelbuf, aesio, array, atexit, binascii, builtins, builtins.pow3, busio.SPI, busio.UART, codeop, collections, digitalio, errno, getpass, io, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, os, os.getenv, rainbowio, random, re, select, storage, struct, supervisor, sys, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
TOUCH1: microcontroller.Pin  # TOUCH1
TOUCH2: microcontroller.Pin  # TOUCH2
TOUCH3: microcontroller.Pin  # TOUCH3
TOUCH4: microcontroller.Pin  # TOUCH4


# Members:

# Unmapped:
#   none
