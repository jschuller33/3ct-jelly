#!/usr/bin/python
# -*- coding: utf-8 -*-

#
 # -----------------------------------------------------
 # File        jelly.py
 # Authors     3ct & Agia
 # License     GPLv3
 # Web         http://
 # -----------------------------------------------------
 # 
 # Copyright (C) 2014-2018 3ct & Agia
 # 
 # This program is free software: you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by
 # the Free Software Foundation, either version 3 of the License, or
 # any later version.
 #  
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 # 
 # You should have received a copy of the GNU General Public License
 # along with this program. If not, see <http://www.gnu.org/licenses/>
#


# This script needs running pigpio (http://abyz.co.uk/rpi/pigpio/)


###### CONFIGURE THIS ######

# The Pins. Use Broadcom numbers.
RED_PIN   = 17
GREEN_PIN = 22
BLUE_PIN  = 24
LIGHT_EFFECT_BTN_PIN = 37    # pin12 --- button
BRIGHTNESS_UP_BTN_PIN = 31
BRIGHTNESS_DOWN_BTN_PIN = 36

# Number of color changes per step (more is faster, less is slower).
# You also can use 0.X floats.
STEPS     = 0.3
IsPattern = False
###### END ######

import os
import sys
import termios
import tty
import pigpio
import time
import RPi.GPIO as GPIO
import subprocess
from thread import start_new_thread

bright = 255
r = 255.0
g = 0.0
b = 0.0

pi = pigpio.pi()

BtnStatus = 1
proc = True

