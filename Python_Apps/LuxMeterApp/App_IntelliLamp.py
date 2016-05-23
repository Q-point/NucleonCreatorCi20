#!/usr/bin/python

import time 
import Image
import ImageDraw
import ImageFont
import TFT as display
import APDS9300 as LuxSens
import math

print "=== Ambient light demo test  ===" 
print "********************************"

THRESHOLD = 5

def main():

	AmbientLight = LuxSens.APDS9300()					#Setup Ambient light sensor 
	
	height = display.TFT_HEIGHT
	width = display.TFT_WIDTH	
	graphicDisplay = display.TFT()	
	graphicDisplay.initialize()				# Initialize display.
	graphicDisplay.clear()					# clear screen 
	LampON = Image.open('Lamp-On.jpg')
	LampOff = Image.open('Lamp-Off.jpg')
	
	print 'Resizing...'
	LampON = LampON.rotate(90).resize((128, 160),Image.ANTIALIAS)	# Resize the image and rotate it so it's 128x160 pixels.
	LampOff = LampOff.rotate(90).resize((128, 160),Image.ANTIALIAS)	# Resize the image and rotate it so it's 128x160 pixels.
	print 'Resizing finished.'
	
	
	while True:
		channel1 = AmbientLight.readChannel(1)				#Take a reading from channel one
		channel2 = AmbientLight.readChannel(0)				#Take a reading from channel two
		Lux = AmbientLight.getLuxLevel(channel1,channel2)
			
		if(Lux > THRESHOLD):
			graphicDisplay.clear()
			graphicDisplay.display(LampON)
		else:
			graphicDisplay.clear()
			graphicDisplay.display(LampOff)

if __name__=="__main__":
    main()
    time.sleep(2)

"""
__author__ = "dhq"
__copyright__ = "Copyright 2016"
__license__ = "GPL V3"
__version__ = "1.0"
"""