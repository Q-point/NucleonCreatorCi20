from PIL import Image
import TFT as display
import time

graphicDisplay = display.TFT()

# Initialize display.
graphicDisplay.initialize()

image1 = Image.open('Terminator.png')

while True:
	# Load an image.
	print 'Loading image...'
	
	image1 = image1.rotate(90).resize((128, 160))		# Resize the image and rotate 
	print 'Drawing image'
	graphicDisplay.display(image1)					# Draw the image on the display hardware.
	time.sleep(3)
	
	
__author__      = "dhq"
__copyright__   = "Copyright May 2016"
