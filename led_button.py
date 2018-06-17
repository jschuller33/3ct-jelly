import RPi.GPIO as GPIO
import time
import os

import pigpio
pi = pigpio.pi()

# The Pins. Use Broadcom numbers.
RED_PIN   = 17
GREEN_PIN = 22
BLUE_PIN  = 24

LedPin = 11    # pin11 --- led
BtnPin = 37    # pin12 --- button

BtnStatus = 1

def setup():
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	#GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
	GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
	#GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to off led

def incrementBtnStatus():
	global BtnStatus
	if BtnStatus == 4:
		BtnStatus = 0
	else:
		BtnStatus = BtnStatus + 1

def swLed(ev=None):
	global BtnStatus
	if BtnStatus == 0:
		print 'State is 0: Off'
		os.system("pkill -f jelly.py")
		#set lights to all 0
	elif BtnStatus == 1:
		print 'State is 1: White'
		setLights(RED_PIN, 255)
		setLights(GREEN_PIN, 255)
		setLights(BLUE_PIN, 255)
		#set lights to white
	elif BtnStatus == 2:
		print 'State is 2: Purple'
		setLights(RED_PIN, 160)
		setLights(GREEN_PIN, 32)
		setLights(BLUE_PIN, 240)
		#set lights to purple
	elif BtnStatus == 3:
		print 'State is 3: Pattern'
		os.system("python jelly.py")
	incrementBtnStatus()
	#global Led_status
	#Led_status = not Led_status
	#GPIO.output(LedPin, Led_status)  # switch led status(on-->off; off-->on)
	#if Led_status == 1:
	#	print 'led off...'
	#else:
	#	print '...led on'

def setLights(pin, brightness):
	realBrightness = int(int(brightness) * (float(bright) / 255.0))
	pi.set_PWM_dutycycle(pin, realBrightness)

def loop():
	GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=swLed, bouncetime=200) # wait for falling and set bouncetime to prevent the callback function from being called multiple times when the button is pressed
	while True:
		time.sleep(1)   # Don't do anything

def destroy():
	#GPIO.output(LedPin, GPIO.HIGH)     # led off
	GPIO.cleanup()                     # Release resource

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()