#!/usr/bin/python

import serial

def main():
	ser = serial.Serial('/dev/ttyS0',115200,timeout=3)
	ser.write('Read data from terminal')

	while True:
		c = ser.read()
		print(c)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("")
