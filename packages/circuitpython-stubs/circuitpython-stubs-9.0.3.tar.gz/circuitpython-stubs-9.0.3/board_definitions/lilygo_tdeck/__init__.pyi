# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for LILYGO T-DECK
 - port: espressif
 - board_id: lilygo_tdeck
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
IO15: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
IO17: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
IO20: microcontroller.Pin  # GPIO20
IO21: microcontroller.Pin  # GPIO21
IO35: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
IO38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
IO41: microcontroller.Pin  # GPIO41
IO42: microcontroller.Pin  # GPIO42
IO43: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
IO45: microcontroller.Pin  # GPIO45
IO46: microcontroller.Pin  # GPIO46
IO47: microcontroller.Pin  # GPIO47
IO48: microcontroller.Pin  # GPIO48
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
SCK: microcontroller.Pin  # GPIO40
MOSI: microcontroller.Pin  # GPIO41
MISO: microcontroller.Pin  # GPIO38
SDA: microcontroller.Pin  # GPIO18
SCL: microcontroller.Pin  # GPIO8
TFT_CS: microcontroller.Pin  # GPIO12
TFT_DC: microcontroller.Pin  # GPIO11
SDCARD_CS: microcontroller.Pin  # GPIO39
TOUCH_INT: microcontroller.Pin  # GPIO16
KEYBOARD_INT: microcontroller.Pin  # GPIO46
TRACKBALL_CLICK: microcontroller.Pin  # GPIO0
TRACKBALL_UP: microcontroller.Pin  # GPIO3
TRACKBALL_DOWN: microcontroller.Pin  # GPIO15
TRACKBALL_LEFT: microcontroller.Pin  # GPIO1
TRACKBALL_RIGHT: microcontroller.Pin  # GPIO2
MICROPHONE_SCK: microcontroller.Pin  # GPIO47
MICROPHONE_WS: microcontroller.Pin  # GPIO21
MICROPHONE_DIN: microcontroller.Pin  # GPIO14
MICROPHONE_MCK: microcontroller.Pin  # GPIO48
SPEAKER_SCK: microcontroller.Pin  # GPIO7
SPEAKER_WS: microcontroller.Pin  # GPIO5
SPEAKER_DOUT: microcontroller.Pin  # GPIO6
LORA_CS: microcontroller.Pin  # GPIO9
LORA_DIO1: microcontroller.Pin  # GPIO45
LORA_RST: microcontroller.Pin  # GPIO17
LORA_BUSY: microcontroller.Pin  # GPIO13
BAT_ADC: microcontroller.Pin  # GPIO4
POWER_ON: microcontroller.Pin  # GPIO10


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
