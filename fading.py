#!/usr/bin/python
# -*- coding: utf-8 -*-

#
 # -----------------------------------------------------
 # File        fading.py
 # Authors     David Ordnung
 # License     GPLv3
 # Web         http://dordnung.de/raspberrypi-ledstrip/
 # -----------------------------------------------------
 # 
 # Copyright (C) 2014-2017 David Ordnung
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

# Number of color changes per step (more is faster, less is slower).
# You also can use 0.X floats.
STEPS     = 0.3

###### END ######




import os
import sys
import termios
import tty
import pigpio
import time
from thread import start_new_thread

bright = 255
r = 255.0
g = 0.0
b = 0.0

brightChanged = False
abort = False
state = True

pi = pigpio.pi()

def updateColor(color, step):
	color += step
	
	if color > 255:
		return 255
	if color < 0:
		return 0
		
	return color


def setLights(pin, brightness):
	realBrightness = int(int(brightness) * (float(bright) / 255.0))
	pi.set_PWM_dutycycle(pin, realBrightness)



setLights(RED_PIN, r)
setLights(GREEN_PIN, g)
setLights(BLUE_PIN, b)


while True:
	if state and not brightChanged:
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
