from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import TFT as GLCD

disp = GLCD.TFT()		# Create TFT LCD display class.
disp.initialize()		# Initialize display.
disp.clear()			# Alternatively can clear to a black screen by calling:
draw = disp.draw()		# Get a PIL Draw object to start drawing on the display buffer

height = GLCD.TFT_HEIGHT
width = GLCD.TFT_WIDTH

while True:
	
	disp.clear()
	draw.ellipse((10, 10, 110, 80), outline=(0,255,0), fill=(0,0,255))		# Draw a blue ellipse with a green outline.
	draw.rectangle((10, 90, 110, 160), outline=(255,255,0), fill=(255,0,255))		# Draw a purple rectangle with yellow outline.
	draw.line((10, 170, 110, 230), fill=(255,255,255))	# Draw a white X.
	draw.line((10, 230, 110, 170), fill=(255,255,255))
	draw.polygon([(10, 275), (110, 240), (110, 310)], outline=(0,0,0), fill=(0,255,255))	# Draw a cyan triangle with a black outline.
	disp.display()
	time.sleep(3)
	disp.clear()
	draw.rectangle((0,0,GLCD.TFT_WIDTH,GLCD.TFT_HEIGHT), outline=0, fill=0)		#Draw a black filled box to clear the image.
	

	# First define some constants to allow easy resizing of shapes.
	padding = 2
	shape_width = 20
	top = padding
	bottom = height-padding
	# Move left to right keeping track of the current x position for drawing shapes.
	x = padding

	draw.ellipse((x, top , x+shape_width, bottom), outline=255, fill=0)		# Draw an ellipse.
	x += shape_width+padding

	draw.rectangle((x, top, x+shape_width, bottom), outline=255, fill=0)		# Draw a rectangle.
	x += shape_width+padding

	draw.polygon([(x, bottom), (x+shape_width/2, top), (x+shape_width, bottom)], outline=255, fill=0)		# Draw a triangle.
	x += shape_width+padding
	draw.line((x, bottom, x+shape_width, top), fill=255)		# Draw an X.
	draw.line((x, top, x+shape_width, bottom), fill=255)
	x += shape_width+padding
	disp.display()
	time.sleep(1)

__author__      = "dhq"
__copyright__   = "dhq May 2016"