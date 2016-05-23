#!/usr/bin/python

from PIL import Image
import TFT as display
import time

graphicDisplay = display.TFT()							# Initialize display.
graphicDisplay.initialize()

image1 = Image.open('Terminator.png')

while True:
	print 'Loading image...'							# Load an image.
	image1 = image1.rotate(90).resize((128, 160))		# Resize the image and rotate it so it's 240x320 pixels.
	print 'Drawing image'
	graphicDisplay.display(image1)						# Draw the image on the display hardware.
	time.sleep(3)
	
	
