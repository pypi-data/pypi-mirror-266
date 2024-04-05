# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Capable Robot Programmable USB Hub
 - port: atmel-samd
 - board_id: capablerobot_usbhub
 - NVM size: 256
 - Included modules: alarm, analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, nvm, onewireio, os, ps2io, pwmio, rainbowio, random, rtc, samd, storage, struct, supervisor, sys, time, usb_cdc, watchdog
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
ANVLIM: microcontroller.Pin  # PA04


# Members:
def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
