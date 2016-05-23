import Ci20GPIO as GPIO
import time

def setup_pin():
	GPIO.setmode()						
	GPIO.setup(6, GPIO.IN)	# Setup GPIO 6 as an input.

def main():
	setup_pin()
	time.sleep(1)						# Sleep 1 second
	print " "
	while True:
		pin = GPIO.input(6)
		if (pin == 1):
			print "Button is pressed!"
		else:
			print "Not pressed"
		time.sleep(0.5)


#if __name__=='__main__':

main()
