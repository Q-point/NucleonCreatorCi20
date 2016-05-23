#!/usr/bin/python

from PIL import Image

import TFT as display
import sys
import time
import FXOS8700CQR1 as imuSens

imuSens = imuSens.FXOS8700CQR1()				#Configure chip in hybrid mode
imuSens.standbyMode()	
imuSens.activeMode()

graphicDisplay = display.TFT()
graphicDisplay.initialize()					# Initialize display.

image1 = Image.open('Logo.jpg')

def L1():
	print "Landscape right.\r\n"
	image = image1.rotate(270).resize((128, 160))
	graphicDisplay.display(image)
	
def L2():
	print "Landscape left. \r\n"
	image = image1.rotate(90).resize((128, 160))
	graphicDisplay.display(image)
		
def P1():
	print "Portrait down.\r\n"
	image = image1.rotate(0).resize((128, 160))
	graphicDisplay.display(image)
		
def P2():
	print "Portrait up.\r\n" 
	image = image1.rotate(180).resize((128, 160))
	graphicDisplay.display(image)
	
options = {0 : L1,
			1 : L2,
			2 : P1,
			3 : P2
		}

imuSens.configureAccelerometer()
imuSens.configureMagnetometer()
imuSens.configureOrientation();
modeprevious = 0

while True:
	if(imuSens.readStatusReg() & 0x80):	
		orienta = imuSens.getOrientation()
		mode = (orienta >> 1) & 0x03	
		
		if (mode != modeprevious):
			options[mode]()
			
		modeprevious = mode
		
print "Shutting down"	

 
"""
__author__ = "dhq"
__copyright__ = "Copyright 2016"
__license__ = "GPL V3"
__version__ = "1.0"
"""
