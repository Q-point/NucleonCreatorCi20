#!/usr/bin/python

"""
__author__ = "dhq"
__copyright__ = "Copyright 2016"
__license__ = "GPL V3"
__version__ = "1.0"
"""

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import os, sys
import sys
import smbus
import serial
import TFT as GLCD
import MPL3115A2 as altibar
import APDS9300 as LuxSens
import CAP1203 as touch
import FXOS8700CQR1 as imuSens
import CAP1203 as capTouch

CapTouch  = capTouch.CAP1203()
CapTouch.activeMode()
id = CapTouch.readID()							#Read ID of Capacitive touch controller 
print "Chip ID: 0x%04X. \r\n" % id

AmbientLight = LuxSens.APDS9300()					#Setup Ambient light sensor 
id = AmbientLight.chipID()
# print "Chip ID: 0x%02X. \r\n" % id
AltiBar = altibar.MPL3115A2()				#initialize sensor
AltiBar.ActiveMode()	#puts sensor in active mode
AltiBar.BarometerMode()	#puts sensor in active mode
	
def main(argv):
	print "========= MPL3115A2 Sensor demo ==========" 
	print "******************************************" 
	
	height = GLCD.TFT_HEIGHT
	width = GLCD.TFT_WIDTH

	disp = GLCD.TFT()		# Create TFT LCD display class.
	disp.initialize()		# Initialize display.
	disp.clear()			# Alternatively can clear to a black screen by calling:
	draw = disp.draw()		# Get a PIL Draw object to start drawing on the display buffer
	font = ImageFont.truetype('/usr/share/fonts/droid/DroidSans.ttf', 14)		# use a truetype font

	time.sleep(1)
	channel1 = AmbientLight.readChannel(1)				#Take a reading from channel one
	print "Channel 1 value: %d." % channel1		
	channel2 = AmbientLight.readChannel(0)				#Take a reading from channel two
	print "Channel 2 value: %d" % channel2
	Lux = AmbientLight.getLuxLevel(channel1,channel2)
	print "Lux output: %d." % Lux
	
	button = NoPress							#reset button
	button = CapTouch.readPressedButton()		#poll for new press
	if (button != NoPress):
		print "Button B%d pressed.\r\n"  % int(button)
			
	
	ser = serial.Serial('/dev/ttyS0',115200,timeout=3) 	# Open the serial port
	ser.write("X-shield UART Demo\r\n")					# Write a serial string to the serial port
	for num in range(1,10):
		ser.write("Number" + str(num) + "\r\n") 					# Write a serial string to the serial port
	
	print "Serial closed"
	ser.close()	
	imuSens = imuSens.FXOS8700CQR1()				#Configure chip in hybrid mode
	id = imuSens.getID()					#Verify chip ID
	print "Chip ID: 0x%02X. \r\n" % id
	imuSens.standbyMode()	
	# imuSens.writeByte(0x0B,0x01)		#Set to wake up 	
	imuSens.activeMode()
	
	while True:
		if(imuSens.readStatusReg() & 0x80):
			x,y,z = imuSens.pollAccelerometer()
			print "Accelerometer data x: %d, y: %d, z: %d \r\n"  % (x, y, z)
			
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
		
