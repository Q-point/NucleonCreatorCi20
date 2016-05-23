#!/usr/bin/python

import ctypes
import os

# Try to locate the .so file in the same directory as this file
from ctypes import *
_mod = CDLL("./libCi20GPIO.so")

# int setup(void) 
_setup = _mod.setup
_setup.restype = ctypes.c_int

# int ci20ValidGPIO(int pin)
_valid = _mod.ci20ValidGPIO

# int ci20PinMode(int pin, int mode)
_pinMode = _mod.ci20PinMode


# int ci20DigitalRead(int pin) 
_digitalRead = _mod.ci20DigitalRead

# int ci20DigitalWrite(int pin, int value)
_digitalWrite = _mod.ci20DigitalWrite

#int ci20GC(void)
_cleanup = _mod.ci20GC

HIGH	= 1
LOW		= 0
IN   = 0
OUT  = 1


def setmode():
    rem = ctypes.c_int()
    rem = _setup()
    return rem
	
def valid(pin):
    rem = ctypes.c_int()
    rem = _valid(pin)
    return rem

def setup(pin, mode):
    rem = ctypes.c_int()
    rem = _pinMode( pin, mode)
    return rem
	
def input(pin):
    rem = ctypes.c_int()
    rem = _digitalRead(pin)
    return rem
	
def output(pin, value):
    rem = ctypes.c_int()
    rem = _digitalWrite(pin, value)
    return rem

def cleanup():
    rem = ctypes.c_int()
    rem = _cleanup()
    return rem