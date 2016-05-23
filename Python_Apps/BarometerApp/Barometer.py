#!/usr/bin/python
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import os, sys
import sys
import TFT as GLCD
import MPL3115A2 as altibar

def main(argv):
	print "========= MPL3115A2 Sensor demo ==========" 
	print "******************************************" 
	
	AltiBar = altibar.MPL3115A2()				#initialize sensor
	AltiBar.ActiveMode()	#puts sensor in active mode
	AltiBar.BarometerMode()	#puts sensor in active mode

	height = GLCD.TFT_HEIGHT
	width = GLCD.TFT_WIDTH

	disp = GLCD.TFT()		# Create TFT LCD display class.
	disp.initialize()		# Initialize display.
	disp.clear()			# Alternatively can clear to a black screen by calling:
	draw = disp.draw()		# Get a PIL Draw object to start drawing on the display buffer
	font = ImageFont.truetype('/usr/share/fonts/droid/DroidSans-Bold.ttf', 14)		# use a truetype font

	
	
	while True:
		press =  AltiBar.ReadBarometricPressure()		#Take a pressure reading
		time.sleep(1)
		draw.text((30, 10), "Pressure (Pa)", font=font)
		draw.text((30, 30), str(press), font=font)		
		disp.display()
		time.sleep(5)
		disp.clear()


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("")
		
"""
__author__ = "dhq"
__copyright__ = "Copyright 2016"
__license__ = "GPL V3"
__version__ = "1.0"
"""