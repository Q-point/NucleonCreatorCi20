#!/usr/bin/env python

"""
__author__ = "D.Qendri"
__copyright__ = "Copyright 2016"
__license__ = "GPL V3"
__version__ = "1.0"
"""

import sys
import smbus
import time
import math
import I2C as I2C
import logging

MPL3115A2_ADDRESS  = 0x60 			#7-bit I2C address for sensor

#Sensor Memory map
STATUS             =  0x00
OUT_P_MSB          =  0x01        
OUT_P_CSB          =  0x02
OUT_P_LSB          =  0x03
OUT_T_MSB          =  0x04
OUT_T_LSB          =  0x05
DR_STATUS          =  0x06
OUT_P_DELTA_MSB    =  0x07
OUT_P_DELTA_CSB    =  0x08
OUT_P_DELTA_LSB    =  0x09
OUT_T_DELTA_MSB    =  0x0A
OUT_T_DELTA_LSB    =  0x0B
WHO_AM_I           =  0x0C
F_STATUS           =  0x0D
F_DATA             =  0x0E
F_SETUP            =  0x0F
TIME_DLY           =  0x10
SYSMOD             =  0x11
INT_SOURCE         =  0x12
PT_DATA_CFG        =  0x13
BAR_IN_MSB         =  0x14
BAR_IN_LSB         =  0x15
P_TGT_MSB          =  0x16
P_TGT_LSB          =  0x17
T_TGT              =  0x18
P_WND_MSB          =  0x19
P_WND_LSB          =  0x1A
T_WND              =  0x1B
P_MIN_MSB          =  0x1C
P_MIN_CSB          =  0x1D
P_MIN_LSB          =  0x1E
T_MIN_MSB          =  0x1F
T_MIN_LSB          =  0x20
P_MAX_MSB          =  0x21
P_MAX_CSB          =  0x22
P_MAX_LSB          =  0x23
T_MAX_MSB          =  0x24
T_MAX_LSB          =  0x25
CTRL_REG1          =  0x26
CTRL_REG2          =  0x27
CTRL_REG3          =  0x28
CTRL_REG4          =  0x29
CTRL_REG5          =  0x2A
OFF_P              =  0x2B
OFF_T              =  0x2C
OFF_H              =  0x2D



#*********************Status **************************************/
PTDR    = 0x04      #Pressure/Altitude OR Temperature data ready
PDR     = 0x02      #Pressure/Altitude new data available
TDR     = 0x01      #Temperature new Data Available.


#*********************Control Register 1****************************/
ALT    =  0x80
RAW    =  0x40
OS2    =  0x20
OS1    =  0x10
OS0    =  0x08
RST    =  0x04
OST    =  0x02
SBYB   =  0x01        #Active mode

# Oversample Ratio 1
OS_1   = 0x00                   #  6 ms min between samples
OS_2   = OS0					#  10 ms
OS_4   = OS1					#  18 ms
OS_8   = OS1 | OS0              #  34 ms
OS_16  = OS2                    #  66 ms
OS_32  = OS2 | OS0              # 130 ms
OS_64  = OS2 | OS1              # 258 ms
OS_128 = OS2 | OS1 | OS2        # 512 ms

BAR_MASK        = 0x80
ALT_MASK        = 0xEF
ACTIVE_MASK     = 0xF1
STANDBY_MASK    = 0xFE


#*********************Control Register 5****************************/

DISABLED    = 0x00
CIRCULAR    = 0x40
FULL_STOP   = 0x80
F_MODE      = DISABLED
#*****************PT_DATA_CFG - Sensor data event flag register***********/
DREM     	= 0x04			# Data Ready Event Mode
PDEFE    	= 0x02 			# Pressure Data Event Flag Enabled
TDEFE    	= 0x01 			# Temperature Data Event Flag Enabled

