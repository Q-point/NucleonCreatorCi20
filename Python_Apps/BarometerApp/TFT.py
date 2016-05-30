#!/usr/bin/python

"""
__author__ = "dhq"
__copyright__ = "Copyright 2016"
__license__ = "GPL V3"
__version__ = "1.0"
"""

import numbers
import time
from PIL import Image
from PIL import ImageDraw
import Ci20GPIO as GPIO
import spidev as spi

spi = spi.SpiDev()

# Constants for interacting with display registers.
TFT_WIDTH    = 128
TFT_HEIGHT   = 160

NOP         = 0x00
SWRESET     = 0x01
RDDID       = 0x04
RDDST       = 0x09

SLPIN       = 0x10
SLPOUT      = 0x11
PTLON       = 0x12
NORON       = 0x13

RDMODE      = 0x0A
RDMADCTL    = 0x0B
RDPIXFMT    = 0x0C
RDIMGFMT    = 0x0A
RDSELFDIAG  = 0x0F

INVOFF      = 0x20
INVON       = 0x21
GAMMASET    = 0x26
DISPOFF     = 0x28
DISPON      = 0x29

CASET       = 0x2A
PASET       = 0x2B
RAMWR       = 0x2C
RAMRD       = 0x2E

PTLAR       = 0x30
MADCTL      = 0x36
PIXFMT      = 0x3A

FRMCTR1     = 0xB1
FRMCTR2     = 0xB2
FRMCTR3     = 0xB3
INVCTR      = 0xB4
DFUNCTR     = 0xB6

PWCTR1      = 0xC0
PWCTR2      = 0xC1
PWCTR3      = 0xC2
PWCTR4      = 0xC3
PWCTR5      = 0xC4
VMCTR1      = 0xC5
VMCTR2      = 0xC7

RDID1       = 0xDA
RDID2       = 0xDB
RDID3       = 0xDC
RDID4       = 0xDD

GMCTRP1     = 0xE0
GMCTRN1     = 0xE1

PWCTR6      = 0xFC

BLACK       = 0x0000
BLUE        = 0x001F
RED         = 0xF800
GREEN       = 0x07E0
CYAN        = 0x07FF
MAGENTA     = 0xF81F
YELLOW      = 0xFFE0  
WHITE       = 0xFFFF

#####################################################

MADCTL_MY  = 0x80
MADCTL_MX  = 0x40
MADCTL_MV  = 0x20
MADCTL_ML  = 0x10
MADCTL_MH  = 0x04

MADCTL_M1  = 0x00
MADCTL_M2  = 0b10000000
MADCTL_M3  = 0b01000000
MADCTL_M4  = 0b11000000
MADCTL_M5  = 0b00100000
MADCTL_M6  = 0b10100000
MADCTL_M7  =  0b01100000
MADCTL_M8  =  0b11100000

MADCTL_RGB  = 0x00
MADCTL_BGR  = 0x08

WIDTH  =  0x7F       # 127
HEIGHT = 0x9F        # 159

#####################################################
DC = 6
RST = 4
TFT_CS = 9

ROWS = 6
COLUMNS = 14
PIXELS_PER_ROW = 6
ON = 1
OFF = 0

CLSBUF=[0]*(ROWS * COLUMNS * PIXELS_PER_ROW)

