#!/usr/bin/python

"""
__author__ = "D.Qendri"
__copyright__ = "Copyright 2015 Sensorian"
__license__ = "GPL V3"
__version__ = "1.0"
"""

import sys
import time
import smbus
import I2C as I2C
import logging

CAP1203ADDR  = 0x28					#Capacitive sensor address

#*****************************Registers**************************/
MAIN_CTRL_REG		=	0x00
GEN_STATUS			=	0x02
SENSOR_INPUTS		=	0x03
NOISE_FLAG			=	0x0A
SENS1DELTACOUNT		=	0x10
SENS2DELTACOUNT		=	0x11
SENS3DELTACOUNT		=	0x12
SENSITIVITY			=	0x1F
CONFIG1				=	0x20
SENSINPUTEN			=	0x21
SENSINCONF1			=	0x22
SENSINCONF2			=	0x23
AVERAGE_SAMP_CONF	=	0x24
CAL_ACTIV			=	0x26
INT_ENABLE			=	0x27
REPEAT_RATE			=	0x28
MULTITOUCH			=	0x2A
MULTIPATCONF		=	0x2B
MULTIPATTERN		=	0x2D
BASECOUNT			=	0x2E
RECALCONFIG			=	0x2F
S1THRESHOLD			=	0x30
S2THRESHOLD			=	0x31
S3THRESHOLD			=	0x32
SENSTHRESHOLD		=	0x38

STANDBYCHAN			=	0x40
STANDBYCONF			=	0x41
STANDBY_SENS		=	0x42
STANDBY_THRE		=	0x43
CONFIG2				=	0x44
S1BASECOUNT			=	0x50
S2BASECOUNT			=	0x51
S3BASECOUNT			=	0x52
PWR_BUTTON			=	0x60
PWR_CONFIG			=	0x61
S1INPCAL			=	0xB1	
S2INPCAL			=	0xB2
S3INPCAL			=	0xB3
S1CALLSB			=	0xB9

PRODUCT_ID			=	0xFD
MAN_ID				=	0xFE
REV					=	0xFF	

#************************MAIN CTRL REG********************************/
STBY				=	0x20
SLEEP				=	0x08
INT					=	0x01
#************************GEN_STATUS REG*******************************/
BC_OUT          	=	0x40
ACAL_FAIL       	=	0x20
PWR             	=	0x10
MULT            	=	0x04
MTP             	=	0x02
TOUCH           	=	0x01

#************************SENSINPUTEN REG*******************************/
CS3             	=	0x04
CS2             	=	0x02
CS1             	=	0x01

#*********************Sensitivity Control Register***************************/

#Delta sense controls the sensitivity of a touch detection for sensor inputs enabled in the Active state
MOST_SENSITIVE 		=	0x00
DEFAULT				=	0x20
LEAST_SENSITIVE		=	0x70

#*********************Configuration Register**********************************/
TIMEOUT				=	0x80
DIS_DIG_NOISE		=	0x20
DIS_ANA_NOISE		=	0x10
MAX_DUR_EN			=	0x08


#**********************Averaging and Sampling Configuration Register**********/

AVG             = 0x30            #default value 0b01100000		8 samples
SAMP_TIME       = 0x80            #0b00001000    1.28 ms
CYCLE_TIME      = 0x01

#************************Multiple Touch Configuration**************************/
MULTBLK_EN     = 0x80


#************************Multiple Touch Pattern Configuration**************************/

MTP_EN 		= 0x80
MTP_TH1		= 0x08	
MTP_TH0			= 0x04
COMP_PTRN		= 0x02
MTP_ALERT		= 0x01

#************************Multiple Touch Pattern Register**************************/

CS3_PTRN	=	0x04
CS2_PTRN	=	0x02
CS1_PTRN	=	0x01

#***********************Power Button Configuration****************************/
PWR_EN		=	0x40
TIME280ms	=	0x00
TIME560ms	=	0x01
TIME1120ms	=	0x02
TIME2240ms	=	0x03