class MPL3115A2(object):

	def __init__(self):
		"""
		Initializes I2C bus if not initizalized and configures sensor in active mode.
		
		
		:param none: 
		:returns none:
		"""
		self._address = MPL3115A2_ADDRESS
		
		self._logger = logging.getLogger('MPL3115A2')
		# Create I2C device.
		self._device = I2C.Device(self._address, 1)
		self.initialize()
		
	
	def initialize(self):
		"""
		Initializes I2C bus if not initizalized and configures sensor in active mode.
		
		
		:param none: 
		:returns none:
		"""
		self.StandbyMode()
		self._device.write8(PT_DATA_CFG, DREM | PDEFE | TDEFE)		#Enable data ready flags for pressure and temperature )	
		self._device.write8(CTRL_REG1, OS_128 | SBYB)					#set sensor to active state with oversampling ratio 128 (512 ms between samples)	
	

	def GetMode(self):
		"""
		Return a bool value indicating wheather the sensor is in Active or Standby mode.
		
		
		:param none: 
		:returns Mode: 1 if in Active mode, 0 otherwise
		"""
		status = self._device.readU8(SYSMOD);
		if(status & 0x01):
			return 1
		else :
			return 0

	def GetID(self):
		"""
		Returns the Factory Sensor ID.
		
		
		:param none: 
		:returns id: Factory ID
		"""
		a = self._device.readU8(WHO_AM_I);
		return a

	def ReadBarometricPressure(self):
		"""
		Reads the current pressure in Pa.
		
		:param none: 
		:returns none: Returns -1 if no new data is available
		"""
		# return sensor.MPL3115A2_ReadBarometricPressure()
		status = self._device.readU8(STATUS)
		
		#Check PDR bit, if it's not set then toggle OST
		if((status & (1<< PDR)) == 0): 	
			self.ToggleOneShot()		#Toggle the OST bit causing the sensor to immediately take another reading
		
		m_pressure = self._device.readU8(OUT_P_MSB)
		c_pressure = self._device.readU8(OUT_P_CSB)
		l_pressure = self._device.readU8(OUT_P_LSB)
		pressure_whole = long (m_pressure<<16) | long(c_pressure<<8) | long (l_pressure)			# Pressure comes back as a left shifted 20 bit number
		pressure_whole >>= 6                       						#Pressure is an 18 bit number with 2 bits of decimal. Get rid of decimal portion.
		c_pressure &= 0b00110000                         				# Bits 5/4 represent the fractional component
		c_pressure >>= 4                                  				# Get it right aligned
		pressure_decimal = float(((c_pressure&0x30)>>4)/4.0) 			# Turn it into fraction
		pressure = float(pressure_whole + pressure_decimal)
		return pressure

	def ToggleOneShot(self):
		"""
		Reads the current temperature in degrees Celcius.
		
		
		:param none: 
		:returns temp: Returns temperature as a float.
		"""
		tempSetting = self._device.readU8(CTRL_REG1)					#Read current settings
		tempSetting &= ~(1<<1)	                                 #Clear OST bit
		self._device.write8(CTRL_REG1, tempSetting)	
		tempSetting = self._device.readU8(CTRL_REG1)              #Read current settings to be safe
		tempSetting |= (1<<1)	                                    #Set OST bit
		self._device.write8(CTRL_REG1, tempSetting)
	
	
	
	def ReadTemperature(self):
		"""
		Reads the current temperature in degrees Celcius.
		
		
		:param none: 
		:returns temp: Returns temperature as a float.
		"""
		# return sensor.MPL3115A2_ReadTemperature()
		t_MSB = self._device.readU8(OUT_T_MSB)
		t_LSB = self._device.readU8(OUT_T_LSB)
		templsb = float((t_LSB >>4) / 16.0) 			#temp, fraction of a degree
		temperature = float(t_MSB + templsb)			#
		return temperature

	def BarometerMode(self):
		"""
		Sets the sensor in Barometer mode.
		
		
		:param none: 
		:returns none:
		"""
		ctrl_reg = self._device.readU8(CTRL_REG1)			#Read current settings
		ctrl_reg &= ~(SBYB)                             #Set SBYB to 0 and go to Standby mode
		self._device.write8(CTRL_REG1, ctrl_reg)
		ctrl_reg = OS_128 	                    		#Set ALT bit to zero and enable back Active mode
		self._device.write8(CTRL_REG1, ctrl_reg)
		
		
	def AltimeterMode(self):
		"""
		Sets the mode in Altimeter mode.
		
		
		:param none: 
		:returns none:
		"""
		ctrl_reg = self._device.readU8(CTRL_REG1)	#Read current settings
		ctrl_reg &= ~(SBYB)											#Go to Standby mode
		self._device.write8(CTRL_REG1, ctrl_reg)
		ctrl_reg = ALT|OS_128										#Set ALT bit to one and enable back Active mode
		self._device.write8(CTRL_REG1, ctrl_reg)
		

	def ReadAltitude(self):
		"""
		Returns the number of meters above sea level.
		
		
		:param none: 
		:returns none: Returns altitude as a float
		"""
		m_altitude = self._device.readU8(OUT_P_MSB)			 #Read altitude data
		c_altitude = self._device.readU8(OUT_P_CSB)
		l_altitude = self._device.readU8(OUT_P_LSB)
		altitude = ((m_altitude << 24) | (c_altitude << 16) | (l_altitude))*10
		return( float(altitude/65536))
		
	def GetAltitude(self):
		"""
		Returns the number of meters above sea level.
		
		
		:param none: 
		:returns none: Returns altitude as a float
		"""
		alt = self.ReadAltitude()
		alt_m = alt >> 8 
		alt_l = alt & 0xff
		if (alt_l > 99):
			alt_l = alt_l / 1000.0
		else:
			alt_l = alt_l / 100.0
		return self.twosToInt(alt_m, 16) + alt_l

	def StandbyMode(self):
		"""
		Puts the sensor in standby mode. This is needed whenever one wants to modify the control registers.
		
		
		:param none: 
		:returns none: 
		"""
		ctrl_reg = self._device.readU8(CTRL_REG1)				#Read current settings
		ctrl_reg &= ~SBYB                              	#Clear SBYB bit for Standby mode
		self._device.write8(CTRL_REG1, ctrl_reg)				#Put device in Standby mode
		

	def ActiveMode(self):
		"""
		Put the sensor in active mode.
		
		
		:param none: 
		:returns none: 
		"""
		tempSetting = self._device.readU8(CTRL_REG1)			#Read current settings
		tempSetting |= SBYB                            #Set SBYB bit for Active mode
		self._device.write8(CTRL_REG1, tempSetting)

	def OversampleRate(self, sampleRate):
		"""
		Sets the ovsersampling rate.
		
		
		:param sampleRate: sampleRate is from 0 to 7
		:returns none: 
		"""
		

	def SetAcquisitionTimeStep(self,ST_Value):
		"""
		Set the acquisition time step.
		
		
		:param ST_Value:  Time Step value
		:returns none: 
		"""
		

	def EnableEventFlags(self):
		"""
		Enables the pressure and temp measurement event flags so that we can
		   test against them. This is recommended in datasheet during setup.
		   
		   
		:param none: 
		:returns none: 
		"""
		

	def ToggleOneShot(self):
		"""
		Clears then sets the OST bit which causes the sensor to immediately take another reading
	       Needed to sample faster than 1Hz.
		   
		   
		:param none: 
		:returns none: 
		"""
		tempSetting = self._device.readU8(CTRL_REG1) 			#Read current settings
		tempSetting &= ~(1<<1)                                   #Clear OST bit
		self._device.write8(CTRL_REG1, tempSetting)
		tempSetting = self._device.readU8(CTRL_REG1)              #Read current settings to be safe
		tempSetting |= (1<<1)                                    #Set OST bit
		self._device.write8(CTRL_REG1, tempSetting)

	def CofigureInterruptPin(self,interrupt,pin):
		"""
		Configure the interrupt pin.
		
		
		:param interrupt: Type of interrupt
		:param pin: Only pin 1 is used
		:returns none: 
		"""
		self._device.write8(CTRL_REG5,(pin << intrrpt))

	def TwosToInt(self, val, len):
		"""
		Convert twos complement to integer.
		
		
		:param val: 
		:param len:
		:returns complememt: integer value of two's complement 
		"""
		if(val & (1 << len - 1)):
			val = val - (1<<len)
			
