# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for TG-Watch
 - port: nrf
 - board_id: TG-Watch
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_ble, adafruit_ble_apple_notification_center, adafruit_display_shapes, adafruit_display_text, adafruit_drv2605, adafruit_ds3231, adafruit_focaltouch, adafruit_lc709203f, adafruit_lsm6ds, adafruit_progressbar, adafruit_register, adafruit_st7789
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
MOSI: microcontroller.Pin  # P0_13
MISO: microcontroller.Pin  # P0_15
TX: microcontroller.Pin  # P0_25
RX: microcontroller.Pin  # P0_24
SCL: microcontroller.Pin  # P0_11
SDA: microcontroller.Pin  # P0_12
ACCEL_INT1: microcontroller.Pin  # P1_11
ACCEL_INT2: microcontroller.Pin  # P1_10
BATTERY_DIV: microcontroller.Pin  # P0_29
_A0: microcontroller.Pin  # P0_04
_A1: microcontroller.Pin  # P0_05
_A2: microcontroller.Pin  # P0_30
_A3: microcontroller.Pin  # P0_28
_A4: microcontroller.Pin  # P0_02
_A5: microcontroller.Pin  # P0_03
AREF: microcontroller.Pin  # P0_31
_VOLTAGE_MONITOR: microcontroller.Pin  # P0_29
_BATTERY: microcontroller.Pin  # P0_29
_SWITCH: microcontroller.Pin  # P1_02
_NFC1: microcontroller.Pin  # P0_09
_NFC2: microcontroller.Pin  # P0_10
_D10: microcontroller.Pin  # P0_27
_D11: microcontroller.Pin  # P0_06
_D12: microcontroller.Pin  # P0_08
_D13: microcontroller.Pin  # P1_09
_NEOPIXEL: microcontroller.Pin  # P0_16


# Members:

# Unmapped:
#   none