def setup():
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	#GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is outexceptput
	GPIO.setup(LIGHT_EFFECT_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(BRIGHTNESS_UP_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(BRIGHTNESS_DOWN_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set LIGHT_EFFECT_BTN_PIN's mode is input, and pull up to high level(3.3V)
	#GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to off led

def incrementBtnStatus():
	global BtnStatus
	if BtnStatus == 4:
		BtnStatus = 0
	else:
		BtnStatus = BtnStatus + 1

def changeBrightness(brightnessUp):
    global bright
    print 'changing brightness...'
    if (bright < 2 and not brightnessUp) or (bright > 254 and brightnessUp):
        return
    
    global r
    global g
    global b
    
    if brightnessUp:
        bright += 50.8
    else:
        bright -= 50.8
        
    setLights(RED_PIN, r)
    setLights(GREEN_PIN, g)
    setLights(BLUE_PIN, b)
    print 'Brightness: ' + str(bright)

def changeLightEffect(ev=None):
	global BtnStatus
	global IsPattern
	global procFast
	global procSlow
	if BtnStatus == 0:
                procFast.kill()
                IsPattern = False
		print 'State is 0: Off'
		#set lights to black
		setLights(RED_PIN, 0)
		setLights(GREEN_PIN, 0)
		setLights(BLUE_PIN, 0)
	elif BtnStatus == 1:
		print 'State is 1: White'
		#set lights to white
		setLights(RED_PIN, 255)
		setLights(GREEN_PIN, 255)
		setLights(BLUE_PIN, 255)
	elif BtnStatus == 2:
		print 'State is 2: Purple'
		#set lights to purple
		setLights(RED_PIN, 160)
		setLights(GREEN_PIN, 32)
		setLights(BLUE_PIN, 240)
	elif BtnStatus == 3:
		print 'State is 3: Pattern Slow'
		#set lights to pattern
		IsPattern = True
		procSlow = subprocess.Popen(['python', 'fading-slow.py'])
        elif BtnStatus == 4:
		print 'State is 4: Pattern Fast'
		#set lights to pattern
		IsPattern = True
		procSlow.kill()
		procFast = subprocess.Popen(['python', 'fading-fast.py'])
	incrementBtnStatus()
	#global Led_status
	#Led_status = not Led_status
	#GPIO.output(LedPin, Led_status)  # switch led status(on-->off; off-->on)
	#if Led_status == 1:
	#	print 'led off...'
	#else:
	#	print '...led on'

def updateColor(color, step):
	color += step
	
	if color > 255:
		return 255
	if color < 0:
		return 0
		
	return color

def setLights(pin, brightness):
        global r
        global g
        global b
        if pin == RED_PIN:
            r = brightness
        elif pin == GREEN_PIN:
            g = brightness
        elif pin == BLUE_PIN:
            b = brightness
	realBrightness = int(int(brightness) * (float(bright) / 255.0))
	pi.set_PWM_dutycycle(pin, realBrightness)

def brightnessUp(self):
    changeBrightness(True)
    
def brightnessDown(self):
    changeBrightness(False)

def getCh():
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	
	try:
		tty.setraw(fd)
		ch = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		
	return ch

def checkKey():
	global bright
	global brightChanged
	global state
	global abort
	
	while True:
		c = getCh()
		
		if c == '+' and bright < 255 and not brightChanged:
			brightChanged = True
			time.sleep(0.01)
			brightChanged = False
			
			bright = bright + 1
			print ("Current brightness: %d" % bright)
			
		if c == '-' and bright > 0 and not brightChanged:
			brightChanged = True
			time.sleep(0.01)
			brightChanged = False
			
			bright = bright - 1
			print ("Current brightness: %d" % bright)
			
		if c == 'p' and state:
			state = False
			print ("Pausing...")
			
			time.sleep(0.1)
			
			setLights(RED_PIN, 0)
			setLights(GREEN_PIN, 0)
			setLights(BLUE_PIN, 0)
			
		if c == 'r' and not state:
			state = True
			print ("Resuming...")
			
		if c == 'c' and not abort:
			abort = True
			break

#start_new_thread(checkKey,  ())

#print ("+ / - = Increase / Decrease brightness")
#print ("p / r = Pause / Resume")
#print ("c = Abort Program")

def loop():
	GPIO.add_event_detect(LIGHT_EFFECT_BTN_PIN, GPIO.FALLING, callback=changeLightEffect, bouncetime=200) # wait for falling and set bouncetime to prevent the callback function from being called multiple times when the button is pressed
	GPIO.add_event_detect(BRIGHTNESS_UP_BTN_PIN, GPIO.FALLING, callback=brightnessUp, bouncetime=200) # wait for falling and set bouncetime to prevent the callback function from being called multiple times when the button is pressed
	GPIO.add_event_detect(BRIGHTNESS_DOWN_BTN_PIN, GPIO.FALLING, callback=brightnessDown, bouncetime=200) # wait for falling and set bouncetime to prevent the callback function from being called multiple times when the button is pressed
	while True:
		time.sleep(1)   # Don't do anything

def destroy():
	#GPIO.output(LedPin, GPIO.HIGH)     # led off
	GPIO.cleanup()                     # Release resource

def pattern():
    global IsPattern
    global LIGHT_EFFECT_BTN_PIN
    while True:
        global r
        global b
        global g
	if r == 255 and b == 0 and g < 255:
		g = updateColor(g, STEPS)
		setLights(GREEN_PIN, g)
	
	elif g == 255 and b == 0 and r > 0:
		r = updateColor(r, -STEPS)
		setLights(RED_PIN, r)
	
	elif r == 0 and g == 255 and b < 255:
		b = updateColor(b, STEPS)
		setLights(BLUE_PIN, b)
	
	elif r == 0 and b == 255 and g > 0:
		g = updateColor(g, -STEPS)
		setLights(GREEN_PIN, g)
	
	elif g == 0 and b == 255 and r < 255:
		r = updateColor(r, STEPS)
		setLights(RED_PIN, r)
	
	elif r == 255 and g == 0 and b > 0:
		b = updateColor(b, -STEPS)
		setLights(BLUE_PIN, b)

if __name__ == '__main__':     # Program start from here
	setup()
	setLights(BLUE_PIN, r)
        setLights(BLUE_PIN, g)
        setLights(BLUE_PIN, b)
	try:
		loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()
