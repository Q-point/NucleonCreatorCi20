#!/usr/bin/python
import time 
import Image
import ImageDraw
import ImageFont
import TFT as GLCD
import APDS9300 as LuxSens
import math

print "=== Ambient light demo test  ===" 
print "********************************" 

AmbientLight = LuxSens.APDS9300()					#Setup Ambient light sensor 
id = AmbientLight.chipID()
print "Chip ID: 0x%02X. \r\n" % id

def main():
	height = GLCD.TFT_HEIGHT
	width = GLCD.TFT_WIDTH

	disp = GLCD.TFT()		# Create TFT LCD display class.
	disp.initialize()		# Initialize display.
	disp.clear()			# Alternatively can clear to a black screen by calling:
	draw = disp.draw()		# Get a PIL Draw object to start drawing on the display buffer
	var = 0
	
	while True:
		channel1 = AmbientLight.readChannel(1)				#Take a reading from channel one
		channel2 = AmbientLight.readChannel(0)				#Take a reading from channel two
		Lux = AmbientLight.getLuxLevel(channel1,channel2)
		font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 14)		# use a truetype font
		draw.text((20, 80), "Ambient Light", font=font)
		draw.text((40, 100), "CH1: " + str(channel1), font=font)
		draw.text((40, 120), "CH2: " + str(channel2), font=font)	
		draw.text((30, 140), "LUX: " + str(Lux), font=font)			
		disp.display()
		
		padding = 2
		shape_width = 20
		top = padding
		bottom = height-padding
		#Move left to right keeping track of the current x position for drawing shapes.
		x = padding
		lev = int(Lux)
		draw.ellipse((20, 10, 110, 80), outline=int(channel2), fill=(int(channel2),int(channel2),int(channel2)))
		draw.text((30, 40),'LUX Level',  font=font, fill=255)		# Write two lines of text.

		disp.display()		
		time.sleep(2)
		disp.clear()

if __name__=="__main__":
    main()

"""
__author__ = "dhq"
__copyright__ = "Copyright 2016"
__license__ = "GPL V3"
__version__ = "1.0"
"""