FONT = {
  ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
  '!': [0x00, 0x00, 0x5f, 0x00, 0x00],
  '"': [0x00, 0x07, 0x00, 0x07, 0x00],
  '#': [0x14, 0x7f, 0x14, 0x7f, 0x14],
  '$': [0x24, 0x2a, 0x7f, 0x2a, 0x12],
  '%': [0x23, 0x13, 0x08, 0x64, 0x62],
  '&': [0x36, 0x49, 0x55, 0x22, 0x50],
  "'": [0x00, 0x05, 0x03, 0x00, 0x00],
  '(': [0x00, 0x1c, 0x22, 0x41, 0x00],
  ')': [0x00, 0x41, 0x22, 0x1c, 0x00],
  '*': [0x14, 0x08, 0x3e, 0x08, 0x14],
  '+': [0x08, 0x08, 0x3e, 0x08, 0x08],
  ',': [0x00, 0x50, 0x30, 0x00, 0x00],
  '-': [0x08, 0x08, 0x08, 0x08, 0x08],
  '.': [0x00, 0x60, 0x60, 0x00, 0x00],
  '/': [0x20, 0x10, 0x08, 0x04, 0x02],
  '0': [0x3e, 0x51, 0x49, 0x45, 0x3e],
  '1': [0x00, 0x42, 0x7f, 0x40, 0x00],
  '2': [0x42, 0x61, 0x51, 0x49, 0x46],
  '3': [0x21, 0x41, 0x45, 0x4b, 0x31],
  '4': [0x18, 0x14, 0x12, 0x7f, 0x10],
  '5': [0x27, 0x45, 0x45, 0x45, 0x39],
  '6': [0x3c, 0x4a, 0x49, 0x49, 0x30],
  '7': [0x01, 0x71, 0x09, 0x05, 0x03],
  '8': [0x36, 0x49, 0x49, 0x49, 0x36],
  '9': [0x06, 0x49, 0x49, 0x29, 0x1e],
  ':': [0x00, 0x36, 0x36, 0x00, 0x00],
  ';': [0x00, 0x56, 0x36, 0x00, 0x00],
  '<': [0x08, 0x14, 0x22, 0x41, 0x00],
  '=': [0x14, 0x14, 0x14, 0x14, 0x14],
  '>': [0x00, 0x41, 0x22, 0x14, 0x08],
  '?': [0x02, 0x01, 0x51, 0x09, 0x06],
  '@': [0x32, 0x49, 0x79, 0x41, 0x3e],
  'A': [0x7e, 0x11, 0x11, 0x11, 0x7e],
  'B': [0x7f, 0x49, 0x49, 0x49, 0x36],
  'C': [0x3e, 0x41, 0x41, 0x41, 0x22],
  'D': [0x7f, 0x41, 0x41, 0x22, 0x1c],
  'E': [0x7f, 0x49, 0x49, 0x49, 0x41],
  'F': [0x7f, 0x09, 0x09, 0x09, 0x01],
  'G': [0x3e, 0x41, 0x49, 0x49, 0x7a],
  'H': [0x7f, 0x08, 0x08, 0x08, 0x7f],
  'I': [0x00, 0x41, 0x7f, 0x41, 0x00],
  'J': [0x20, 0x40, 0x41, 0x3f, 0x01],
  'K': [0x7f, 0x08, 0x14, 0x22, 0x41],
  'L': [0x7f, 0x40, 0x40, 0x40, 0x40],
  'M': [0x7f, 0x02, 0x0c, 0x02, 0x7f],
  'N': [0x7f, 0x04, 0x08, 0x10, 0x7f],
  'O': [0x3e, 0x41, 0x41, 0x41, 0x3e],
  'P': [0x7f, 0x09, 0x09, 0x09, 0x06],
  'Q': [0x3e, 0x41, 0x51, 0x21, 0x5e],
  'R': [0x7f, 0x09, 0x19, 0x29, 0x46],
  'S': [0x46, 0x49, 0x49, 0x49, 0x31],
  'T': [0x01, 0x01, 0x7f, 0x01, 0x01],
  'U': [0x3f, 0x40, 0x40, 0x40, 0x3f],
  'V': [0x1f, 0x20, 0x40, 0x20, 0x1f],
  'W': [0x3f, 0x40, 0x38, 0x40, 0x3f],
  'X': [0x63, 0x14, 0x08, 0x14, 0x63],
  'Y': [0x07, 0x08, 0x70, 0x08, 0x07],
  'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
  '[': [0x00, 0x7f, 0x41, 0x41, 0x00],
  '\\': [0x02, 0x04, 0x08, 0x10, 0x20],
  ']': [0x00, 0x41, 0x41, 0x7f, 0x00],
  '^': [0x04, 0x02, 0x01, 0x02, 0x04],
  '_': [0x40, 0x40, 0x40, 0x40, 0x40],
  '`': [0x00, 0x01, 0x02, 0x04, 0x00],
  'a': [0x20, 0x54, 0x54, 0x54, 0x78],
  'b': [0x7f, 0x48, 0x44, 0x44, 0x38],
  'c': [0x38, 0x44, 0x44, 0x44, 0x20],
  'd': [0x38, 0x44, 0x44, 0x48, 0x7f],
  'e': [0x38, 0x54, 0x54, 0x54, 0x18],
  'f': [0x08, 0x7e, 0x09, 0x01, 0x02],
  'g': [0x0c, 0x52, 0x52, 0x52, 0x3e],
  'h': [0x7f, 0x08, 0x04, 0x04, 0x78],
  'i': [0x00, 0x44, 0x7d, 0x40, 0x00],
  'j': [0x20, 0x40, 0x44, 0x3d, 0x00],
  'k': [0x7f, 0x10, 0x28, 0x44, 0x00],
  'l': [0x00, 0x41, 0x7f, 0x40, 0x00],
  'm': [0x7c, 0x04, 0x18, 0x04, 0x78],
  'n': [0x7c, 0x08, 0x04, 0x04, 0x78],
  'o': [0x38, 0x44, 0x44, 0x44, 0x38],
  'p': [0x7c, 0x14, 0x14, 0x14, 0x08],
  'q': [0x08, 0x14, 0x14, 0x18, 0x7c],
  'r': [0x7c, 0x08, 0x04, 0x04, 0x08],
  's': [0x48, 0x54, 0x54, 0x54, 0x20],
  't': [0x04, 0x3f, 0x44, 0x40, 0x20],
  'u': [0x3c, 0x40, 0x40, 0x20, 0x7c],
  'v': [0x1c, 0x20, 0x40, 0x20, 0x1c],
  'w': [0x3c, 0x40, 0x30, 0x40, 0x3c],
  'x': [0x44, 0x28, 0x10, 0x28, 0x44],
  'y': [0x0c, 0x50, 0x50, 0x50, 0x3c],
  'z': [0x44, 0x64, 0x54, 0x4c, 0x44],
  '{': [0x00, 0x08, 0x36, 0x41, 0x00],
  '|': [0x00, 0x00, 0x7f, 0x00, 0x00],
  '}': [0x00, 0x41, 0x36, 0x08, 0x00],
  '~': [0x10, 0x08, 0x08, 0x10, 0x08],
  '\x7f': [0x00, 0x7e, 0x42, 0x42, 0x7e],
}

