import Ci20GPIO as GPIO
import time

def setup_pin():
	GPIO.setmode()						
	GPIO.setup(21, GPIO.OUT)	# Setup GPIO 7 as an output.

def main():
	setup_pin()
	time.sleep(1)						# Sleep 1 second
	print " "
	while True:
		GPIO.output(21,GPIO.HIGH)
		time.sleep(1)
		GPIO.output(21,GPIO.LOW)
		time.sleep(1)


#if __name__=='__main__':

main()