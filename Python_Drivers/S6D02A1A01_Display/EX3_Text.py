from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import TFT as GLCD

def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
	# Get rendered font width and height.
	draw = ImageDraw.Draw(image)
	width, height = draw.textsize(text, font=font)
	# Create a new image with transparent background to store the text.
	textimage = Image.new('RGBA', (width, height), (0,0,0,0))
	# Render the text.
	textdraw = ImageDraw.Draw(textimage)
	textdraw.text((0,0), text, font=font, fill=fill)
	# Rotate the text image.
	rotated = textimage.rotate(angle, expand=1)
	# Paste the text into the image, using it as a mask for transparency.
	image.paste(rotated, position, rotated)
	

def main():
	height = GLCD.TFT_HEIGHT
	width = GLCD.TFT_WIDTH

	disp = GLCD.TFT()		# Create TFT LCD display class.
	disp.initialize()		# Initialize display.
	disp.clear()			# Alternatively can clear to a black screen by calling:
	draw = disp.draw()		# Get a PIL Draw object to start drawing on the display buffer
	var = 0
	
	while True:
		var += 1
		font = ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSans-Bold.ttf', 14)		# use a truetype font
		draw.text((40, 80), "FreeSans", font=font)
		draw.text((50, 100), str(var), font=font)
		disp.display()
		time.sleep(1)
		disp.clear()
		
		padding = 2
		shape_width = 20
		top = padding
		bottom = height-padding
		# Move left to right keeping track of the current x position for drawing shapes.
		x = padding		
		draw.text((40, top),    'Red ',  font=font, fill=255)		# Write two lines of text.
		draw.text((x, top+20), 'Text on this line!', font=font, fill=255)		
		disp.display()		
		time.sleep(1)
		disp.clear()

if __name__=="__main__":
    main()
	
__author__      = "Dhimiter Qendri"
__copyright__   = "Copyright June 2015"