class CAP1203(object):
	'''Capacitive touch controller. Class for CAP1203 touch sensor.'''
	MAIN_CTRL_REG = 0x00
	SENSOR_INPUTS = 0x03

	
	def  __init__(self):
		"""
		Configure sensor for capacitive touch.
		
		
		:param none: 
		:returns: none 
		"""
		self._address = CAP1203ADDR	
		self._logger = logging.getLogger('CAP1203')
		# Create I2C device.
		self._device = I2C.Device(self._address, 1)
		self.Initialize()

	def Initialize(self):
		self.activeMode()                       #All three sensors are monitored in Active mode
		self._device.write8(SENSINPUTEN,CS1|CS2|CS3)		    #Set active inputs
		self._device.write8(AVERAGE_SAMP_CONF, AVG|SAMP_TIME|CYCLE_TIME)	#Setup averaging and sampling time
		
	def  activeMode(self):
		"""
		Set the capacitive controller in active mode.
		
		:param none: 
		:returns: none
		"""
		status = self._device.readU8(MAIN_CTRL_REG)
		status &= ~STBY
		self._device.write8(MAIN_CTRL_REG,status)
		return self._device.readU8(MAIN_CTRL_REG)

		
	def  standbyMode(self):
		"""
		Set the capacitive controller in standby mode.
		
		
		:param none: 
		:returns: none
		"""
		self._device.write8(STANDBY_SENS,0x07)			      #Set sensitivity in standby mode    
		status = self._device.readU8(MAIN_CTRL_REG)
		status |= STBY
		self._device.write8(MAIN_CTRL_REG,status)
		return self._device.readU8(MAIN_CTRL_REG)
		
	def  deepSleep(self):
		"""
		Put the capacitive controller in deep sleep mode.
		
		
		:param none: 
		:returns: none
		"""
		status = self._device.readU8(MAIN_CTRL_REG)
		status |= SLEEP                            #Set Sleep bit
		self._device.write8(MAIN_CTRL_REG,status)        #Update register
		return self._device.readU8(MAIN_CTRL_REG)

	def resumeFromDeepSleep(self):
		"""
		Take the capacitive controller out of deep sleep mode.
		
		
		:param none: 
		:returns: none
		"""
		status = self._device.readU8(MAIN_CTRL_REG)
		status &= ~SLEEP
		self._device.write8(MAIN_CTRL_REG,status)
		return self._device.readU8(MAIN_CTRL_REG)

	def  configureMultiTouch(self,number,mulchan):
		"""
		Configure the capacitve touch for multitouch inputs.
		
		
		:param number: number of simultaneous touches 2 or 3
		:param chan: One of the three channels.
		:returns: none
		"""
		self._device.write8(MULTITOUCH,number|MULTBLK_EN)      							  #Set number of simultaneous touches
		self._device.write8(MULTIPATCONF,MTP_EN|MTP_TH1|MTP_TH0|COMP_PTRN|MTP_ALERT)      #Enable multitouch
		self._device.write8(MULTIPATTERN,mulchan)
		
	def multitouchEvent(self):
		"""
		Return true if a multi-touch event happened.
		
		
		:param none: 
		:returns : none 
		"""
		mt = 0
		multi = self._device.readU8(GEN_STATUS)
		if((multi & MULT) == MULT):
			mt = 1
		
		return mt
		

	def setPowerButton(self,button):
		"""
		Configure the button for power button mode.
		
		
		:param button: One of the three buttons
		:returns: none
		"""
		self._device.write8(PWR_BUTTON,button)
		self._device.write8(PWR_CONFIG,PWR_EN|TIME1120ms)		#Configure as power button in Active mode

		
	def	 readPressedButton(self):
		"""
		Read the pressed button, one of buttons 1 to 3.
		
		
		:param none: 
		:returns: key - Button pressed
		"""
		buttonPressed = 0
		status = self.getStatusReg()      #Check if touch bit was registered
		
		if (status & TOUCH):
			button = self._device.readU8(SENSOR_INPUTS)
			if(button == CS1):
				buttonPressed = 3
			elif(button == CS2):
				buttonPressed = 2
			elif(button == CS3):
				buttonPressed = 1
			else:
				buttonPressed = 0
		self._device.write8(MAIN_CTRL_REG,0x00)		#Clear interrupt
			
		return buttonPressed   

	def getStatusReg(self):
		"""Read the status register.
		
		
		:param none: 
		:returns: status - Contents of status register
		"""
		status = self._device.readU8(GEN_STATUS)
		return status

	def  enableInterrupt(self,pin):
		"""
		Enable the interrupt mode.
		
		
		:param pin: Enables interrupt on the specific pin
		:returns: none
		"""
		self._device.write8(REPEAT_RATE,pin)     #Enable repeat rate for the input pins
		self._device.write8(INT_ENABLE,pin)		#2:0 c2:c1:c0  last three bits are the specific channels

		
	def  setSensitivity(self,sensitivity):
		"""
		Configure the sensitivity of the controller.
		
		
		:param sensitivity: 
		:returns: none
		"""
		self._device.write8(0x00,sensitivity)
		
	def  checkSensorStatus(self):
		"""
		Check the current sensor status.
		
		
		:param none: 
		:returns: status - Current chip status
		"""
		return 0

		
	def  clearInterrupt(self):
		"""
		Clear any active interrupts.
		
		
		:param none: 
		:returns: none
		"""
		intStatus = 0x00
		self._device.readU8(GEN_STATUS)
		return intStatus
		
	def  readID(self):
		"""
		Read the sensor manufacturer ID.
		
		
		:param none: 
		:returns: id - Sensor ID as a number
		"""
		id = self._device.readU8(PRODUCT_ID)
		manu = self._device.readU8(MAN_ID)
		return ((manu << 8)|id)