ORIGINAL_CUSTOM = FONT['\x7f']

def color565(r, g, b):
	"""
	Convert red, green, blue components to a 16-bit 565 RGB value. 
	Components should be values 0 to 255.
	:param r: Red byte.
	:param g: Green byte.
	:param b: Blue byte.
	:returns pixel : 16-bit 565 RGB value
	"""
	return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def image_to_data(image):
	"""Generator function to convert a PIL image to 16-bit 565 RGB bytes.
	:param image: PIL image
	:returns imgArray : 
	"""
	pixels = image.convert('RGB').load()
	width, height = image.size
	for y in range(height):
		for x in range(width):
			r,g,b = pixels[(x,y)]
			color = color565(r, g, b)
			yield (color >> 8) & 0xFF
			yield color & 0xFF


class TFT(object):
	"""Representation of an S6D02A1A01 TFT lcd controller."""

	def __init__(self):
		""" Creates a TFT object and configures SPI bus and pins.
		:param none: 
		:returns none :
		"""
		self.dc = DC
		self.rst = RST
		self.width = TFT_WIDTH
		self.height = TFT_HEIGHT
		
		GPIO.setmode()		
		GPIO.setup(self.dc, GPIO.OUT)	# Set DC as output.
		# Setup reset as output (if provided).
		if self.rst is not None:
			GPIO.setup(self.rst, GPIO.OUT)
		# Set SPI to mode 0, MSB first.
		spi.open(32766,0)
		spi.max_speed_hz = 20000000
		# Create an image buffer.
		self.buffer = Image.new('RGB', (self.width, self.height))

	def send(self, data, dataOrCmd=True, length=4096):
		"""
		Writes a byte or array of bytes to the display. 
		dataOrCmd parameter controls if byte should be interpreted as display data (True)/ command data otherwise.  
		Length is an optional size of bytes to write in a single SPI transaction, with a default of 4096. 
		:param data: Single byte or an array of bytes.
		:param dataOrCmd: Flag for command or data mode
		:param length: size of array
		:returns none :
		"""
		# Set DC low for command, high for data.
		GPIO.output(self.dc, dataOrCmd)
		# Convert scalar argument to list so either can be passed as parameter.
		if isinstance(data, numbers.Number):
			data = [data & 0xFF]
		# Write data a chunk at a time.
		for start in range(0, len(data), length):
			end = min(start+length, len(data))
			spi.writebytes(data[start:end])

	def command(self, data):
		"""
		Write a byte or array of bytes to the display as command data.
		:param data: Single byte command.
		:returns none :
		"""
		self.send(data, False)

	def data(self, data):
		"""Write a byte or array of bytes to the display as display data.
		:param data: Data byte
		:returns none :
		"""
		self.send(data, True)

	def reset(self):
		"""Resets the display, (RST) reset pin must be connected.
		:param none: 
		:returns none :
		"""
		if self._rst is not None:
			GPIO.output(self.rst,1)
			time.sleep(0.005)
			GPIO.output(self.rst,0)
			time.sleep(0.02)
			GPIO.output(self.rst,1)
			time.sleep(0.150)

	def initialize(self):
		"""Intializes the display controller and prepares the it for any subsequent operations. 
		:param none: 
		:returns none :
		"""
	
		GPIO.setup(self.dc, GPIO.OUT)
		GPIO.setup(self.rst, GPIO.OUT)
		
		#self._gpio.output(24, 0)
		GPIO.output(self.dc, 0)
		GPIO.output(self.rst, 1)

		self.command(0xf0)
		self.data(0x5a)
		self.data(0x5a)

		self.command(0xfc)
		self.data(0x5a)
		self.data(0x5a)

		self.command(0x26)
		self.data(0x01)

		self.command(0xfa)
		self.data(0x02)
		self.data(0x1f)
		self.data(0x00)
		self.data(0x10)
		self.data(0x22)
		self.data(0x30)
		self.data(0x38)
		self.data(0x3A)
		self.data(0x3A)
		self.data(0x3A)
		self.data(0x3A)
		self.data(0x3A)
		self.data(0x3d)
		self.data(0x02)
		self.data(0x01)

		self.command(0xfb)
		self.data(0x21)
		self.data(0x00)
		self.data(0x02)
		self.data(0x04)
		self.data(0x07)
		self.data(0x0a)
		self.data(0x0b)
		self.data(0x0c)
		self.data(0x0c)
		self.data(0x16)
		self.data(0x1e)
		self.data(0x30)
		self.data(0x3f)
		self.data(0x01)
		self.data(0x02)

		#power setting sequence
		self.command(0xfd)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x17)
		self.data(0x10)
		self.data(0x00)
		self.data(0x01)
		self.data(0x01)
		self.data(0x00)
		self.data(0x1f)
		self.data(0x1f)

		self.command(0xf4)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x3f)
		self.data(0x3f)
		self.data(0x07)
		self.data(0x00)
		self.data(0x3C)
		self.data(0x36)
		self.data(0x00)
		self.data(0x3C)
		self.data(0x36)
		self.data(0x00)
		time.sleep(0.08)			   

		self.command(0xf5)
		self.data(0x00)
		self.data(0x70)		#39
		self.data(0x66)		#3a
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x6d)		#38
		self.data(0x66)		#38
		self.data(0x06)

		self.command(0xf6)
		self.data(0x02)
		self.data(0x00)
		self.data(0x3f)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x02)
		self.data(0x00)
		self.data(0x06)
		self.data(0x01)
		self.data(0x00)

		self.command(0xf2)
		self.data(0x00)
		self.data(0x01)	#04
		self.data(0x03)
		self.data(0x08)
		self.data(0x08)
		self.data(0x04)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x01)
		self.data(0x00)
		self.data(0x00)
		self.data(0x04)
		self.data(0x08)
		self.data(0x08)

		self.command(0xf8)
		self.data(0x11)	#66

		self.command(0xf7)
		self.data(0xc8)
		self.data(0x20)
		self.data(0x00)
		self.data(0x00)

		self.command(0xf3)
		self.data(0x00)
		self.data(0x00)

		self.command(0x11)

		self.command(0xf3)
		self.data(0x00)
		self.data(0x01)
		time.sleep(0.05)
		self.command(0xf3)
		self.data(0x00)
		self.data(0x03)
		time.sleep(0.05)
		self.command(0xf3)
		self.data(0x00)
		self.data(0x07)
		time.sleep(0.05)
		self.command(0xf3)
		self.data(0x00)
		self.data(0x0f)
		time.sleep(0.05)

		self.command(0xf4)
		self.data(0x00)
		self.data(0x04)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x3f)
		self.data(0x3f)
		self.data(0x07)
		self.data(0x00)
		self.data(0x3C)
		self.data(0x36)
		self.data(0x00)
		self.data(0x3C)
		self.data(0x36)
		self.data(0x00)

		self.command(0xf3)
		self.data(0x00)
		self.data(0x1f)
		time.sleep(0.05)
		self.command(0xf3)
		self.data(0x00)
		self.data(0x7f)

		self.command(0xf3)
		self.data(0x00)
		self.data(0xff)

		self.command(0xfd)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x17)
		self.data(0x10)
		self.data(0x00)
		self.data(0x00)
		self.data(0x01)
		self.data(0x00)
		self.data(0x16)
		self.data(0x16)

		self.command(0xf4)
		self.data(0x00)
		self.data(0x09)
		self.data(0x00)
		self.data(0x00)
		self.data(0x00)
		self.data(0x3f)
		self.data(0x3f)
		self.data(0x07)
		self.data(0x00)
		self.data(0x3C)
		self.data(0x36)
		self.data(0x00)
		self.data(0x3C)
		self.data(0x36)
		self.data(0x00)

		#initializing sequence

		self.command(0x36)
		self.data(0x08)

		self.command(0x35)
		self.data(0x00)
		self.command(0x3a)
		self.data(0x05)
		#gamma setting sequence
		self.command(0x29)
		self.command(0x2c)

	def set_window(self, x0=0, y0=0, x1=None, y1=None):
		"""Set the pixel address window for proceeding drawing commands. 
		:param x0: x0 and x1 should define the minimum and maximum x pixel bounds.
		:param y0:
		:param x1: y0 and y1 should define the minimum and maximum y pixel bound.
		:param y1:
		:returns none :
		"""
		if x1 is None:
			x1 = self.width-1
		if y1 is None:
			y1 = self.height-1
		self.command(CASET)		# Column addr set
		self.data(x0 >> 8)
		self.data(x0)					# XSTART 
		self.data(x1 >> 8)
		self.data(x1)					# XEND
		self.command(PASET)		# Row addr set
		self.data(y0 >> 8)
		self.data(y0)					# YSTART
		self.data(y1 >> 8)
		self.data(y1)					# YEND
		self.command(RAMWR)		# write to RAM

	def display(self, image=None):
		"""Write the provided image to the hardware. If no image parameter is provided the display buffer will be written to the hardware.  
		If an image is provided, it should be RGB format and the same dimensions as the display hardware.
		:param image: 
		:returns none :
		"""
		# By default write the internal buffer to the display.
		if image is None:
			image = self.buffer
		# Set address bounds to entire display.
		self.set_window()
		# Convert image to array of 16bit 565 RGB data bytes.
		# Unfortunate that this copy has to occur, but the SPI byte writing
		# function needs to take an array of bytes and PIL doesn't natively
		# store images in 16-bit 565 RGB format.
		pixelbytes = list(image_to_data(image))
		# Write data to hardware.
		self.data(pixelbytes)

	def clear(self, color=(0,0,0)):
		"""Clear the image buffer to the specified RGB color (default black).
		:param color: Background color. 
		:returns none :
		"""
		width, height = self.buffer.size
		self.buffer.putdata([color]*(width*height))

	def draw(self):
		"""Return a PIL ImageDraw instance for 2D drawing on the image buffer.
		:param none: 
		:returns none :
		"""
		return ImageDraw.Draw(self.buffer)
	
	def display_char(self,char, font=FONT):
		"""
		:param none: 
		:returns none :
		"""
		try:
			self.data(font[char]+[0])
		except KeyError:
			pass # Ignore undefined characters.


	def text(string, font=FONT):
		"""Plot an ASCII char on the display. A specific font is used.
		:param font:  FONT used for glyphs
		:returns none :
		"""
		for char in string:
			self.display_char(char, font)
			
	def invert(self,status):
		"""Disables color inversion on the display.
		:param status:  Color inversion status.
		:returns none :
		"""
		if (status == False):
			self.command(INVERSION_OFF)
		else:
			self.command(INVERSION_ON)
	
	def setRotation(self,mode):	
		"""Sets the display text orientation. Mirrored modes are 
			also supported on top of portrait and landscape modes.
		:param mode: orientation data   
		:returns none :
		"""
		self.command(MADCTL)
		if (mode == 0x00):
			 self.data(MADCTL_MY | MADCTL_MX| MADCTL_BGR)	#portrait
		elif (mode == 0x01):
			 self.data(MADCTL_MV |MADCTL_ML| MADCTL_BGR)	#Landscape mode reflected 
		elif (mode == 0x02):
			 self.data(MADCTL_MY | MADCTL_BGR)				#Portrait mode reflected 
		elif (mode == 0x03):
			 self.data(MADCTL_MX | MADCTL_BGR)				#Portarit mode inverted and reflected
		elif (mode == 0x04):
			 self.data(MADCTL_MV | MADCTL_BGR | MADCTL_MX)	#Landscape mode inverted 
		elif (mode == 0x05):
			 self.data(MADCTL_ML | MADCTL_BGR)				#Portrait inverted 
		elif (mode == 0x06):
			 self.data(MADCTL_MV|MADCTL_MY | MADCTL_BGR)	#Landscape mode 
		else :
			 self.data(MADCTL_M8 | MADCTL_BGR)				#Landscape mode reflected and inverted

	def	sleep(self):
		"""Return a PIL ImageDraw instance for 2D drawing on the image buffer.
		:param none: 
		:returns none :
		"""
		self.command(SLEEP_IN)
		time.sleep(0.005)

	def wakeUp(self):
		"""Wakes the display from sleep mode.
		:param none: 
		:returns none :
		"""
		self.command(SLEEP_OUT)
		time.sleep(0.120)

	def turnOff(self):
		"""Blanks out the display.
		:param none: 
		:returns none :
		"""
		self.command(DISPLAY_OFF)

	def turnOn(self):
		"""This function turn on the display from idle mode.
		:param none: 
		:returns none :
		"""
		self.command(DISPLAY_ON)

__author__      = "Dhimiter Qendri"
__copyright__   = "Copyright June 2015"